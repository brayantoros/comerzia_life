import os
import csv
from datetime import datetime
from fpdf import FPDF
from conexion import connect
import mysql.connector

# Rutas base dinámicas para garantizar portabilidad
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "Reportes")
IMG_DIR = os.path.join(BASE_DIR, "img")
HEADER_IMG = os.path.join(IMG_DIR, "header.jpg")
FOOTER_IMG = os.path.join(IMG_DIR, "footer.jpg")

# Asegurar que el directorio de reportes exista siempre
os.makedirs(REPORTS_DIR, exist_ok=True)


class CustomPDF(FPDF):
    """Clase personalizada de FPDF con encabezado y pie de página institucionales."""
    
    def __init__(self, report_title="Reporte del Sistema", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report_title = report_title
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        # 1. Banda superior decorativa
        self.set_fill_color(26, 54, 93)  # Azul corporativo profundo
        self.rect(0, 0, 210, 18, 'F')
        
        # 2. Imagen de cabecera si existe
        if os.path.exists(HEADER_IMG):
            try:
                self.image(HEADER_IMG, x=10, y=2, w=45, h=14)
            except Exception:
                pass

        # 3. Título del reporte
        self.set_font("Helvetica", style="B", size=13)
        self.set_text_color(255, 255, 255)
        self.set_xy(60, 4)
        self.cell(140, 10, self.report_title, align="R")
        
        self.set_text_color(0, 0, 0)
        self.ln(18)

    def footer(self):
        self.set_y(-18)
        self.set_font("Helvetica", style="I", size=8)
        self.set_text_color(100, 100, 100)
        
        # Línea divisoria
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        
        # Información de pie de página
        fecha_gen = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.cell(100, 6, f"Comerzia CRUD | Generado el: {fecha_gen}", align="L")
        self.cell(90, 6, f"Página {self.page_no()}", align="R")


def generate_pdf_report(filename="Reporte_Usuarios.pdf"):
    """
    REPORTE 1: Reporte General de Usuarios en Formato PDF.
    Genera un listado completo y estilizado de los usuarios registrados.
    """
    output_path = os.path.join(REPORTS_DIR, filename)
    connection = None
    cursor = None
    
    try:
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, email, age FROM users ORDER BY id ASC")
        users = cursor.fetchall()

        pdf = CustomPDF(report_title="Reporte General de Usuarios")
        pdf.add_page()

        # Metadatos del documento
        pdf.set_font("Helvetica", style="B", size=14)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, "LISTADO OFICIAL DE USUARIOS REGISTRADOS")
        pdf.ln(8)
        
        pdf.set_font("Helvetica", size=9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 5, f"Total de registros consultados: {len(users)} | Base de Datos: crud_db")
        pdf.ln(8)

        # Encabezado de la tabla
        pdf.set_font("Helvetica", style="B", size=10)
        pdf.set_fill_color(37, 99, 235)      # Azul vibrante
        pdf.set_text_color(255, 255, 255)    # Texto blanco
        pdf.set_draw_color(203, 213, 225)
        
        pdf.cell(18, 9, "ID", border=1, align="C", fill=True)
        pdf.cell(65, 9, "Nombre Completo", border=1, align="L", fill=True)
        pdf.cell(82, 9, "Correo Electrónico", border=1, align="L", fill=True)
        pdf.cell(25, 9, "Edad", border=1, align="C", fill=True)
        pdf.ln()

        # Filas de la tabla con efecto cebra (zebra striping)
        pdf.set_font("Helvetica", size=9)
        for i, user in enumerate(users):
            if i % 2 == 0:
                pdf.set_fill_color(248, 250, 252)  # Fondo blanco hueso
            else:
                pdf.set_fill_color(241, 245, 249)  # Fondo grisáceo claro
            
            pdf.set_text_color(15, 23, 42)
            pdf.cell(18, 8, str(user[0]), border=1, align="C", fill=True)
            pdf.cell(65, 8, str(user[1]), border=1, align="L", fill=True)
            pdf.cell(82, 8, str(user[2]), border=1, align="L", fill=True)
            pdf.cell(25, 8, f"{user[3]} años", border=1, align="C", fill=True)
            pdf.ln()

        # Resumen al final de la tabla
        pdf.ln(4)
        pdf.set_font("Helvetica", style="B", size=10)
        pdf.set_fill_color(226, 232, 240)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(165, 8, "TOTAL DE USUARIOS ACTIVOS:", border=1, align="R", fill=True)
        pdf.cell(25, 8, str(len(users)), border=1, align="C", fill=True)
        pdf.ln()

        # Guardar archivo PDF
        pdf.output(output_path)
        print(f"[REPORTE GENERADO] Reporte general guardado con éxito en: {output_path}")
        return output_path

    except mysql.connector.Error as err:
        print(f"[ERROR BD EN REPORTE 1]: {err}")
        return None
    except Exception as ex:
        print(f"[ERROR INESPERADO EN REPORTE 1]: {ex}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def generate_statistical_report(filename="Reporte_Estadistico_Usuarios.pdf"):
    """
    REPORTE 2 (NUEVO): Reporte Estadístico y Demográfico de Usuarios en Formato PDF.
    Calcula KPIs demográficos (promedios, rangos etarios, porcentajes) y genera un informe analítico.
    """
    output_path = os.path.join(REPORTS_DIR, filename)
    connection = None
    cursor = None

    try:
        connection = connect()
        cursor = connection.cursor()

        # 1. Consulta de métricas generales
        cursor.execute("SELECT COUNT(*), COALESCE(AVG(age), 0), COALESCE(MIN(age), 0), COALESCE(MAX(age), 0) FROM users")
        stats = cursor.fetchone()
        total_users = stats[0]
        avg_age = round(float(stats[1]), 1)
        min_age = int(stats[2])
        max_age = int(stats[3])

        # 2. Distribución por rangos etarios
        # Rango 1: < 25 años
        cursor.execute("SELECT COUNT(*) FROM users WHERE age < 25")
        count_jovenes = cursor.fetchone()[0]
        # Rango 2: 25 a 30 años
        cursor.execute("SELECT COUNT(*) FROM users WHERE age BETWEEN 25 AND 30")
        count_adultos_jovenes = cursor.fetchone()[0]
        # Rango 3: > 30 años
        cursor.execute("SELECT COUNT(*) FROM users WHERE age > 30")
        count_adultos = cursor.fetchone()[0]

        # Porcentajes
        pct_jovenes = round((count_jovenes / total_users * 100), 1) if total_users > 0 else 0
        pct_adultos_jov = round((count_adultos_jovenes / total_users * 100), 1) if total_users > 0 else 0
        pct_adultos = round((count_adultos / total_users * 100), 1) if total_users > 0 else 0

        # Crear PDF
        pdf = CustomPDF(report_title="Reporte Estadístico y Demográfico")
        pdf.add_page()

        # Título principal
        pdf.set_font("Helvetica", style="B", size=14)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, "ANÁLISIS ESTADÍSTICO Y DEMOGRÁFICO POR EDADES")
        pdf.ln(8)
        
        pdf.set_font("Helvetica", size=9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 5, "Métricas consolidadas de usuarios para toma de decisiones y segmentación.")
        pdf.ln(8)

        # SECCIÓN 1: TARJETAS DE INDICADORES CLAVE (KPIs)
        kpi_width = 45
        kpi_height = 18
        
        # KPI 1: Total
        pdf.set_fill_color(238, 242, 255)
        pdf.set_draw_color(199, 210, 254)
        pdf.rect(10, pdf.get_y(), kpi_width, kpi_height, 'DF')
        pdf.set_xy(10, pdf.get_y() + 2)
        pdf.set_font("Helvetica", style="B", size=8)
        pdf.set_text_color(79, 70, 229)
        pdf.cell(kpi_width, 4, "TOTAL USUARIOS", align="C")
        pdf.ln(4)
        pdf.set_font("Helvetica", style="B", size=14)
        pdf.cell(kpi_width, 8, str(total_users), align="C")

        # KPI 2: Edad Promedio
        curr_y = pdf.get_y() - 10
        pdf.set_fill_color(240, 253, 244)
        pdf.set_draw_color(187, 247, 208)
        pdf.rect(58, curr_y, kpi_width, kpi_height, 'DF')
        pdf.set_xy(58, curr_y + 2)
        pdf.set_font("Helvetica", style="B", size=8)
        pdf.set_text_color(22, 163, 74)
        pdf.cell(kpi_width, 4, "EDAD PROMEDIO", align="C")
        pdf.ln(4)
        pdf.set_font("Helvetica", style="B", size=14)
        pdf.cell(kpi_width, 8, f"{avg_age} años", align="C")

        # KPI 3: Edad Mínima
        pdf.set_fill_color(254, 242, 242)
        pdf.set_draw_color(254, 202, 202)
        pdf.rect(106, curr_y, kpi_width, kpi_height, 'DF')
        pdf.set_xy(106, curr_y + 2)
        pdf.set_font("Helvetica", style="B", size=8)
        pdf.set_text_color(220, 38, 38)
        pdf.cell(kpi_width, 4, "EDAD MÍNIMA", align="C")
        pdf.ln(4)
        pdf.set_font("Helvetica", style="B", size=14)
        pdf.cell(kpi_width, 8, f"{min_age} años", align="C")

        # KPI 4: Edad Máxima
        pdf.set_fill_color(254, 249, 195)
        pdf.set_draw_color(253, 224, 71)
        pdf.rect(154, curr_y, kpi_width, kpi_height, 'DF')
        pdf.set_xy(154, curr_y + 2)
        pdf.set_font("Helvetica", style="B", size=8)
        pdf.set_text_color(202, 138, 4)
        pdf.cell(kpi_width, 4, "EDAD MÁXIMA", align="C")
        pdf.ln(4)
        pdf.set_font("Helvetica", style="B", size=14)
        pdf.cell(kpi_width, 8, f"{max_age} años", align="C")

        pdf.set_xy(10, curr_y + kpi_height + 8)

        # SECCIÓN 2: TABLA DE DISTRIBUCIÓN POR RANGOS DE EDAD
        pdf.set_font("Helvetica", style="B", size=11)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, "DISTRIBUCIÓN Y SEGMENTACIÓN POR RANGOS ETARIOS")
        pdf.ln(8)

        pdf.set_font("Helvetica", style="B", size=9)
        pdf.set_fill_color(15, 23, 42)
        pdf.set_text_color(255, 255, 255)
        pdf.set_draw_color(203, 213, 225)
        pdf.cell(60, 8, "Rango de Edad", border=1, align="L", fill=True)
        pdf.cell(35, 8, "Cantidad de Usuarios", border=1, align="C", fill=True)
        pdf.cell(35, 8, "Participación (%)", border=1, align="C", fill=True)
        pdf.cell(60, 8, "Representación Gráfica", border=1, align="L", fill=True)
        pdf.ln()

        rangos = [
            ("Menores de 25 años (< 25)", count_jovenes, pct_jovenes, (59, 130, 246)),
            ("Adultos Jóvenes (25 - 30)", count_adultos_jovenes, pct_adultos_jov, (16, 185, 129)),
            ("Adultos mayores de 30 (> 30)", count_adultos, pct_adultos, (245, 158, 11))
        ]

        pdf.set_font("Helvetica", size=9)
        for nombre, cant, pct, color in rangos:
            pdf.set_fill_color(248, 250, 252)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(60, 9, nombre, border=1, align="L", fill=True)
            pdf.cell(35, 9, str(cant), border=1, align="C", fill=True)
            pdf.cell(35, 9, f"{pct}%", border=1, align="C", fill=True)
            
            # Celda de representación gráfica (barra proporcional)
            x_bar = pdf.get_x()
            y_bar = pdf.get_y()
            pdf.cell(60, 9, "", border=1, fill=True)
            
            # Dibujar mini barra de progreso dentro de la celda
            bar_max_width = 50
            bar_width = max(1.0, (pct / 100.0) * bar_max_width)
            pdf.set_fill_color(*color)
            pdf.rect(x_bar + 5, y_bar + 2.5, bar_width, 4, 'F')
            pdf.ln()

        # SECCIÓN 3: DETALLE DE USUARIOS ORDENADOS POR EDAD
        pdf.ln(6)
        pdf.set_font("Helvetica", style="B", size=11)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, "LISTADO DE USUARIOS ORDENADO POR EDAD (DE MENOR A MAYOR)")
        pdf.ln(8)

        cursor.execute("SELECT id, name, email, age FROM users ORDER BY age ASC, id ASC")
        users_by_age = cursor.fetchall()

        pdf.set_font("Helvetica", style="B", size=9)
        pdf.set_fill_color(71, 85, 105)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(20, 8, "ID", border=1, align="C", fill=True)
        pdf.cell(65, 8, "Nombre", border=1, align="L", fill=True)
        pdf.cell(75, 8, "Email", border=1, align="L", fill=True)
        pdf.cell(30, 8, "Edad", border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("Helvetica", size=9)
        for i, u in enumerate(users_by_age):
            if i % 2 == 0:
                pdf.set_fill_color(255, 255, 255)
            else:
                pdf.set_fill_color(241, 245, 249)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(20, 7, str(u[0]), border=1, align="C", fill=True)
            pdf.cell(65, 7, str(u[1]), border=1, align="L", fill=True)
            pdf.cell(75, 7, str(u[2]), border=1, align="L", fill=True)
            pdf.cell(30, 7, f"{u[3]} años", border=1, align="C", fill=True)
            pdf.ln()

        # Guardar archivo PDF
        pdf.output(output_path)
        print(f"[REPORTE GENERADO] Reporte estadístico guardado con éxito en: {output_path}")
        return output_path

    except mysql.connector.Error as err:
        print(f"[ERROR BD EN REPORTE 2]: {err}")
        return None
    except Exception as ex:
        print(f"[ERROR INESPERADO EN REPORTE 2]: {ex}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def export_users_csv(filename="Reporte_Usuarios.csv"):
    """
    REPORTE ADICIONAL TABULAR: Exportación completa de usuarios a archivo CSV (compatible con Excel).
    """
    output_path = os.path.join(REPORTS_DIR, filename)
    connection = None
    cursor = None

    try:
        connection = connect()
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, email, age FROM users ORDER BY id ASC")
        users = cursor.fetchall()

        # Utilizar 'utf-8-sig' para compatibilidad nativa con Microsoft Excel en español
        with open(output_path, mode="w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            # Encabezados
            writer.writerow(["ID", "Nombre", "Email", "Edad"])
            # Filas
            for u in users:
                writer.writerow([u[0], u[1], u[2], u[3]])

        print(f"[EXPORTACIÓN EXITOSA] Archivo CSV generado con éxito en: {output_path}")
        return output_path

    except Exception as err:
        print(f"[ERROR EN EXPORTACIÓN CSV]: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    print("Probando generación de reportes...")
    rep1 = generate_pdf_report()
    rep2 = generate_statistical_report()
    rep3 = export_users_csv()
    print("Resultados:", rep1, rep2, rep3)

