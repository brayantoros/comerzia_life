-- =======================================================
-- Base de Datos: tienda_db - Proyecto Productivo Comerzia
-- SENA - Analisis y Desarrollo de Software
-- Evidencia: 3_4_1_CRUD_NOMBRES INTEGRANTES
-- =======================================================

CREATE DATABASE IF NOT EXISTS tienda_db;
USE tienda_db;

-- Tabla de Productos de Comerzia
CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    stock INT NOT NULL DEFAULT 0,
    imagen VARCHAR(255) NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Datos de prueba para el catalogo de Comerzia
INSERT INTO productos (nombre, descripcion, precio, stock, imagen, activo) VALUES
('Saco Blazer', 'Saco de corte clasico en lana virgen color azul medianoche.', 45.00, 10, 'blazer_dama.jpg', 1),
('Camisa de Lino', 'Camisa de cuello italiano confeccionada en lino 100% organico.', 12.00, 10, 'camisa_de_lino.jpg', 1),
('Cardigan de Cashmere', 'Tejido de punto fino en color camel. Comodidad y estilo.', 21.00, 10, 'Cardigan_de_Cashmere.jpg', 1),
('Pantalon Casual', 'Pantalon de corte recto para uso diario.', 30.00, 15, NULL, 1),
('Zapatos de Cuero', 'Calzado formal de cuero vacuno.', 60.00, 8, NULL, 1),
('Chaqueta Cortaviento', 'Chaqueta impermeable ligera.', 35.00, 0, NULL, 0)
ON DUPLICATE KEY UPDATE id=id;
