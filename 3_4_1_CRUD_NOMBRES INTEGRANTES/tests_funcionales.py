"""
SUITE DE PRUEBAS FUNCIONALES AUTOMATIZADAS - PROYECTO PRODUCTIVO COMERZIA
Evidencia: 3_4_1_CRUD_NOMBRES INTEGRANTES
Actividad: 3.4.2 Actividad Transferencia de Conocimiento - PROYECTO PRODUCTIVO
Marco de Pruebas: unittest (Biblioteca estandar de Python)
"""

import os
import unittest
import warnings
from conexion import connect
from crud import (
    create_product,
    read_products,
    get_product_by_id,
    update_product,
    delete_product
)
from report import (
    generate_pdf_report,
    generate_inventory_report,
    export_products_csv,
    REPORTS_DIR
)

# Ignoramos avisos para una salida limpia en consola
warnings.simplefilter('ignore')


class TestComerziaProductos(unittest.TestCase):
    """Casos de prueba funcionales para validar la gestion de productos y generacion de reportes."""

    @classmethod
    def setUpClass(cls):
        """Inicializacion de variables y preparacion de datos de prueba."""
        cls.test_name = "Producto Automatizado de Prueba"
        cls.test_desc = "Descripcion de prueba para pruebas funcionales"
        cls.test_price = 35000.0
        cls.test_stock = 15
        cls.created_id = None

    @classmethod
    def tearDownClass(cls):
        """Limpieza final: borrado del producto de prueba y de archivos temporales de test."""
        if cls.created_id:
            try:
                delete_product(cls.created_id)
            except Exception:
                pass

        # Limpiamos los archivos temporales generados por las pruebas
        archivos_test = ["Test_Reporte_Productos.pdf", "Test_Reporte_Inventario.pdf", "Test_Reporte_Productos.csv"]
        for nombre in archivos_test:
            ruta = os.path.join(REPORTS_DIR, nombre)
            if os.path.exists(ruta):
                try:
                    os.remove(ruta)
                except Exception:
                    pass

    # CP-01: Conexion a la base de datos
    def test_01_conexion_tienda_db(self):
        """Valida que la conexion con la base de datos tienda_db sea exitosa."""
        conn = connect()
        self.assertIsNotNone(conn, "No se pudo establecer la conexion.")
        self.assertTrue(conn.is_connected(), "El estado de la conexion no esta activo.")
        conn.close()

    # CP-02: Lectura de productos preexistentes
    def test_02_lectura_productos_catalogo(self):
        """Valida que la consulta retorne una lista valida de productos."""
        productos = read_products()
        self.assertIsInstance(productos, list, "El resultado de la consulta debe ser una lista.")

    # CP-03: Insercion exitosa de un nuevo producto
    def test_03_crear_producto_exitoso(self):
        """Valida la insercion de un nuevo producto y persistencia en la BD."""
        nuevo_id = create_product(self.test_name, self.test_desc, self.test_price, self.test_stock)
        self.assertTrue(nuevo_id, "Fallo la creacion del producto.")
        TestComerziaProductos.created_id = nuevo_id

        # Verificamos que realmente se pueda consultar por su ID
        prod = get_product_by_id(nuevo_id)
        self.assertIsNotNone(prod, "El producto creado no fue encontrado en la BD.")
        self.assertEqual(prod['nombre'], self.test_name)
        self.assertEqual(float(prod['precio']), self.test_price)
        self.assertEqual(int(prod['stock']), self.test_stock)

    # CP-04: Validacion de precio no valido
    def test_04_rechazo_precio_invalido(self):
        """Valida que el sistema rechace productos con precio menor o igual a 0."""
        res_cero = create_product("Producto Invalido", "Test", 0, 10)
        res_negativo = create_product("Producto Invalido", "Test", -25000, 10)
        self.assertFalse(res_cero, "Se permitio registrar precio en 0.")
        self.assertFalse(res_negativo, "Se permitio registrar precio negativo.")

    # CP-05: Validacion de nombre vacio
    def test_05_rechazo_nombre_vacio(self):
        """Valida que no se permita registrar productos sin nombre."""
        res_vacio = create_product("", "Test", 20000, 5)
        res_espacios = create_product("   ", "Test", 20000, 5)
        self.assertFalse(res_vacio, "Se permitio registrar un nombre vacio.")
        self.assertFalse(res_espacios, "Se permitio registrar solo espacios en el nombre.")

    # CP-06: Validacion de stock negativo
    def test_06_rechazo_stock_negativo(self):
        """Valida que no se permita registrar productos con stock menor a 0."""
        res_stock = create_product("Producto Stock Malo", "Test", 15000, -5)
        self.assertFalse(res_stock, "Se permitio registrar stock negativo.")

    # CP-07: Actualizacion de producto existente
    def test_07_actualizar_producto_existente(self):
        """Valida la modificacion del precio y stock de un producto creado."""
        self.assertIsNotNone(self.created_id, "No hay producto de prueba para actualizar.")
        nuevo_precio = 48000.0
        nuevo_stock = 25
        resultado = update_product(self.created_id, precio=nuevo_precio, stock=nuevo_stock)
        self.assertTrue(resultado, "Fallo la actualizacion del producto.")

        # Comprobamos los cambios
        prod_modificado = get_product_by_id(self.created_id)
        self.assertEqual(float(prod_modificado['precio']), nuevo_precio)
        self.assertEqual(int(prod_modificado['stock']), nuevo_stock)

    # CP-08: Eliminacion del producto de prueba
    def test_08_eliminar_producto_existente(self):
        """Valida el borrado de un producto y confirma que ya no exista."""
        self.assertIsNotNone(self.created_id, "No hay producto de prueba para eliminar.")
        resultado = delete_product(self.created_id)
        self.assertTrue(resultado, "Fallo la eliminacion del producto.")

        # Confirmamos que ya no existe en la BD
        prod = get_product_by_id(self.created_id)
        self.assertIsNone(prod, "El producto sigue existiendo despues de eliminarlo.")
        TestComerziaProductos.created_id = None

    # CP-09: Verificacion fisica del Reporte 1 en PDF
    def test_09_generacion_reporte_pdf(self):
        """Valida que el Reporte 1 en PDF se genere en disco y no este vacio."""
        ruta_pdf = generate_pdf_report(filename="Test_Reporte_Productos.pdf")
        self.assertTrue(os.path.exists(ruta_pdf), "El archivo PDF no fue creado en disco.")
        self.assertGreater(os.path.getsize(ruta_pdf), 0, "El archivo PDF generado esta vacio.")

    # CP-10: Verificacion fisica del Reporte 2 de Inventario en PDF
    def test_10_generacion_reporte_inventario_pdf(self):
        """Valida que el Reporte 2 de Inventario se genere en disco y no este vacio."""
        ruta_pdf = generate_inventory_report(filename="Test_Reporte_Inventario.pdf")
        self.assertTrue(os.path.exists(ruta_pdf), "El archivo de inventario PDF no fue creado.")
        self.assertGreater(os.path.getsize(ruta_pdf), 0, "El archivo de inventario esta vacio.")

    # CP-11: Verificacion fisica de la exportacion a CSV (Excel)
    def test_11_exportacion_csv_excel(self):
        """Valida que el archivo CSV para Excel se cree en disco y contenga datos."""
        ruta_csv = export_products_csv(filename="Test_Reporte_Productos.csv")
        self.assertTrue(os.path.exists(ruta_csv), "El archivo CSV no fue creado en disco.")
        self.assertGreater(os.path.getsize(ruta_csv), 0, "El archivo CSV generado esta vacio.")


if __name__ == '__main__':
    print("\n" + "=" * 65)
    print("   EJECUTANDO PRUEBAS FUNCIONALES - PROYECTO PRODUCTIVO COMERZIA")
    print("=" * 65 + "\n")
    unittest.main(verbosity=2, warnings='ignore')
