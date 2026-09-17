-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 17-09-2026 a las 23:46:56
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `tienda_db3`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `carrito`
--

CREATE TABLE `carrito` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `carrito`
--

INSERT INTO `carrito` (`id`, `usuario_id`, `fecha_creacion`) VALUES
(1, 3, '2026-05-21 00:10:04'),
(2, 1, '2026-05-27 23:53:04');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `carrito_productos`
--

CREATE TABLE `carrito_productos` (
  `carrito_id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `carrito_productos`
--

INSERT INTO `carrito_productos` (`carrito_id`, `producto_id`, `cantidad`) VALUES
(2, 2, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos`
--

CREATE TABLE `pedidos` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `total` decimal(10,2) NOT NULL DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `pedidos`
--

INSERT INTO `pedidos` (`id`, `usuario_id`, `fecha`, `total`) VALUES
(1, 3, '2026-05-21 00:11:44', 1.00),
(2, 1, '2026-05-27 23:55:09', 50001.00),
(3, 3, '2026-09-17 19:27:45', 45.00),
(4, 3, '2026-09-17 19:49:18', 12.00),
(5, 3, '2026-09-17 20:26:51', 3.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos_productos`
--

CREATE TABLE `pedidos_productos` (
  `pedido_id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `pedidos_productos`
--

INSERT INTO `pedidos_productos` (`pedido_id`, `producto_id`, `cantidad`, `precio_unitario`) VALUES
(2, 2, 1, 1.00),
(2, 3, 1, 50000.00),
(3, 4, 1, 45.00),
(4, 5, 1, 12.00),
(5, 2, 3, 1.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `precio` decimal(10,2) NOT NULL DEFAULT 0.00,
  `imagen` varchar(255) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  `stock` int(11) NOT NULL DEFAULT 10
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `imagen`, `activo`, `stock`) VALUES
(2, 'pastrana', 'lo puedes llevar a cualquier parte', 1.00, 'pastrana.jpg', 1, 0),
(3, 'Brayan Ricardo', 'yo', 50000.00, NULL, 0, 2),
(4, 'Saco Blazer', 'Saco de corte clásico en lana virgen color azul medianoche. Botones de cuerno genuino y forro de seda satinada. Ideal para eventos formales.', 45.00, 'blazer_dama.jpg', 1, 2),
(5, 'Camisa de Lino', 'Camisa de cuello italiano confeccionada en lino 100% orgánico. Frescura y distinción para climas cálidos o reuniones de día.', 12.00, 'camisa_de_lino.jpg', 1, 2),
(6, 'Cárdigan de Cashmere', 'Tejido de punto fino en color camel. Una pieza versátil y sofisticada para el caballero que aprecia la comodidad sin perder el estilo.', 21.00, 'Cardigan_de_Cashmere.jpg', 1, 2),
(7, 'Cinturón de Cuero', 'Cuero de plena flor curtido vegetalmente con hebilla de latón envejecido. El complemento esencial para un conjunto señorial.', 40.00, 'Cinturon_de_Cuero.jpg', 1, 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `rol` enum('admin','cliente') NOT NULL DEFAULT 'cliente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `nombre`, `apellido`, `correo`, `username`, `password`, `rol`) VALUES
(1, 'brayan', 'toro', 'brayan@comerzia.com', 'cliente', 'pbkdf2:sha256:260000$TDVDgXeWKVlf8h6P$bb0a36866d2cd3e11e7547226bfc6e0110bc0fc068b699f10a07fa14b163d649', 'cliente'),
(3, 'admin', '2', 'admin@comerzia.com', 'admin123', 'pbkdf2:sha256:260000$5Qr2R6IgNqN6pBoc$bd3888c572820641e0bd18d63ec288b3078fada67d94d97ee3988806f810ee2c', 'admin');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `carrito`
--
ALTER TABLE `carrito`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_carrito_usuario` (`usuario_id`);

--
-- Indices de la tabla `carrito_productos`
--
ALTER TABLE `carrito_productos`
  ADD PRIMARY KEY (`carrito_id`,`producto_id`),
  ADD KEY `fk_cp_producto` (`producto_id`);

--
-- Indices de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_pedidos_usuario` (`usuario_id`);

--
-- Indices de la tabla `pedidos_productos`
--
ALTER TABLE `pedidos_productos`
  ADD PRIMARY KEY (`pedido_id`,`producto_id`),
  ADD KEY `fk_pp_producto` (`producto_id`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `correo` (`correo`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `carrito`
--
ALTER TABLE `carrito`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `carrito`
--
ALTER TABLE `carrito`
  ADD CONSTRAINT `fk_carrito_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `carrito_productos`
--
ALTER TABLE `carrito_productos`
  ADD CONSTRAINT `fk_cp_carrito` FOREIGN KEY (`carrito_id`) REFERENCES `carrito` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_cp_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD CONSTRAINT `fk_pedidos_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `pedidos_productos`
--
ALTER TABLE `pedidos_productos`
  ADD CONSTRAINT `fk_pp_pedido` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_pp_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
