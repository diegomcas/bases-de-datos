-- ======================================================
-- LIVE DEMO: NORMALIZACIÓN "EL CHIP"
-- ======================================================

-- 1. EL CAOS: La Tabla Excel de Martín
-- ------------------------------------------------------
CREATE DATABASE IF NOT EXISTS el_chip_masterclass;
USE el_chip_masterclass;

DROP TABLE IF EXISTS planilla_excel;
CREATE TABLE planilla_excel (
    nro_orden INT,
    fecha DATE,
    cliente VARCHAR(100),
    tel_cliente VARCHAR(20),
    equipo_marca VARCHAR(50),
    equipo_modelo VARCHAR(50),
    problemas VARCHAR(255),
    repuestos VARCHAR(255),
    precios_repuestos VARCHAR(255),
    total DECIMAL(10,2)
);

INSERT INTO planilla_excel VALUES 
(101, '2026-06-01', 'Juan Perez', '11-2222', 'iPhone', '13', 'Pantalla, Batería', 'Pantalla iPhone 13, Batería iPhone 13', '15000, 8000', 23000.00),
(102, '2026-06-02', 'Ana Lopez', '11-3333', 'Samsung', 'S22', 'Pin de Carga', 'Pin Samsung S22', '5000', 5000.00),
(103, '2026-06-03', 'Juan Perez', '11-2222', 'iPhone', '13', 'Vidrio Templado', 'Vidrio iPhone 13', '2000', 2000.00);

-- DEMO: ¿Cómo busco todos los equipos que usaron "Batería"? 
-- El LIKE es lento y propenso a errores.
SELECT * FROM planilla_excel WHERE repuestos LIKE '%Batería%';

-- ------------------------------------------------------
-- 2. HACIA LA 1NF (Atomaticidad)
-- ------------------------------------------------------
-- Eliminamos los grupos repetidos (las comas).
-- Ahora cada fila es una combinación de Orden + Problema/Repuesto.

DROP TABLE IF EXISTS ordenes_1nf;
CREATE TABLE ordenes_1nf AS
SELECT 101 as nro_orden, '2026-06-01' as fecha, 'Juan Perez' as cliente, '11-2222' as tel_cliente, 'iPhone' as equipo_marca, '13' as equipo_modelo, 'Pantalla' as problema, 'Pantalla iPhone 13' as repuesto, 15000.00 as precio_repuesto
UNION ALL
SELECT 101, '2026-06-01', 'Juan Perez', '11-2222', 'iPhone', '13', 'Batería', 'Batería iPhone 13', 8000.00
UNION ALL
SELECT 102, '2026-06-02', 'Ana Lopez', '11-3333', 'Samsung', 'S22', 'Pin de Carga', 'Pin Samsung S22', 5000.00
UNION ALL
SELECT 103, '2026-06-03', 'Juan Perez', '11-2222', 'iPhone', '13', 'Vidrio Templado', 'Vidrio iPhone 13', 2000.00;

-- ------------------------------------------------------
-- 3. HACIA LA 2NF (Dependencia de toda la PK)
-- ------------------------------------------------------
-- PK es (nro_orden, problema). 
-- ¿El tel_cliente depende del problema? NO. Depende del nro_orden.
-- Separamos CLIENTES y REPUESTOS.

CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    telefono VARCHAR(20)
);

CREATE TABLE repuestos (
    id_repuesto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    precio_actual DECIMAL(10,2)
);

-- ------------------------------------------------------
-- 4. HACIA LA 3NF (Dependencia Transitiva)
-- ------------------------------------------------------
-- En EQUIPOS: ID -> Modelo -> Marca.
-- Separamos MARCAS de MODELOS.

CREATE TABLE marcas (
    id_marca INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50)
);

CREATE TABLE modelos (
    id_modelo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50),
    id_marca INT,
    FOREIGN KEY (id_marca) REFERENCES marcas(id_marca)
);

-- ------------------------------------------------------
-- EL "TRUCO FINAL": Preservación de Historial
-- ------------------------------------------------------
-- ¿Qué pasa si el precio de la pantalla sube hoy?
-- NO queremos que cambie el precio de la Orden 101 de la semana pasada.

CREATE TABLE orden_detalle_repuestos (
    nro_orden INT,
    id_repuesto INT,
    precio_cobrado DECIMAL(10,2), -- <-- AQUÍ ESTÁ EL SECRETO
    cantidad INT,
    PRIMARY KEY (nro_orden, id_repuesto)
);
