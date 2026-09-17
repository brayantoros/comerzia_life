import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import DB_CONFIG, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, SECRET_KEY
from flask import make_response

# Recuerda instalar esta librería para poder generar PDFs.
# Puedes hacerlo abriendo tu terminal y ejecutando: pip install fpdf
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegura carpeta de imágenes
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_cart_count():
    cart_count = 0
    if session.get('user_id'):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id FROM carrito WHERE usuario_id = %s", (session['user_id'],))
            carrito = cursor.fetchone()
            if carrito:
                cursor.execute("SELECT SUM(cantidad) as total FROM carrito_productos WHERE carrito_id = %s", (carrito['id'],))
                result = cursor.fetchone()
                if result and result['total']:
                    cart_count = int(result['total'])
        except Exception:
            pass
        finally:
            cursor.close()
            db.close()
    return dict(cart_count=cart_count)

# ----------------- Rutas públicas -----------------
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/tienda')
def tienda():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, descripcion, precio, imagen, stock FROM productos WHERE activo = 1")
    productos = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('index.html', productos=productos)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        apellido = request.form['apellido'].strip()
        correo = request.form['correo'].strip()
        rol = 'cliente'
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password or not nombre or not apellido or not correo:
            flash('Completa todos los campos', 'warning')
            return redirect(url_for('register'))
        hashed = generate_password_hash(password)
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (username, password, rol, nombre, apellido, correo) VALUES (%s,%s,%s,%s,%s,%s)", (username, hashed, rol, nombre, apellido, correo))
            db.commit()
            user_id = cursor.lastrowid
            session['user_id'] = user_id
            session['username'] = username
            session['rol'] = rol
            flash('Registro exitoso. Bienvenido ' + username, 'success')
            if rol == 'admin':
                return redirect(url_for('admin_products'))
            return redirect(url_for('tienda'))
        except mysql.connector.IntegrityError:
            flash('El usuario ya existe', 'danger')
            return redirect(url_for('register'))
        finally:
            cursor.close()
            db.close()
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password, rol FROM usuarios WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['rol'] = user['rol']
            flash('Bienvenido ' + user['username'], 'success')
            if user['rol'] == 'admin':
                return redirect(url_for('admin_products'))
            return redirect(url_for('tienda'))
        flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('landing'))

# ----------------- Rutas del Carrito y Compra -----------------
@app.route('/cart')
def cart():
    if not session.get('user_id'):
        flash('Inicia sesión para ver tu carrito', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Obtener el carrito del usuario. Si no existe, crearlo.
    cursor.execute("SELECT id FROM carrito WHERE usuario_id = %s", (user_id,))
    carrito = cursor.fetchone()
    
    if not carrito:
        cursor.execute("INSERT INTO carrito (usuario_id) VALUES (%s)", (user_id,))
        db.commit()
        carrito_id = cursor.lastrowid
    else:
        carrito_id = carrito['id']
        
    # Obtener los productos en el carrito
    query = """
        SELECT cp.producto_id, cp.cantidad, p.nombre, p.precio, p.imagen, p.stock 
        FROM carrito_productos cp
        JOIN productos p ON cp.producto_id = p.id
        WHERE cp.carrito_id = %s
    """
    cursor.execute(query, (carrito_id,))
    items = cursor.fetchall()
    
    # Calcular subtotales y total
    total = 0.0
    for item in items:
        item['precio'] = float(item['precio'])
        item['subtotal'] = item['precio'] * item['cantidad']
        total += item['subtotal']
        
    cursor.close()
    db.close()
    
    return render_template('cart.html', items=items, total=total)

@app.route('/cart/add/<int:prod_id>', methods=['POST'])
def add_to_cart(prod_id):
    if not session.get('user_id'):
        flash('Inicia sesión para agregar productos al carrito', 'warning')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    try:
        cantidad_a_agregar = int(request.form.get('cantidad', 1))
    except ValueError:
        cantidad_a_agregar = 1
        
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # 1. Verificar stock disponible del producto
    cursor.execute("SELECT nombre, precio, stock, activo FROM productos WHERE id = %s", (prod_id,))
    product = cursor.fetchone()
    
    if not product or product['activo'] == 0:
        flash('El producto no está disponible', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('tienda'))
        
    stock_disponible = product['stock']
    
    if stock_disponible < 1:
        flash('Este producto se encuentra agotado', 'warning')
        cursor.close()
        db.close()
        return redirect(url_for('tienda'))
        
    # 2. Obtener o crear el carrito activo
    cursor.execute("SELECT id FROM carrito WHERE usuario_id = %s", (user_id,))
    carrito = cursor.fetchone()
    if not carrito:
        cursor.execute("INSERT INTO carrito (usuario_id) VALUES (%s)", (user_id,))
        db.commit()
        carrito_id = cursor.lastrowid
    else:
        carrito_id = carrito['id']
        
    # 3. Verificar si el producto ya está en el carrito
    cursor.execute("SELECT cantidad FROM carrito_productos WHERE carrito_id = %s AND producto_id = %s", (carrito_id, prod_id))
    cart_item = cursor.fetchone()
    
    if cart_item:
        nueva_cantidad = cart_item['cantidad'] + cantidad_a_agregar
        if nueva_cantidad > stock_disponible:
            flash(f"No puedes agregar {cantidad_a_agregar} unidades más. Solo hay {stock_disponible} en stock y ya tienes {cart_item['cantidad']} en tu carrito.", 'warning')
        else:
            cursor.execute("UPDATE carrito_productos SET cantidad = %s WHERE carrito_id = %s AND producto_id = %s", (nueva_cantidad, carrito_id, prod_id))
            db.commit()
            flash(f"Se aumentó la cantidad de {product['nombre']} en el carrito.", 'success')
    else:
        if cantidad_a_agregar > stock_disponible:
            flash(f"Solo hay {stock_disponible} unidades disponibles de {product['nombre']}.", 'warning')
        else:
            cursor.execute("INSERT INTO carrito_productos (carrito_id, producto_id, cantidad) VALUES (%s, %s, %s)", (carrito_id, prod_id, cantidad_a_agregar))
            db.commit()
            flash(f"{product['nombre']} agregado al carrito.", 'success')
            
    cursor.close()
    db.close()
    return redirect(url_for('tienda'))

@app.route('/cart/update/<int:prod_id>', methods=['POST'])
def update_cart(prod_id):
    if not session.get('user_id'):
        flash('Inicia sesión para modificar tu carrito', 'warning')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    try:
        nueva_cantidad = int(request.form.get('cantidad', 1))
    except ValueError:
        nueva_cantidad = 1
        
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Validar stock actual
    cursor.execute("SELECT nombre, stock, activo FROM productos WHERE id = %s", (prod_id,))
    product = cursor.fetchone()
    
    if not product or product['activo'] == 0:
        flash('El producto no está disponible', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('cart'))
        
    stock_disponible = product['stock']
    
    cursor.execute("SELECT id FROM carrito WHERE usuario_id = %s", (user_id,))
    carrito = cursor.fetchone()
    
    if carrito:
        carrito_id = carrito['id']
        
        if stock_disponible < 1:
            # Si ya no hay stock, lo quitamos del carrito automáticamente
            cursor.execute("DELETE FROM carrito_productos WHERE carrito_id = %s AND producto_id = %s", (carrito_id, prod_id))
            db.commit()
            flash(f"El producto '{product['nombre']}' se ha agotado y fue eliminado de tu carrito.", 'warning')
        elif nueva_cantidad > stock_disponible:
            # Si intenta poner más cantidad que el stock
            cursor.execute("UPDATE carrito_productos SET cantidad = %s WHERE carrito_id = %s AND producto_id = %s", (stock_disponible, carrito_id, prod_id))
            db.commit()
            flash(f"Stock insuficiente. Se ajustó la cantidad de '{product['nombre']}' al máximo disponible ({stock_disponible}).", 'warning')
        elif nueva_cantidad <= 0:
            cursor.execute("DELETE FROM carrito_productos WHERE carrito_id = %s AND producto_id = %s", (carrito_id, prod_id))
            db.commit()
            flash('Producto eliminado del carrito', 'info')
        else:
            cursor.execute("UPDATE carrito_productos SET cantidad = %s WHERE carrito_id = %s AND producto_id = %s", (nueva_cantidad, carrito_id, prod_id))
            db.commit()
            flash('Cantidad actualizada', 'success')
            
    cursor.close()
    db.close()
    return redirect(url_for('cart'))

@app.route('/cart/remove/<int:prod_id>', methods=['POST'])
def remove_from_cart(prod_id):
    if not session.get('user_id'):
        flash('Inicia sesión para realizar esta acción', 'warning')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Obtener el carrito
    cursor.execute("SELECT id FROM carrito WHERE usuario_id = %s", (user_id,))
    carrito = cursor.fetchone()
    
    if carrito:
        carrito_id = carrito['id']
        cursor.execute("DELETE FROM carrito_productos WHERE carrito_id = %s AND producto_id = %s", (carrito_id, prod_id))
        db.commit()
        flash('Producto eliminado del carrito', 'info')
        
    cursor.close()
    db.close()
    return redirect(url_for('cart'))

@app.route('/cart/checkout', methods=['POST'])
def checkout():
    if not session.get('user_id'):
        flash('Inicia sesión para realizar la compra', 'warning')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    try:
        # 1. Iniciar la transacción explícita
        db.start_transaction()
        
        # 2. Obtener el carrito
        cursor.execute("SELECT id FROM carrito WHERE usuario_id = %s", (user_id,))
        carrito = cursor.fetchone()
        
        if not carrito:
            flash('No tienes un carrito activo', 'warning')
            db.rollback()
            cursor.close()
            db.close()
            return redirect(url_for('tienda'))
            
        carrito_id = carrito['id']
        
        # 3. Obtener los productos y cantidades en el carrito junto con el stock y precio actual
        query = """
            SELECT cp.producto_id, cp.cantidad, p.nombre, p.precio, p.stock, p.activo
            FROM carrito_productos cp
            JOIN productos p ON cp.producto_id = p.id
            WHERE cp.carrito_id = %s
        """
        cursor.execute(query, (carrito_id,))
        cart_items = cursor.fetchall()
        
        if not cart_items:
            flash('Tu carrito está vacío', 'warning')
            db.rollback()
            cursor.close()
            db.close()
            return redirect(url_for('cart'))
            
        # 4. Validar stock e inactividad, y calcular el total de la compra
        total_pedido = 0.0
        for item in cart_items:
            if item['activo'] == 0:
                flash(f"El producto '{item['nombre']}' ya no está activo para venta. Por favor, elimínalo del carrito.", 'danger')
                db.rollback()
                cursor.close()
                db.close()
                return redirect(url_for('cart'))
                
            if item['cantidad'] > item['stock']:
                flash(f"Stock insuficiente para '{item['nombre']}'. Disponible: {item['stock']}.", 'danger')
                db.rollback()
                cursor.close()
                db.close()
                return redirect(url_for('cart'))
                
            item['precio'] = float(item['precio'])
            total_pedido += item['precio'] * item['cantidad']
            
        # 5. Crear la cabecera del pedido (Factura)
        cursor.execute("INSERT INTO pedidos (usuario_id, total) VALUES (%s, %s)", (user_id, total_pedido))
        pedido_id = cursor.lastrowid
        
        # 6. Mover el detalle del carrito a 'pedidos_productos', congelar precios y actualizar stock
        for item in cart_items:
            # Insertar en pedidos_productos congelando el precio actual
            cursor.execute(
                "INSERT INTO pedidos_productos (pedido_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
                (pedido_id, item['producto_id'], item['cantidad'], item['precio'])
            )
            # Descontar del stock de productos
            cursor.execute(
                "UPDATE productos SET stock = stock - %s WHERE id = %s",
                (item['cantidad'], item['producto_id'])
            )
            
        # 7. Vaciar el carrito de forma segura
        cursor.execute("DELETE FROM carrito_productos WHERE carrito_id = %s", (carrito_id,))
        
        # 8. Confirmar la transacción
        db.commit()
        flash(f"¡Compra realizada con éxito! N° de pedido: #{pedido_id}. Total: ${total_pedido:.2f}", 'success')
        exito = True
        
    except mysql.connector.Error as e:
        # En caso de cualquier error en la base de datos, revertimos todo
        db.rollback()
        flash(f"Error en el proceso de compra: {e}", 'danger')
        exito = False
    finally:
        cursor.close()
        db.close()
        
    if exito:
        return redirect(url_for('receipt', pedido_id=pedido_id))
    return redirect(url_for('tienda'))

# ----------------- Rutas del Recibo y PDF -----------------
@app.route('/pedido/<int:pedido_id>')
def receipt(pedido_id):
    if not session.get('user_id'):
        flash('Inicia sesión para ver tu recibo', 'warning')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Obtener el pedido
    cursor.execute("SELECT id, total FROM pedidos WHERE id = %s AND usuario_id = %s", (pedido_id, user_id))
    pedido = cursor.fetchone()
    
    if not pedido:
        flash('Pedido no encontrado', 'danger')
        cursor.close()
        db.close()
        return redirect(url_for('tienda'))
        
    # Obtener los productos del pedido
    query = """
        SELECT pp.cantidad, pp.precio_unitario, p.nombre 
        FROM pedidos_productos pp
        JOIN productos p ON pp.producto_id = p.id
        WHERE pp.pedido_id = %s
    """
    cursor.execute(query, (pedido_id,))
    productos = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return render_template('receipt.html', pedido=pedido, productos=productos)

@app.route('/pedido/<int:pedido_id>/pdf')
def receipt_pdf(pedido_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT id, total FROM pedidos WHERE id = %s AND usuario_id = %s", (pedido_id, user_id))
    pedido = cursor.fetchone()
    
    if not pedido:
        cursor.close()
        db.close()
        return redirect(url_for('tienda'))
        
    cursor.execute("""
        SELECT pp.cantidad, pp.precio_unitario, p.nombre 
        FROM pedidos_productos pp
        JOIN productos p ON pp.producto_id = p.id
        WHERE pp.pedido_id = %s
    """, (pedido_id,))
    productos = cursor.fetchall()
    
    cursor.close()
    db.close()

    # Generamos el PDF usando fpdf
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, txt=f"Recibo de Compra - Pedido #{pedido['id']}", ln=True, align='C')
    pdf.ln(10)
    
    # Total
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, txt=f"Total pagado: ${pedido['total']}", ln=True)
    pdf.ln(5)
    
    # Cabecera de la tabla
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(90, 10, txt="Producto", border=1)
    pdf.cell(40, 10, txt="Cantidad", border=1, align='C')
    pdf.cell(40, 10, txt="Precio Unit.", border=1, align='C')
    pdf.ln()
    
    # Filas de la tabla
    pdf.set_font("Arial", size=12)
    for prod in productos:
        # Convertimos el nombre a string por si acaso, usando una codificación segura para fpdf
        nombre = str(prod['nombre']).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(90, 10, txt=nombre, border=1)
        pdf.cell(40, 10, txt=str(prod['cantidad']), border=1, align='C')
        pdf.cell(40, 10, txt=f"${prod['precio_unitario']}", border=1, align='C')
        pdf.ln()

    # Preparamos el PDF para descargar
    pdf_content = pdf.output(dest='S').encode('latin-1')
    response = make_response(pdf_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=recibo_pedido_{pedido["id"]}.pdf'
    return response

# ----------------- Rutas admin (protege con rol) -----------------
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('rol') != 'admin':
            flash('Acceso denegado', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/admin/products')
@admin_required
def admin_products():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('admin_products.html', productos=productos)

@app.route('/admin/products/update_stock/<int:prod_id>', methods=['POST'])
@admin_required
def update_stock(prod_id):
    # Obtenemos el nuevo stock del formulario
    nuevo_stock = request.form.get('stock', 0)
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE productos SET stock = %s WHERE id = %s", (nuevo_stock, prod_id))
    db.commit()
    cursor.close()
    db.close()
    
    flash('Stock actualizado correctamente', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/reporte_pdf')
@admin_required
def admin_reporte_pdf():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # Obtenemos los productos para el reporte
    cursor.execute("SELECT id, nombre, stock, precio FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    db.close()

    # Generamos el PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Título del reporte
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, txt="Reporte General de Inventario", ln=True, align='C')
    pdf.ln(10)

    # Cabecera de la tabla
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(20, 10, txt="ID", border=1, align='C')
    pdf.cell(90, 10, txt="Nombre", border=1)
    pdf.cell(30, 10, txt="Stock", border=1, align='C')
    pdf.cell(40, 10, txt="Precio", border=1, align='C')
    pdf.ln()

    # Contenido de la tabla
    pdf.set_font("Arial", size=12)
    for p in productos:
        nombre = str(p['nombre']).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(20, 10, txt=str(p['id']), border=1, align='C')
        pdf.cell(90, 10, txt=nombre, border=1)
        pdf.cell(30, 10, txt=str(p['stock']), border=1, align='C')
        pdf.cell(40, 10, txt=f"${p['precio']}", border=1, align='C')
        pdf.ln()

    # Preparamos la respuesta para que se descargue
    pdf_content = pdf.output(dest='S').encode('latin-1')
    response = make_response(pdf_content)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=reporte_inventario.pdf'
    return response

@app.route('/admin/products/new', methods=['GET','POST'])
@admin_required
def new_product():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion','')
        precio = request.form['precio'] or 0
        activo = 1 if request.form.get('activo') == 'on' else 0
        imagen_filename = None
        file = request.files.get('imagen')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagen_filename = filename
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO productos (nombre, descripcion, precio, imagen, activo) VALUES (%s,%s,%s,%s,%s)",
                       (nombre, descripcion, precio, imagen_filename, activo))
        db.commit()
        cursor.close()
        db.close()
        flash('Producto agregado', 'success')
        return redirect(url_for('admin_products'))
    return render_template('product_form.html', action='Crear', producto=None)

@app.route('/admin/products/edit/<int:prod_id>', methods=['GET','POST'])
@admin_required
def edit_product(prod_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion','')
        precio = request.form['precio'] or 0
        activo = 1 if request.form.get('activo') == 'on' else 0
        file = request.files.get('imagen')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cursor.execute("UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, imagen=%s, activo=%s WHERE id=%s",
                           (nombre, descripcion, precio, filename, activo, prod_id))
        else:
            cursor.execute("UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, activo=%s WHERE id=%s",
                           (nombre, descripcion, precio, activo, prod_id))
        db.commit()
        cursor.close()
        db.close()
        flash('Producto actualizado', 'success')
        return redirect(url_for('admin_products'))
    cursor.execute("SELECT * FROM productos WHERE id = %s", (prod_id,))
    producto = cursor.fetchone()
    cursor.close()
    db.close()
    if not producto:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('admin_products'))
    return render_template('product_form.html', action='Editar', producto=producto)

@app.route('/admin/products/delete/<int:prod_id>', methods=['POST'])
@admin_required
def delete_product(prod_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM productos WHERE id = %s", (prod_id,))
        db.commit()
        flash('Producto eliminado', 'info')
    except mysql.connector.Error as e:
        db.rollback()
        if e.errno == 1451:
            flash('No se puede eliminar este producto porque está asociado a un historial de pedidos. Si ya no deseas venderlo, desactívalo.', 'danger')
        else:
            flash(f'Error al intentar eliminar el producto: {e}', 'danger')
    finally:
        cursor.close()
        db.close()
    return redirect(url_for('admin_products'))

@app.route('/admin/products/toggle/<int:prod_id>', methods=['POST'])
@admin_required
def toggle_product(prod_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT activo FROM productos WHERE id = %s", (prod_id,))
    row = cursor.fetchone()
    if row:
        nuevo = 0 if row[0] == 1 else 1
        cursor.execute("UPDATE productos SET activo = %s WHERE id = %s", (nuevo, prod_id))
        db.commit()
    cursor.close()
    db.close()
    return redirect(url_for('admin_products'))

# Ruta para servir imágenes (opcional)
@app.route('/static/img/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
