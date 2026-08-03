-- =====================================================================
--  BIBLIOTECA MUNICIPAL - Estructura
--  Caso de estudio del examen de SQL (DML + Agrupación)
-- =====================================================================
--  Ejecutar PRIMERO este script y DESPUÉS poblar_biblioteca.sql
--
--  ATENCIÓN: este script BORRA y vuelve a crear el esquema `biblioteca`.
--  No afecta a `el_chip` ni a ninguna otra base.
--
--  El juego de caracteres y la collation se declaran de forma explícita
--  (utf8mb4_0900_ai_ci, la de MySQL 8 por defecto) porque el examen
--  supone comparaciones de texto que IGNORAN mayúsculas y tildes.
--  Si se cambia por una collation _cs o _bin, la pregunta 7 del examen
--  pasa a tener otra respuesta.
-- =====================================================================

DROP SCHEMA IF EXISTS `biblioteca`;
CREATE SCHEMA `biblioteca`
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE `biblioteca`;

-- ---------------------------------------------------------------------
-- 1. TABLAS SIN DEPENDENCIAS
-- ---------------------------------------------------------------------

CREATE TABLE `editorial` (
  `id_editorial` INT NOT NULL AUTO_INCREMENT,
  `nombre`       VARCHAR(80) NOT NULL,
  PRIMARY KEY (`id_editorial`),
  UNIQUE INDEX `nombre_UNIQUE` (`nombre` ASC)
) ENGINE = InnoDB;

CREATE TABLE `socio` (
  `id_socio`   INT NOT NULL AUTO_INCREMENT,
  `nombre`     VARCHAR(60) NOT NULL,
  `apellido`   VARCHAR(60) NOT NULL,
  `ciudad`     VARCHAR(60) NOT NULL,
  `fecha_alta` DATE NULL,
  PRIMARY KEY (`id_socio`)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- 2. TABLAS CON CLAVES FORÁNEAS
--    Todas las FK son ON DELETE RESTRICT: no se puede borrar una fila
--    que tenga hijos. Es lo que hace fallar los borrados de la
--    pregunta 9 del examen.
-- ---------------------------------------------------------------------

CREATE TABLE `libro` (
  `id_libro`     INT NOT NULL AUTO_INCREMENT,
  `titulo`       VARCHAR(150) NOT NULL,
  `id_editorial` INT NOT NULL,
  `anio`         INT NULL,
  `precio`       DECIMAL(10,2) NOT NULL,
  `stock`        INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_libro`),
  INDEX `fk_libro_editorial_idx` (`id_editorial` ASC),
  CONSTRAINT `fk_libro_editorial`
    FOREIGN KEY (`id_editorial`)
    REFERENCES `editorial` (`id_editorial`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE `prestamo` (
  `id_prestamo`      INT NOT NULL AUTO_INCREMENT,
  `id_socio`         INT NOT NULL,
  `id_libro`         INT NOT NULL,
  `fecha_prestamo`   DATE NOT NULL,
  `fecha_devolucion` DATE NULL,
  PRIMARY KEY (`id_prestamo`),
  INDEX `fk_prestamo_socio_idx` (`id_socio` ASC),
  INDEX `fk_prestamo_libro_idx` (`id_libro` ASC),
  CONSTRAINT `fk_prestamo_socio`
    FOREIGN KEY (`id_socio`)
    REFERENCES `socio` (`id_socio`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT `fk_prestamo_libro`
    FOREIGN KEY (`id_libro`)
    REFERENCES `libro` (`id_libro`)
    ON DELETE RESTRICT
    ON UPDATE RESTRICT
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- 3. VERIFICACIÓN DE LA ESTRUCTURA
-- ---------------------------------------------------------------------
SHOW TABLES;
