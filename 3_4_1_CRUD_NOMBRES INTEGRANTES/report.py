import os
import csv
import warnings
from datetime import datetime
from fpdf import FPDF
from conexion import connect

# Silenciamos avisos de deprecacion para mantener la consola limpia
warnings.simplefilter('ignore')

# Rutas del modulo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "Reportes")
IMG_DIR = os.path.join(BASE_DIR, "img")
HEADER_IMG = os.path.join(IMG_DIR, "header.jpg")
FOOTER_IMG = os.path.join(IMG_DIR, "footer.jpg")

os.makedirs(REPORTS_DIR, exist_ok=True)


class CustomPDF(FPDF):
    """Clase de FPDF con membrete institucional de Comerzia."""

    def __init__(self, report_title="Reporte Comerzia", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report_title = report_title

    def header(self):
        # 1. Imagen institucional si existe
        if os.path.exists(HEADER_IMG):
            try:
                self.image(HEADER_IMG, x=10, y=8, w=45)
            except Exception:
                pass

        # 2. Titulo del reporte alineado a la derecha
        self.set_font("Helvetica", "B", 13)
        self.set_xy(60, 10)
        self.cell(140, 8, self.report_title, align="R")
        self.ln(18)

    def footer(self):
        self.set_y(-18)
        self.set_font("Helvetica", "I", 8)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

        fecha_gen = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.cell(100, 6, f"Proyecto Comerzia | Generado el: {fecha_gen}", align="L")
        self.cell(90, 6, f"Pagina {self.page_no()}", align="R")


def generate_pdf_report(filename="Reporte_Productos.pdf"):
    """
    REPORTE 1: Catalogo General de Productos en Formato PDF.
    Lee los datos reales de la base de datos de Comerzia (tienda_db).
    """
    output_path = os.path.join(REPORTS_DIR, filename)
    connection = None
    cursor = None

    try:
        connection = connect()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, descripcion, precio, stock, activo FROM productos ORDER BY id ASC")
        productos = cursor.fetchall()

        pdf = CustomPDF(report_title="Reporte General de Productos")
        pdf.add_page()

        # Titulo y subtitulo
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, "CATALOGO OFICIAL DE PRODUCTOS - COMERZIA", align="L")
        pdf.ln(8)

        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 5, f"Total de productos en base de datos: {len(productos)} | Base de Datos: tienda_db", align="L")
        pdf.ln(8)

        # Encabezado de la tabla
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(220, 230, 245)

        pdf.cell(15, 8, "ID", border=1, align="C", fill=True)
        pdf.cell(75, 8, "Nombre del Producto", border=1, align="L", fill=True)
        pdf.cell(35, 8, "Precio Unit.", border=1, align="R", fill=True)
        pdf.cell(25, 8, "Stock", border=1, align="C", fill=True)
        pdf.cell(35, 8, "Estado", border=1, align="C", fill=True)
        pdf.ln(8)

        # Filas con los productos de Comerzia
        pdf.set_font("Helvetica", "", 9)
        total_stock = 0
        valor_total = 0.0

        for prod in productos:
            prod_id = str(prod['id'])
            nombre = str(prod['nombre'])[:38]
            precio = float(prod['precio'])
            stock = int(prod['stock']) if prod['stock'] is not None else 0
            activo = prod['activo']

            estado = "Activo" if activo == 1 else "Inactivo"
            if stock == 0:
                estado = "Agotado"

            pdf.cell(15, 7, prod_id, border=1, align="C")
            pdf.cell(75, 7, nombre, border=1, align="L")
            pdf.cell(35, 7, f"${precio:,.2f}", border=1, align="R")
            pdf.cell(25, 7, str(stock), border=1, align="C")
            pdf.cell(35, 7, estado, border=1, align="C")
            pdf.ln(7)

            total_stock += stock
            valor_total += (precio * stock)

        # Resumen al pie
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"Total de productos listados: {len(productos)}")
        pdf.ln(6)
        pdf.cell(0, 6, f"Total de unidades en inventario: {total_stock}")
        pdf.ln(6)
        pdf.cell(0, 6, f"Valor total estimado del catalogo: ${valor_total:,.2f}")
        pdf.ln(6)

        pdf.output(output_path)
        print(f"[EXITO] Reporte PDF generado en: {output_path}")
        return output_path
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def generate_inventory_report(filename="Reporte_Inventario.pdf"):
    """
    REPORTE 2: Reporte de Inventario y Stock en Formato PDF.
    Muestra los productos disponibles vs agotados y estadisticas de stock.
    """
    output_path = os.path.join(REPORTS_DIR, filename)
    connection = None
    cursor = None

    try:
        connection = connect()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, precio, stock, activo FROM productos ORDER BY stock ASC")
        productos = cursor.fetchall()

        pdf = CustomPDF(report_title="Reporte de Inventario y Stock")
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, "CONTROL DE INVENTARIO Y STOCK - COMERZIA", align="L")
        pdf.ln(8)

        agotados = [p for p in productos if (p['stock'] is None or p['stock'] == 0)]
        disponibles = [p for p in productos if p['stock'] is not None and p['stock'] > 0]

        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Productos disponibles con stock: {len(disponibles)} | Productos agotados: {len(agotados)}")
        pdf.ln(8)

        # Encabezados
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(20, 8, "ID", border=1, align="C", fill=True)
        pdf.cell(85, 8, "Producto", border=1, align="L", fill=True)
        pdf.cell(40, 8, "Stock en Bodega", border=1, align="C", fill=True)
        pdf.cell(40, 8, "Situacion", border=1, align="C", fill=True)
        pdf.ln(8)

        pdf.set_font("Helvetica", "", 9)
        for prod in productos:
            stock = int(prod['stock']) if prod['stock'] is not None else 0
            situacion = "Disponible" if stock > 0 else "Agotado / Reponer"

            pdf.cell(20, 7, str(prod['id']), border=1, align="C")
            pdf.cell(85, 7, str(prod['nombre'])[:40], border=1, align="L")
            pdf.cell(40, 7, str(stock), border=1, align="C")
            pdf.cell(40, 7, situacion, border=1, align="C")
            pdf.ln(7)

        pdf.output(output_path)
        print(f"[EXITO] Reporte de Inventario generado en: {output_path}")
        return output_path
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def export_products_csv(filename="Reporte_Productos.csv"):
    """
    REPORTE ADICIONAL: Exportacion tabular compatible con Microsoft Excel en formato CSV.
    """
    output_path = os.path.join(REPORTS_DIR, filename)
    connection = None
    cursor = None

    try:
        connection = connect()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, descripcion, precio, stock, activo FROM productos ORDER BY id ASC")
        productos = cursor.fetchall()

        with open(output_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")

            writer.writerow(["REPORTE DE PRODUCTOS E INVENTARIO - COMERZIA"])
            writer.writerow(["Generado el:", datetime.now().strftime("%d/%m/%Y %H:%M:%S")])
            writer.writerow([])

            writer.writerow(["ID", "Producto", "Descripcion", "Precio Unitario ($)", "Stock", "Estado", "Subtotal ($)"])

            total_stock = 0
            valor_total = 0.0

            for prod in productos:
                prod_id = prod['id']
                nombre = prod['nombre']
                desc = prod.get('descripcion') or ""
                precio = float(prod['precio'])
                stock = int(prod['stock']) if prod['stock'] is not None else 0
                activo = prod['activo']

                estado = "Activo" if activo == 1 else "Inactivo"
                if stock == 0:
                    estado = "Agotado"

                subtotal = precio * stock
                total_stock += stock
                valor_total += subtotal

                writer.writerow([prod_id, nombre, desc, f"{precio:.2f}", stock, estado, f"{subtotal:.2f}"])

            writer.writerow([])
            writer.writerow(["TOTALES", "", "", "", total_stock, "", f"{valor_total:.2f}"])

        print(f"[EXITO] Reporte CSV para Excel generado en: {output_path}")
        return output_path
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == '__main__':
    print("==================================================")
    print("      GENERADOR DE REPORTES - PROYECTO COMERZIA   ")
    print("==================================================")
    generate_pdf_report()
    generate_inventory_report()
    export_products_csv()
