-- =====================================================================
--  EL CHIP - Datos adicionales para el COMPENDIO DE SUBCONSULTAS
-- =====================================================================
--  Requisitos previos: ElChip.sql y poblar_elchip.sql ya ejecutados.
--
--  Este script es ADITIVO: no modifica ni borra ninguna fila existente.
--
--  >>> NINGUN INSERT FUERZA UN ID <<<
--  Todas las PK autoincrementales se dejan que las asigne el motor, y
--  las claves foraneas se resuelven de dos maneras:
--    a) los registros PREEXISTENTES se buscan por su clave natural
--       (nro_serie, usuario, email, nombre de marca/estado/metodo);
--    b) los registros que crea este mismo script capturan su id con
--       LAST_INSERT_ID() en variables de sesion (@cli_..., @eq_..., etc.).
--  Asi el script funciona aunque la base ya haya sido tocada en clase,
--  aunque falten IDs por borrados previos o aunque los contadores
--  AUTO_INCREMENT esten adelantados.
--
--  >>> ATENCION DOCENTE <<<
--  Ejecutar DESPUES de haber dado los Talleres 1, 2 y 3, que estan
--  calibrados sobre el dataset chico. El COMPENDIO esta calibrado sobre
--  la base YA AMPLIADA. Al final hay un bloque de REVERSION comentado.
--
--  Ejecutar como UN SOLO SCRIPT en UNA SOLA SESION: las variables
--  @nombre no sobreviven a una reconexion.
-- =====================================================================

USE `el_chip`;

-- ---------------------------------------------------------------------
-- 0. GUARDA CONTRA DOBLE EJECUCION
--    Si el script ya se corrio, el INSERT de abajo falla con
--    "ERROR 1062 (23000): Duplicate entry 'compendio_subconsultas'"
--    y hay que detener la ejecucion: los datos ya estan cargados.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `_carga_compendio` (
  `marca`     VARCHAR(50) NOT NULL PRIMARY KEY,
  `ejecutado` DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB;

INSERT INTO `_carga_compendio` (`marca`) VALUES ('compendio_subconsultas');

-- ---------------------------------------------------------------------
-- 1. ANCLAS A DATOS PREEXISTENTES
--    Se resuelven por clave natural, nunca por ID literal.
--    Los emails y los nro_serie se usan como ancla porque no llevan
--    acentos: asi el script no depende del charset del cliente.
--    IMPORTANTE: los clientes se capturan ANTES de insertar al homonimo.
-- ---------------------------------------------------------------------
SET @cli_perez  = (SELECT MIN(id_cliente) FROM `email` WHERE `email` = 'juan.perez@email.com');
SET @cli_garcia = (SELECT MIN(id_cliente) FROM `email` WHERE `email` = 'm.garcia@gmail.com');

SET @emp_juan = (SELECT id_empleado FROM `empleado` WHERE usuario = 'tecnico_juan');
SET @emp_ana  = (SELECT id_empleado FROM `empleado` WHERE usuario = 'tecnico_ana');

SET @est_pendiente  = (SELECT id_orden_estado FROM `orden_estado` WHERE nombre = 'Pendiente');
SET @est_reparado   = (SELECT id_orden_estado FROM `orden_estado` WHERE nombre = 'Reparado');
SET @est_entregado  = (SELECT id_orden_estado FROM `orden_estado` WHERE nombre = 'Entregado');
SET @est_abandonado = (SELECT id_orden_estado FROM `orden_estado` WHERE nombre = 'Abandonado');

SET @mp_efectivo  = (SELECT id_metodo_pago FROM `metodo_pago` WHERE nombre = 'Efectivo');
SET @mp_tarjeta   = (SELECT id_metodo_pago FROM `metodo_pago` WHERE nombre = 'Tarjeta');
SET @mp_transfer  = (SELECT id_metodo_pago FROM `metodo_pago` WHERE nombre = 'Transferencia');
SET @mp_billetera = (SELECT id_metodo_pago FROM `metodo_pago` WHERE nombre = 'Billetera Virtual');

SET @marca_samsung = (SELECT id_marca FROM `marca` WHERE nombre = 'Samsung');
SET @marca_apple   = (SELECT id_marca FROM `marca` WHERE nombre = 'Apple');
SET @marca_lenovo  = (SELECT id_marca FROM `marca` WHERE nombre = 'Lenovo');

SET @tel_celular = (SELECT id_telefonotipo FROM `telefonotipo` WHERE tipo = 'Celular');
SET @mail_pers   = (SELECT id_emailtipo    FROM `emailtipo`    WHERE tipo = 'Personal');

-- Problemas: se buscan con LIKE para no depender de los acentos.
SET @prob_pantalla = (SELECT MIN(id_problema) FROM `problema` WHERE descripcion LIKE 'Pantalla rota%');
SET @prob_bateria  = (SELECT MIN(id_problema) FROM `problema` WHERE descripcion LIKE 'Bater%agotada%');
SET @prob_pin      = (SELECT MIN(id_problema) FROM `problema` WHERE descripcion LIKE 'Pin de carga%');
SET @prob_limpieza = (SELECT MIN(id_problema) FROM `problema` WHERE descripcion LIKE 'Limpieza%');
SET @prob_software = (SELECT MIN(id_problema) FROM `problema` WHERE descripcion LIKE 'Error de Software%');

-- Equipos preexistentes que vuelven a entrar al taller, por nro_serie (UNIQUE).
SET @eq_tab     = (SELECT id_equipo FROM `equipo` WHERE nro_serie = 'LEN-TAB-5544');
SET @eq_edge30  = (SELECT id_equipo FROM `equipo` WHERE nro_serie = 'MOT-E30-7766');

-- Chequeo: si alguna de estas anclas es NULL, el dataset base no esta
-- completo y los INSERT siguientes van a fallar por clave foranea.
SELECT
    CASE WHEN @cli_perez IS NULL OR @cli_garcia IS NULL OR @emp_juan IS NULL
           OR @emp_ana IS NULL OR @est_pendiente IS NULL OR @mp_efectivo IS NULL
           OR @marca_samsung IS NULL OR @marca_apple IS NULL OR @marca_lenovo IS NULL
           OR @prob_pantalla IS NULL OR @prob_bateria IS NULL OR @prob_pin IS NULL
           OR @prob_limpieza IS NULL OR @prob_software IS NULL
           OR @eq_tab IS NULL OR @eq_edge30 IS NULL
         THEN 'ERROR: faltan datos de poblar_elchip.sql. NO CONTINUAR.'
         ELSE 'OK: dataset base completo, se puede continuar.'
    END AS estado_previo;

-- ---------------------------------------------------------------------
-- 2. METODOS DE PAGO SIN USO
--    Casos negativos para los retos de EXISTS / NOT EXISTS: quedan
--    cargados como opcion pero jamas aparecen en orden_servicio_pago.
--    El WHERE NOT EXISTS evita chocar con el indice UNIQUE del nombre.
-- ---------------------------------------------------------------------
INSERT INTO `metodo_pago` (`nombre`)
SELECT 'Cheque' FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM `metodo_pago` WHERE nombre = 'Cheque');

INSERT INTO `metodo_pago` (`nombre`)
SELECT 'Crédito en cuenta' FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM `metodo_pago` WHERE nombre = 'Crédito en cuenta');

-- ---------------------------------------------------------------------
-- 3. REPUESTOS
--    Dispersan precios y stocks para que AVG, > ALL y > ANY discriminen.
--    El "Módulo Google Pixel 7" es intencional: existe el repuesto de la
--    marca pero NO hay ningun equipo Google (eso mantiene vivos los
--    retos de marcas sin equipos). Ninguno se referencia despues, asi
--    que no hace falta capturar sus IDs.
-- ---------------------------------------------------------------------
INSERT INTO `repuesto` (`nombre`, `stock`, `precio_unitario`) VALUES
('Flex de carga Xiaomi',       15,  2200.00),
('Vidrio templado universal', 100,   800.00),
('Módulo Google Pixel 7',       1, 38000.00);

-- ---------------------------------------------------------------------
-- 4. CLIENTES
--    Uno por vez, capturando el id que asigno el motor.
--    - homonimo EXACTO de Juan Perez -> deteccion de duplicados.
--    - Sofia Rossi: mismo apellido que Diego Rossi, distinto nombre.
--    - Marcos Ferreyra: sin telefono, sin email y sin ordenes.
-- ---------------------------------------------------------------------
INSERT INTO `cliente` (`nombre`, `apellido`) VALUES ('Juan', 'Pérez');
SET @cli_perez2 = LAST_INSERT_ID();

INSERT INTO `cliente` (`nombre`, `apellido`) VALUES ('Sofía', 'Rossi');
SET @cli_sofia = LAST_INSERT_ID();

INSERT INTO `cliente` (`nombre`, `apellido`) VALUES ('Marcos', 'Ferreyra');
SET @cli_ferreyra = LAST_INSERT_ID();

-- ---------------------------------------------------------------------
-- 5. CONTACTOS (repartidos desigualmente a proposito)
--    - Perez (2do): telefono Y email.
--    - Sofia Rossi: telefono, SIN email -> aparece en "sin email" pero
--      NO en "sin ningun contacto". Es el distractor del reto 8.1.
--    - Ferreyra y Diego Rossi: nada.
-- ---------------------------------------------------------------------
INSERT INTO `telefono` (`numero`, `descripcion`, `id_telefonotipo`, `id_cliente`) VALUES
('3415557788', 'Celular Juan P. (2)', @tel_celular, @cli_perez2),
('3415551122', 'Celular Sofía',       @tel_celular, @cli_sofia);

INSERT INTO `email` (`email`, `id_emailtipo`, `id_cliente`) VALUES
('juanperez2@email.com', @mail_pers, @cli_perez2);

-- ---------------------------------------------------------------------
-- 6. EQUIPOS
--    - iPhone 13 (2do): gemelo exacto en (tipo, marca) del iPhone
--      original -> hace funcionar los retos de subconsulta DE FILA.
--    - Galaxy A54: gemelo del Galaxy S21.
--    - iPad Air: Apple pero Tablet -> contraejemplo, coincide en marca
--      y NO en tipo. Existe para que el error se pueda cometer.
--    - IdeaPad 3: tipo nuevo 'Notebook'.
--    Ninguno usa Google ni Sony: esas marcas siguen sin equipos.
-- ---------------------------------------------------------------------
INSERT INTO `equipo` (`tipo`, `id_marca`, `modelo`, `nro_serie`) VALUES
('Celular', @marca_apple, 'iPhone 13', 'IPH13-445566');
SET @eq_iphone2 = LAST_INSERT_ID();

INSERT INTO `equipo` (`tipo`, `id_marca`, `modelo`, `nro_serie`) VALUES
('Celular', @marca_samsung, 'Galaxy A54', 'SAM-A54-334455');
SET @eq_a54 = LAST_INSERT_ID();

INSERT INTO `equipo` (`tipo`, `id_marca`, `modelo`, `nro_serie`) VALUES
('Tablet', @marca_apple, 'iPad Air', 'IPAD-778899');
SET @eq_ipad = LAST_INSERT_ID();

INSERT INTO `equipo` (`tipo`, `id_marca`, `modelo`, `nro_serie`) VALUES
('Notebook', @marca_lenovo, 'IdeaPad 3', 'LEN-IP3-2211');
SET @eq_ideapad = LAST_INSERT_ID();

-- ---------------------------------------------------------------------
-- 7. ORDENES DE SERVICIO
--    Distribucion buscada de ordenes por cliente:
--      Perez (1ro) -> 3      Garcia -> 2
--      Rossi D., Perez (2do), Sofia -> 1 c/u
--      Lopez, Martinez, Ferreyra -> 0  (casos negativos)
--    Las ordenes @ord_pendiente y la original sin pagos quedan SIN
--    PAGOS a proposito: son las que hacen que SUM() devuelva NULL.
-- ---------------------------------------------------------------------
INSERT INTO `orden_servicio`
    (`fecha_ingreso`, `id_empleado`, `id_cliente`, `id_orden_estado`, `total`) VALUES
    ('2026-05-15 09:20:00', @emp_juan, @cli_perez, @est_reparado, 18500.00);
SET @ord_4 = LAST_INSERT_ID();

INSERT INTO `orden_servicio`
    (`fecha_ingreso`, `id_empleado`, `id_cliente`, `id_orden_estado`, `total`) VALUES
    ('2026-05-20 16:40:00', @emp_ana, @cli_perez, @est_entregado, 27000.00);
SET @ord_5 = LAST_INSERT_ID();

INSERT INTO `orden_servicio`
    (`fecha_ingreso`, `id_empleado`, `id_cliente`, `id_orden_estado`, `total`) VALUES
    ('2026-05-22 11:05:00', @emp_juan, @cli_garcia, @est_entregado, 20000.00);
SET @ord_6 = LAST_INSERT_ID();

INSERT INTO `orden_servicio`
    (`fecha_ingreso`, `id_empleado`, `id_cliente`, `id_orden_estado`, `total`) VALUES
    ('2026-06-01 10:15:00', @emp_ana, @cli_perez2, @est_pendiente, 0.00);
SET @ord_7 = LAST_INSERT_ID();

INSERT INTO `orden_servicio`
    (`fecha_ingreso`, `id_empleado`, `id_cliente`, `id_orden_estado`, `total`) VALUES
    ('2026-03-10 15:30:00', @emp_juan, @cli_sofia, @est_abandonado, 9000.00);
SET @ord_8 = LAST_INSERT_ID();

-- ---------------------------------------------------------------------
-- 8. PAGOS
--    Clave para el reto de DIVISION RELACIONAL. Los metodos usados en
--    la orden 1 (la original) son {Efectivo, Tarjeta}:
--      Perez (1ro) usa {Efectivo, Tarjeta, Billetera} -> cubre  SI
--      Garcia      usa {Efectivo, Tarjeta, Transfer.} -> cubre  SI
--      Sofia       usa {Efectivo, Transferencia}      -> falta Tarjeta
--    Total general: 10 pagos, $168.500.
-- ---------------------------------------------------------------------
INSERT INTO `orden_servicio_pago` (`nro_orden`, `id_metodo_pago`, `monto`, `fecha_pago`) VALUES
(@ord_4, @mp_efectivo,  10000.00, '2026-05-15 18:00:00'),
(@ord_4, @mp_billetera,  8500.00, '2026-05-15 18:05:00'),
(@ord_5, @mp_tarjeta,   27000.00, '2026-05-20 17:30:00'),
(@ord_6, @mp_efectivo,  15000.00, '2026-05-22 12:00:00'),
(@ord_6, @mp_tarjeta,    5000.00, '2026-05-22 12:02:00'),
(@ord_8, @mp_efectivo,   4000.00, '2026-03-10 16:00:00'),
(@ord_8, @mp_transfer,   5000.00, '2026-03-11 09:00:00');

-- ---------------------------------------------------------------------
-- 9. DETALLE ORDEN - EQUIPO - PROBLEMA
--    Dos cosas deliberadas:
--    a) @ord_5 repite el mismo equipo con DOS problemas distintos:
--       demuestra por que una subconsulta que devuelve "el equipo de una
--       orden" puede NO ser escalar (y por que el LIMIT 1 miente).
--    b) El par (Tab P11, bateria) aparece en @ord_4 y @ord_6: es el
--       unico par repetido y es lo que hace que el reto de IN
--       multicolumna devuelva filas. Lectura de negocio: el equipo
--       volvio al taller por la misma falla.
--    El problema "Camara no enfoca" queda sin usar a proposito.
-- ---------------------------------------------------------------------
INSERT INTO `orden_servicio_has_equipo` (`nro_orden`, `id_equipo`, `id_problema`) VALUES
(@ord_4, @eq_tab,      @prob_bateria),
(@ord_4, @eq_tab,      @prob_limpieza),
(@ord_5, @eq_edge30,   @prob_pantalla),
(@ord_5, @eq_edge30,   @prob_pin),
(@ord_6, @eq_iphone2,  @prob_software),
(@ord_6, @eq_tab,      @prob_bateria),
(@ord_7, @eq_a54,      @prob_limpieza),
(@ord_8, @eq_ideapad,  @prob_software);

-- =====================================================================
--  VERIFICACION
-- =====================================================================
SELECT 'clientes' AS tabla, COUNT(*) AS filas, 8 AS esperado FROM `cliente`
UNION ALL SELECT 'equipos',         COUNT(*),  9 FROM `equipo`
UNION ALL SELECT 'repuestos',       COUNT(*),  9 FROM `repuesto`
UNION ALL SELECT 'metodos_pago',    COUNT(*),  6 FROM `metodo_pago`
UNION ALL SELECT 'ordenes',         COUNT(*),  8 FROM `orden_servicio`
UNION ALL SELECT 'pagos',           COUNT(*), 10 FROM `orden_servicio_pago`
UNION ALL SELECT 'detalle_ordenes', COUNT(*), 11 FROM `orden_servicio_has_equipo`
UNION ALL SELECT 'telefonos',       COUNT(*),  6 FROM `telefono`
UNION ALL SELECT 'emails',          COUNT(*),  5 FROM `email`;

-- Los IDs reales que quedaron asignados. Sobre una base virgen coinciden
-- con los que documentan las Resoluciones (clientes 6-8, equipos 6-9,
-- ordenes 4-8); si la base ya habia sido tocada seran otros y hay que
-- leer las guias por nombre, no por numero.
SELECT @cli_perez2 AS cli_perez_2do, @cli_sofia AS cli_sofia,
       @cli_ferreyra AS cli_ferreyra, @ord_4 AS orden_a, @ord_8 AS orden_e,
       @eq_iphone2 AS eq_iphone_2do, @eq_ideapad AS eq_ideapad;

-- =====================================================================
--  REVERSION - volver al dataset de poblar_elchip.sql
--  Descomentar y ejecutar EN ESTE ORDEN, en la MISMA sesion que la
--  carga (usa las variables). Si ya cerraste la sesion, borra por clave
--  natural con las consultas alternativas de mas abajo.
-- =====================================================================
-- DELETE FROM `orden_servicio_has_equipo` WHERE nro_orden IN (@ord_4,@ord_5,@ord_6,@ord_7,@ord_8);
-- DELETE FROM `orden_servicio_pago`       WHERE nro_orden IN (@ord_4,@ord_5,@ord_6,@ord_7,@ord_8);
-- DELETE FROM `orden_servicio`            WHERE nro_orden IN (@ord_4,@ord_5,@ord_6,@ord_7,@ord_8);
-- DELETE FROM `email`                     WHERE id_cliente IN (@cli_perez2,@cli_sofia,@cli_ferreyra);
-- DELETE FROM `telefono`                  WHERE id_cliente IN (@cli_perez2,@cli_sofia,@cli_ferreyra);
-- DELETE FROM `equipo`                    WHERE id_equipo IN (@eq_iphone2,@eq_a54,@eq_ipad,@eq_ideapad);
-- DELETE FROM `cliente`                   WHERE id_cliente IN (@cli_perez2,@cli_sofia,@cli_ferreyra);
-- DELETE FROM `repuesto`                  WHERE nombre IN ('Flex de carga Xiaomi','Vidrio templado universal','Módulo Google Pixel 7');
-- DELETE FROM `metodo_pago`               WHERE nombre IN ('Cheque','Crédito en cuenta');
-- DROP TABLE `_carga_compendio`;

--  Reversion sin variables (sesion nueva). Anclas por clave natural:
-- SET @r_eq = (SELECT GROUP_CONCAT(id_equipo) FROM equipo WHERE nro_serie IN
--              ('IPH13-445566','SAM-A54-334455','IPAD-778899','LEN-IP3-2211'));
-- DELETE FROM orden_servicio_has_equipo WHERE nro_orden IN
--        (SELECT nro_orden FROM orden_servicio WHERE fecha_ingreso IN
--         ('2026-05-15 09:20:00','2026-05-20 16:40:00','2026-05-22 11:05:00',
--          '2026-06-01 10:15:00','2026-03-10 15:30:00'));
-- ... (mismo criterio para pagos y ordenes, luego contactos, equipos y clientes)
