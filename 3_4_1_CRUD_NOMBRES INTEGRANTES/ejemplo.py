import os
from fpdf import FPDF

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Reportes')
os.makedirs(output_dir, exist_ok=True)

pdf = FPDF(orientation='P', unit='mm', format='A4') # Orientación P es vertical y L horizontal
pdf.add_page()
pdf.set_font('Helvetica', size=12)
pdf.cell(0, 10, 'Ejemplo básico de PDF generado con FPDF.')
pdf.output(os.path.join(output_dir, 'Reporte.pdf'))
print("PDF básico de ejemplo generado con éxito en Reportes/Reporte.pdf")