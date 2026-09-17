# Informe de Pruebas Funcionales y Reportes del Proyecto Productivo

**Evidencia:** 3_4_1_CRUD_NOMBRES INTEGRANTES  
**Actividad:** 3.4.2 Actividad Transferencia de Conocimiento - PROYECTO PRODUCTIVO  
**Proyecto Productivo:** Comerzia (Tienda Virtual / Comercio Electronico)  
**Entorno de Formacion:** SENA - Analisis y Desarrollo de Software  
**Base de Datos Utilizada:** tienda_db (Tabla: productos)  

---

## 1. Descripcion de la Actividad y Aplicacion al Proyecto

En esta actividad de transferencia de conocimiento, tomamos la base del modulo CRUD y generacion de reportes vista en la guia y en clases practicas, y la adaptamos directamente a los datos y necesidades reales de nuestro **proyecto productivo Comerzia**.

En lugar de utilizar tablas genericas de prueba, conectamos el sistema a la base de datos real `tienda_db` y enfocamos el modulo en la gestion del **catalogo de productos e inventario**, permitiendo:
1. Administrar los productos (crear, consultar, actualizar stock/precio y eliminar).
2. Generar reportes oficiales del catalogo y estado de bodega en formato **PDF** (usando FPDF y membrete corporativo) y en formato tabular para **Microsoft Excel** (en formato CSV delimitado por punto y coma).
3. Implementar una bateria de pruebas funcionales automatizadas con la libreria estandar `unittest` de Python para asegurar la calidad y estabilidad de la base de datos y de la logica del sistema.

---

## 2. Estructura de la Carpeta de la Evidencia

```text
3_4_1_CRUD_NOMBRES INTEGRANTES/
│
├── conexion.py                 # Modulo de conexion a MariaDB/MySQL (tienda_db)
├── crud.py                     # Operaciones CRUD para productos y menu por consola
├── report.py                   # Generador de reportes en PDF y exportacion a Excel (CSV)
├── tests_funcionales.py        # Suite de 11 pruebas automatizadas con unittest
├── crud_db.sql                 # Script SQL con la estructura y datos de Comerzia
├── INFORME_PRUEBAS_FUNCIONALES.md # Este documento de evidencias
│
├── img/                        # Recursos graficos institucionales
│   ├── header.jpg              # Membrete superior para los reportes PDF
│   └── footer.jpg              # Pie de pagina institucional
│
└── Reportes/                   # Carpeta de salida con los documentos generados
    ├── Reporte_Productos.pdf   # Reporte 1: PDF General del Catalogo
    ├── Reporte_Inventario.pdf  # Reporte 2: PDF de Control de Inventario y Stock
    └── Reporte_Productos.csv   # Reporte Tabular para Microsoft Excel
```

---

## 3. Descripcion de los Reportes Desarrollados

Siguiendo los lineamientos de la guia de aprendizaje y los materiales de apoyo, se implementaron dos tipos de reportes en PDF y uno en formato de hoja de calculo:

1. **Reporte 1: Catalogo General de Productos (`Reporte_Productos.pdf`)**
   - Encabezado con imagen corporativa (`header.jpg`).
   - Titulo institucional y cantidad de productos registrados en `tienda_db`.
   - Tabla estructurada con columnas: ID, Nombre del Producto, Precio Unitario, Stock y Estado (Activo, Inactivo o Agotado).
   - Resumen totalizador al pie con la cantidad total de unidades en bodega y el valor monetario estimado del inventario.

2. **Reporte 2: Control de Inventario y Stock (`Reporte_Inventario.pdf`)**
   - Enfocado en la gestion logistica de la tienda.
   - Clasifica los productos por nivel de existencias e identifica rapidamente aquellos que estan agotados para su reposicion.

3. **Reporte Adicional: Exportacion para Microsoft Excel (`Reporte_Productos.csv`)**
   - Generado con la libreria nativa `csv` de Python.
   - Codificado en `utf-8-sig` con delimitador punto y coma (`;`) para que abra de forma directa y ordenada en columnas en Microsoft Excel en Windows, sin danar las tildes.

---

## 4. Matriz de Pruebas Funcionales Automatizadas (unittest)

Se desarrollo el archivo `tests_funcionales.py` para verificar que la gestion de productos y la generacion de reportes funcionen correctamente de principio a fin:

| Caso de Prueba | Metodo de Prueba | Descripcion / Objetivo | Resultado |
|:---|:---|:---|:---:|
| **CP-01** | `test_01_conexion_tienda_db` | Verificar conectividad exitosa con el servidor MySQL y la base de datos `tienda_db`. | Aprobado (OK) |
| **CP-02** | `test_02_lectura_productos_catalogo` | Validar la consulta de los productos existentes en el catalogo. | Aprobado (OK) |
| **CP-03** | `test_03_crear_producto_exitoso` | Validar la insercion de un producto de prueba y su persistencia en la base de datos. | Aprobado (OK) |
| **CP-04** | `test_04_rechazo_precio_invalido` | Validar que el sistema impida registrar productos con precio en 0 o negativo. | Aprobado (OK) |
| **CP-05** | `test_05_rechazo_nombre_vacio` | Validar que el sistema impida registrar productos con nombre vacio o puros espacios. | Aprobado (OK) |
| **CP-06** | `test_06_rechazo_stock_negativo` | Validar que no se puedan guardar cantidades de inventario negativas. | Aprobado (OK) |
| **CP-07** | `test_07_actualizar_producto_existente` | Validar la modificacion exitosa de precio y stock de un producto existente. | Aprobado (OK) |
| **CP-08** | `test_08_eliminar_producto_existente` | Validar el borrado fisico del producto de prueba y comprobar que ya no exista. | Aprobado (OK) |
| **CP-09** | `test_09_generacion_reporte_pdf` | Validar la creacion fisica del Reporte 1 en PDF y comprobar que el archivo no este vacio. | Aprobado (OK) |
| **CP-10** | `test_10_generacion_reporte_inventario_pdf` | Validar la creacion fisica del Reporte 2 de inventario en PDF. | Aprobado (OK) |
| **CP-11** | `test_11_exportacion_csv_excel` | Validar la generacion correcta del archivo CSV para Excel en disco. | Aprobado (OK) |

---

## 5. Instrucciones de Ejecucion

Para interactuar con el sistema o correr las pruebas:

1. **Ejecutar el menu interactivo de gestion:**
   ```bash
   cd "3_4_1_CRUD_NOMBRES INTEGRANTES"
   python crud.py
   ```

2. **Ejecutar la suite de pruebas funcionales:**
   ```bash
   cd "3_4_1_CRUD_NOMBRES INTEGRANTES"
   python tests_funcionales.py
   ```

3. **Generar los reportes directamente:**
   ```bash
   cd "3_4_1_CRUD_NOMBRES INTEGRANTES"
   python report.py
   ```

---

## 6. Conclusiones

La realizacion de esta actividad permitio aplicar directamente los conceptos de persistencia relacional, aseguramiento de la calidad mediante pruebas funcionales con `unittest` y generacion de reportes administrativos a nuestro proyecto productivo Comerzia. Esto fortalece la confiabilidad del sistema y asegura que los datos del catalogo puedan ser analizados y reportados en formatos estandar de la industria.