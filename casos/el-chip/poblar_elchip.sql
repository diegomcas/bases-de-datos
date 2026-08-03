USE `el_chip`;

-- -----------------------------------------------------
-- 1. POBLAR TABLAS MAESTRAS
-- -----------------------------------------------------

-- Roles
INSERT INTO `rol` (`nombre`) VALUES ('Administrador'), ('Tecnico');

-- Estados de Orden
INSERT INTO `orden_estado` (`nombre`) VALUES ('Pendiente'), ('Reparado'), ('Entregado'), ('Abandonado');

-- Métodos de Pago
INSERT INTO `metodo_pago` (`nombre`) VALUES ('Efectivo'), ('Tarjeta'), ('Transferencia'), ('Billetera Virtual');

-- Tipos de Teléfono
INSERT INTO `telefonotipo` (`tipo`) VALUES ('Celular'), ('Fijo'), ('Trabajo');

-- Tipos de Email
INSERT INTO `emailtipo` (`tipo`) VALUES ('Personal'), ('Trabajo');

-- Marcas
INSERT INTO `marca` (`nombre`) VALUES ('Samsung'), ('Apple'), ('Lenovo'), ('Motorola'), ('Xiaomi'), ('Google'), ('Sony');

-- Problemas
INSERT INTO `problema` (`descripcion`, `mano_obra`) VALUES 
('Pantalla rota / Cambio de modulo', 8500.00),
('Batería agotada / Cambio de batería', 4500.00),
('Pin de carga dañado', 5000.00),
('Limpieza y mantenimiento preventivo', 3000.00),
('Error de Software / Reinstalación', 6000.00),
('Cámara principal no enfoca', 7500.00);

-- Repuestos
INSERT INTO `repuesto` (`nombre`, `stock`, `precio_unitario`) VALUES 
('Módulo Samsung S21 Original', 5, 45000.00),
('Módulo iPhone 13 Genérico', 3, 32000.00),
('Batería iPhone 11/12', 10, 12000.00),
('Pin de carga Universal USB-C', 50, 1500.00),
('Módulo Motorola Edge 30', 2, 28000.00),
('Batería Samsung Serie A', 8, 9500.00);

-- -----------------------------------------------------
-- 2. RELACIONAR PROBLEMAS CON REPUESTOS (Histórico de Precios)
-- -----------------------------------------------------
INSERT INTO `problema_has_repuesto` (`id_problema`, `id_repuesto`, `cantidad`, `precio_unitario`, `mano_obra`) VALUES 
(1, 1, 1, 45000.00, 8500.00), -- Pantalla S21
(1, 2, 1, 32000.00, 8000.00), -- Pantalla iPhone 13
(2, 3, 1, 12000.00, 4500.00), -- Batería iPhone
(3, 4, 1, 1500.00, 5000.00);  -- Pin de carga

-- -----------------------------------------------------
-- 3. POBLAR ENTIDADES PRINCIPALES
-- -----------------------------------------------------

-- Clientes
INSERT INTO `cliente` (`nombre`, `apellido`) VALUES 
('Juan', 'Pérez'),
('María', 'García'),
('Carlos', 'López'),
('Ana', 'Martínez'),
('Diego', 'Rossi');

-- Teléfonos (Relacionados con Clientes)
INSERT INTO `telefono` (`numero`, `descripcion`, `id_telefonotipo`, `id_cliente`) VALUES 
('3415551234', 'Personal', 1, 1),
('3415555678', 'Casa', 2, 2),
('3415559012', 'Trabajo', 3, 3),
('3415553456', 'Celular Ana', 1, 4);

-- Emails (Relacionados con Clientes)
INSERT INTO `email` (`email`, `id_emailtipo`, `id_cliente`) VALUES 
('juan.perez@email.com', 1, 1),
('m.garcia@gmail.com', 1, 2),
('carlos_trabajo@empresa.com', 2, 3),
('ana.mtz@yahoo.com', 1, 4);

-- Equipos (Relacionados con Marcas)
INSERT INTO `equipo` (`tipo`, `id_marca`, `modelo`, `nro_serie`) VALUES 
('Celular', 1, 'Galaxy S21', 'S21-998877'),    -- Samsung
('Celular', 2, 'iPhone 13', 'IPH13-112233'),   -- Apple
('Tablet', 3, 'Tab P11', 'LEN-TAB-5544'),       -- Lenovo
('Celular', 4, 'Edge 30', 'MOT-E30-7766'),      -- Motorola
('Smartwatch', 5, 'Mi Band 7', 'XIA-MB7-0011'); -- Xiaomi

-- Empleados (Relacionados con Roles)
INSERT INTO `empleado` (`usuario`, `password`, `id_rol`) VALUES 
('admin', 'hash_admin_2026', 1),
('tecnico_juan', 'hash_juan_99', 2),
('tecnico_ana', 'hash_ana_88', 2);

-- -----------------------------------------------------
-- 4. TRANSACCIONES: ÓRDENES Y PAGOS
-- -----------------------------------------------------

-- Órdenes de Servicio
INSERT INTO `orden_servicio` (`nro_orden`, `fecha_ingreso`, `id_empleado`, `id_cliente`, `id_orden_estado`, `total`) VALUES 
(1, '2026-05-01 10:00:00', 2, 1, 3, 53500.00), -- Entregado
(2, '2026-05-02 11:30:00', 3, 2, 3, 40500.00), -- Entregado
(3, '2026-05-10 10:45:00', 2, 5, 1, 0.00);      -- Pendiente

-- Pagos (Caso N:M - Orden 1 pagada con Efectivo y Tarjeta)
INSERT INTO `orden_servicio_pago` (`nro_orden`, `id_metodo_pago`, `monto`) VALUES 
(1, 1, 20000.00), -- Efectivo
(1, 2, 33500.00), -- Tarjeta
(2, 3, 40500.00); -- Transferencia

-- Relación Orden - Equipo - Problema
INSERT INTO `orden_servicio_has_equipo` (`nro_orden`, `id_equipo`, `id_problema`) VALUES 
(1, 1, 1), -- Orden 1, Galaxy S21, Pantalla rota
(2, 2, 1), -- Orden 2, iPhone 13, Pantalla rota
(3, 5, 4); -- Orden 3, Mi Band 7, Limpieza
