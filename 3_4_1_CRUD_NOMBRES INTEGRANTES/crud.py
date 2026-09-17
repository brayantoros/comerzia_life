import mysql.connector
from conexion import connect
from report import generate_pdf_report, generate_inventory_report, export_products_csv


def get_product_by_id(prod_id):
    """Consulta y retorna un unico producto por su ID (o None si no existe)."""
    connection = None
    cursor = None
    try:
        connection = connect()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, descripcion, precio, stock, activo FROM productos WHERE id = %s", (prod_id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"[ERROR BD al consultar producto]: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def create_product(nombre, descripcion, precio, stock, activo=1):
    """
    Inserta un nuevo producto en el catalogo de Comerzia con validaciones basicas.
    Retorna el ID del producto creado o False si hay error.
    """
    # Validaciones basicas
    if not nombre or not str(nombre).strip():
        print("[VALIDACION] El nombre del producto no puede estar vacio.")
        return False

    try:
        precio_float = float(precio)
        if precio_float <= 0:
            print("[VALIDACION] El precio debe ser un numero positivo mayor a 0.")
            return False
    except (ValueError, TypeError):
        print("[VALIDACION] El precio debe ser un numero valido.")
        return False

    try:
        stock_int = int(stock)
        if stock_int < 0:
            print("[VALIDACION] El stock no puede ser negativo.")
            return False
    except (ValueError, TypeError):
        print("[VALIDACION] El stock debe ser un numero entero valido.")
        return False

    connection = None
    cursor = None
    try:
        connection = connect()
        cursor = connection.cursor()
        query = "INSERT INTO productos (nombre, descripcion, precio, stock, activo) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (nombre.strip(), descripcion.strip() if descripcion else "", precio_float, stock_int, activo))
        connection.commit()
        nuevo_id = cursor.lastrowid
        print(f"[EXITO] Producto registrado con exito con ID: {nuevo_id}")
        return nuevo_id
    except mysql.connector.Error as err:
        print(f"[ERROR BD al registrar producto]: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def read_products():
    """Consulta y muestra en consola la lista completa de productos de Comerzia."""
    connection = None
    cursor = None
    try:
        connection = connect()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, descripcion, precio, stock, activo FROM productos ORDER BY id ASC")
        productos = cursor.fetchall()

        if not productos:
            print("\n[INFORMACION] No hay productos registrados en la base de datos de Comerzia.")
            return []

        print("\n" + "=" * 80)
        print(f"{'ID':<5} | {'PRODUCTO':<30} | {'PRECIO':<12} | {'STOCK':<8} | {'ESTADO':<10}")
        print("=" * 80)
        for p in productos:
            estado = "Activo" if p['activo'] == 1 else "Inactivo"
            if p['stock'] == 0:
                estado = "Agotado"
            nombre = str(p['nombre'])[:28]
            precio = f"${float(p['precio']):,.2f}"
            print(f"{p['id']:<5} | {nombre:<30} | {precio:<12} | {p['stock']:<8} | {estado:<10}")
        print("=" * 80)
        print(f"Total productos en catalogo: {len(productos)}\n")
        return productos
    except mysql.connector.Error as err:
        print(f"[ERROR BD al leer productos]: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def update_product(prod_id, nombre=None, descripcion=None, precio=None, stock=None, activo=None):
    """
    Actualiza la informacion de un producto existente en Comerzia.
    """
    producto = get_product_by_id(prod_id)
    if not producto:
        print(f"[ERROR] No existe ningun producto con el ID {prod_id}.")
        return False

    # Tomar valores nuevos o conservar los actuales
    nuevo_nombre = str(nombre).strip() if nombre is not None and str(nombre).strip() else producto['nombre']
    nueva_desc = str(descripcion).strip() if descripcion is not None else producto['descripcion']
    
    if precio is not None and str(precio).strip() != "":
        try:
            nuevo_precio = float(precio)
            if nuevo_precio <= 0:
                print("[VALIDACION] El precio debe ser mayor a 0.")
                return False
        except ValueError:
            print("[VALIDACION] El precio no es valido.")
            return False
    else:
        nuevo_precio = float(producto['precio'])

    if stock is not None and str(stock).strip() != "":
        try:
            nuevo_stock = int(stock)
            if nuevo_stock < 0:
                print("[VALIDACION] El stock no puede ser negativo.")
                return False
        except ValueError:
            print("[VALIDACION] El stock no es valido.")
            return False
    else:
        nuevo_stock = int(producto['stock'])

    nuevo_activo = int(activo) if activo is not None and str(activo).strip() != "" else producto['activo']

    connection = None
    cursor = None
    try:
        connection = connect()
        cursor = connection.cursor()
        query = "UPDATE productos SET nombre = %s, descripcion = %s, precio = %s, stock = %s, activo = %s WHERE id = %s"
        cursor.execute(query, (nuevo_nombre, nueva_desc, nuevo_precio, nuevo_stock, nuevo_activo, prod_id))
        connection.commit()
        print(f"[EXITO] Producto con ID {prod_id} actualizado con exito.")
        return True
    except mysql.connector.Error as err:
        print(f"[ERROR BD al actualizar producto]: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def delete_product(prod_id):
    """Elimina un producto por su ID tras verificar su existencia."""
    try:
        pid = int(prod_id)
    except (ValueError, TypeError):
        print("[VALIDACION] El ID debe ser un numero entero valido.")
        return False

    if not get_product_by_id(pid):
        print(f"[ERROR] No se encontro ningun producto con el ID {pid} para eliminar.")
        return False

    connection = None
    cursor = None
    try:
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM productos WHERE id = %s", (pid,))
        connection.commit()
        print(f"[EXITO] Producto con ID {pid} eliminado con exito.")
        return True
    except mysql.connector.Error as err:
        print(f"[ERROR BD al eliminar producto]: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def main_menu():
    """Menu interactivo por consola para gestionar los productos de Comerzia."""
    while True:
        print("\n" + "=" * 54)
        print("    GESTION DE PRODUCTOS & REPORTES - COMERZIA")
        print("=" * 54)
        print("  1. Registrar nuevo producto")
        print("  2. Consultar listado de productos")
        print("  3. Actualizar informacion de producto")
        print("  4. Eliminar producto")
        print("  5. Generar Reporte 1: PDF General de Catalogo")
        print("  6. Generar Reporte 2: PDF de Inventario y Stock")
        print("  7. Exportar Reporte a CSV (Excel)")
        print("  8. Salir")
        print("=" * 54)

        choice = input("Seleccione una opcion (1-8): ").strip()

        if choice == "1":
            print("\n--- REGISTRAR NUEVO PRODUCTO ---")
            nombre = input("Nombre del producto: ").strip()
            desc = input("Descripcion: ").strip()
            precio = input("Precio: ").strip()
            stock = input("Stock inicial: ").strip()
            create_product(nombre, desc, precio, stock)

        elif choice == "2":
            print("\n--- CATALOGO DE PRODUCTOS ---")
            read_products()

        elif choice == "3":
            print("\n--- ACTUALIZAR PRODUCTO ---")
            pid = input("ID del producto a modificar: ").strip()
            nombre = input("Nuevo nombre (enter para conservar): ").strip()
            desc = input("Nueva descripcion (enter para conservar): ").strip()
            precio = input("Nuevo precio (enter para conservar): ").strip()
            stock = input("Nuevo stock (enter para conservar): ").strip()
            update_product(pid, nombre or None, desc or None, precio or None, stock or None)

        elif choice == "4":
            print("\n--- ELIMINAR PRODUCTO ---")
            pid = input("ID del producto a eliminar: ").strip()
            confirm = input(f"Seguro de eliminar el ID {pid}? (s/n): ").strip().lower()
            if confirm in ('s', 'si', 'y', 'yes'):
                delete_product(pid)
            else:
                print("Operacion cancelada.")

        elif choice == "5":
            print("\n--- GENERANDO REPORTE 1: PDF GENERAL ---")
            generate_pdf_report()

        elif choice == "6":
            print("\n--- GENERANDO REPORTE 2: PDF DE INVENTARIO ---")
            generate_inventory_report()

        elif choice == "7":
            print("\n--- EXPORTANDO REPORTE A CSV PARA EXCEL ---")
            export_products_csv()

        elif choice == "8":
            print("\nSaliendo del sistema de gestion... Hasta pronto.")
            break
        else:
            print("\n[AVISO] Opcion invalida. Por favor seleccione del 1 al 8.")


if __name__ == "__main__":
    main_menu()
