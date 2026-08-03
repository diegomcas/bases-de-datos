-- =====================================================================
--  BIBLIOTECA MUNICIPAL - Datos
--  Caso de estudio del examen de SQL (DML + Agrupación)
-- =====================================================================
--  Requisito previo: Biblioteca.sql ya ejecutado.
--
--  Estos son EXACTAMENTE los datos que figuran impresos en la primera
--  hoja del examen. Los IDs se fuerzan a propósito para que coincidan
--  con los del enunciado.
--
--  >>> CASOS SEMBRADOS A PROPÓSITO - NO "COMPLETAR" <<<
--    - Minotauro es la única editorial SIN libros.
--    - El túnel y Pedro Páramo son los únicos libros NUNCA prestados.
--    - Los socios 6, 7 y 8 no tienen ningún préstamo.
--    - Laura Giménez está cargada dos veces (ids 1 y 5): es el duplicado
--      real. Sosa y Giménez se repiten como apellido en personas
--      distintas: son los falsos positivos.
--    - 6 préstamos tienen fecha_devolucion en NULL (siguen prestados).
--    - La ciudad y los perros cuesta exactamente $9.000, que es el
--      extremo del rango de la pregunta 2.
-- =====================================================================

USE `biblioteca`;

-- ---------------------------------------------------------------------
-- 1. EDITORIALES
-- ---------------------------------------------------------------------
INSERT INTO `editorial` (`id_editorial`, `nombre`) VALUES
(1, 'Sudamericana'),
(2, 'Planeta'),
(3, 'Anagrama'),
(4, 'Siglo XXI'),
(5, 'Minotauro');   -- sin libros, a propósito

-- ---------------------------------------------------------------------
-- 2. SOCIOS
-- ---------------------------------------------------------------------
INSERT INTO `socio` (`id_socio`, `nombre`, `apellido`, `ciudad`, `fecha_alta`) VALUES
(1, 'Laura',  'Giménez', 'Rosario', '2024-03-10'),
(2, 'Marcos', 'Ferrari', 'Rosario', '2024-05-22'),
(3, 'Ana',    'Giménez', 'Funes',   '2025-01-15'),
(4, 'Pablo',  'Sosa',    'Rosario', '2025-02-03'),
(5, 'Laura',  'Giménez', 'Rosario', '2025-06-18'),  -- homónima exacta de la 1
(6, 'Julián', 'Ortiz',   'Funes',   '2025-07-01'),  -- sin préstamos
(7, 'Carla',  'Sosa',    'Roldán',  '2025-08-12'),  -- sin préstamos
(8, 'Diego',  'Ramos',   'Rosario', '2025-09-05');  -- sin préstamos

-- ---------------------------------------------------------------------
-- 3. LIBROS
-- ---------------------------------------------------------------------
INSERT INTO `libro` (`id_libro`, `titulo`, `id_editorial`, `anio`, `precio`, `stock`) VALUES
(1,  'Rayuela',                 1, 1963,  8500.00, 3),
(2,  'Ficciones',               1, 1944,  6200.00, 5),
(3,  'El Aleph',                1, 1949,  5800.00, 0),
(4,  'La ciudad y los perros',  2, 1963,  9000.00, 2),
(5,  'Cien años de soledad',    2, 1967, 12400.00, 4),
(6,  'Los detectives salvajes', 3, 1998, 15300.00, 1),
(7,  'Nocturno de Chile',       3, 2000,  7400.00, 6),
(8,  'El túnel',                1, 1948,  4900.00, 8),   -- nunca prestado
(9,  'Pedro Páramo',            4, 1955,  5200.00, 0),   -- nunca prestado
(10, 'Boquitas pintadas',       2, 1969,  6800.00, 2);

-- ---------------------------------------------------------------------
-- 4. PRÉSTAMOS
--    Distribución buscada:
--      socio 1 -> 4 préstamos    socio 2 -> 3    socio 3 -> 3
--      socio 4 -> 2              socio 5 -> 2    socios 6, 7 y 8 -> 0
--    Libro más prestado: Cien años de soledad (4 veces).
-- ---------------------------------------------------------------------
INSERT INTO `prestamo` (`id_prestamo`, `id_socio`, `id_libro`, `fecha_prestamo`, `fecha_devolucion`) VALUES
(1,  1,  1, '2025-03-02', '2025-03-16'),
(2,  1,  5, '2025-04-10', '2025-04-25'),
(3,  1,  2, '2025-06-01', NULL),
(4,  2,  3, '2025-03-15', '2025-03-30'),
(5,  2,  5, '2025-07-20', NULL),
(6,  3,  4, '2025-04-05', '2025-04-19'),
(7,  3,  1, '2025-08-11', '2025-08-30'),
(8,  4,  7, '2025-05-06', NULL),
(9,  5,  6, '2025-09-02', '2025-09-20'),
(10, 5,  5, '2025-09-15', NULL),
(11, 1, 10, '2025-10-01', '2025-10-14'),
(12, 2,  1, '2025-10-05', NULL),
(13, 3,  5, '2025-11-02', '2025-11-16'),
(14, 4,  2, '2025-11-20', NULL);

-- =====================================================================
--  VERIFICACIÓN
--  Los cuatro números tienen que dar exactos. Si no coinciden, la base
--  no quedó bien cargada y los resultados del examen no van a dar.
-- =====================================================================
SELECT 'editoriales' AS tabla, COUNT(*) AS filas,  5 AS esperado FROM `editorial`
UNION ALL SELECT 'socios',     COUNT(*),  8 FROM `socio`
UNION ALL SELECT 'libros',     COUNT(*), 10 FROM `libro`
UNION ALL SELECT 'prestamos',  COUNT(*), 14 FROM `prestamo`;
