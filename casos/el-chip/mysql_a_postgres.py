#!/usr/bin/env python3
"""
Traduce el modelo de El Chip de MySQL a PostgreSQL para la consola web.

El original sigue siendo ElChip.sql. Este script no lo toca: genera
assets/consola/elchip.js, que es lo que carga consola.html. Si cambiás el
modelo, volvé a correrlo y no quedan dos verdades.

    python casos/el-chip/mysql_a_postgres.py

Lo unico que no se traduce solo es la vista orden_servicio_completa: usa
GROUP_CONCAT con SEPARATOR y un GROUP BY que Postgres no acepta. Esta
portada a mano mas abajo, con el motivo escrito al lado.
"""

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CASO = RAIZ / "casos" / "el-chip"
SALIDA = RAIZ / "assets" / "consola" / "elchip.js"

# ---------------------------------------------------------------------------
# Los INSERT del compendio se apoyan en variables de sesion y LAST_INSERT_ID().
# En la consola la base siempre arranca virgen, asi que los ids son los mismos
# que documentan las Resoluciones: clientes 6-8, equipos 6-9, ordenes 4-8.
# Resolverlos a literales evita tener que emular las variables de MySQL.
# ---------------------------------------------------------------------------
VARIABLES = {
    "cli_perez": 1, "cli_garcia": 2,
    "emp_juan": 2, "emp_ana": 3,
    "est_pendiente": 1, "est_reparado": 2, "est_entregado": 3, "est_abandonado": 4,
    "mp_efectivo": 1, "mp_tarjeta": 2, "mp_transfer": 3, "mp_billetera": 4,
    "marca_samsung": 1, "marca_apple": 2, "marca_lenovo": 3,
    "tel_celular": 1, "mail_pers": 1,
    "prob_pantalla": 1, "prob_bateria": 2, "prob_pin": 3,
    "prob_limpieza": 4, "prob_software": 5,
    "eq_tab": 3, "eq_edge30": 4,
    # Los que crea el propio compendio, en orden de insercion.
    "cli_perez2": 6, "cli_sofia": 7, "cli_ferreyra": 8,
    "eq_iphone2": 6, "eq_a54": 7, "eq_ipad": 8, "eq_ideapad": 9,
    "ord_4": 4, "ord_5": 5, "ord_6": 6, "ord_7": 7, "ord_8": 8,
}

VISTA_POSTGRES = """
-- Portada a mano: GROUP_CONCAT(... SEPARATOR x) es STRING_AGG(..., x), y
-- Postgres exige en el GROUP BY toda columna de OTRA tabla que se proyecte.
CREATE VIEW orden_servicio_completa AS
SELECT
    O.nro_orden                               AS "Nro Orden",
    CONCAT(C.apellido, ', ', C.nombre)        AS "Cliente",
    STRING_AGG(DISTINCT M.nombre, ' / ')      AS "Marcas",
    STRING_AGG(DISTINCT E.modelo, ' / ')      AS "Modelos",
    STRING_AGG(DISTINCT P.descripcion, ' + ') AS "Problemas Detectados",
    O.fecha_ingreso                           AS "Fecha Ingreso",
    ST.nombre                                 AS "Estado Actual",
    STRING_AGG(DISTINCT MP.nombre, ' + ')     AS "Metodos de Pago",
    O.total                                   AS "Monto Total"
FROM orden_servicio AS O
INNER JOIN cliente AS C ON C.id_cliente = O.id_cliente
INNER JOIN orden_servicio_has_equipo AS OSE ON OSE.nro_orden = O.nro_orden
INNER JOIN equipo AS E ON E.id_equipo = OSE.id_equipo
INNER JOIN marca AS M ON M.id_marca = E.id_marca
INNER JOIN problema AS P ON P.id_problema = OSE.id_problema
INNER JOIN orden_estado AS ST ON ST.id_orden_estado = O.id_orden_estado
LEFT JOIN orden_servicio_pago AS OSP ON OSP.nro_orden = O.nro_orden
LEFT JOIN metodo_pago AS MP ON MP.id_metodo_pago = OSP.id_metodo_pago
GROUP BY O.nro_orden, C.apellido, C.nombre, O.fecha_ingreso, ST.nombre, O.total;
"""

# ---------------------------------------------------------------------------
# Capa de compatibilidad: funciones de MySQL que no existen en Postgres.
# Van en el esquema public para que se encuentren siempre.
# Lo que no se puede definir como funcion (SHOW, DESCRIBE, la coma invertida)
# lo traduce consola.html antes de mandar la consulta.
# ---------------------------------------------------------------------------
COMPATIBILIDAD = r"""
-- IFNULL: en Postgres es COALESCE.
CREATE FUNCTION ifnull(a anyelement, b anyelement) RETURNS anyelement
  AS 'SELECT COALESCE(a, b)' LANGUAGE sql IMMUTABLE;

-- GROUP_CONCAT: en Postgres es STRING_AGG. Se define como agregado propio
-- para que DISTINCT siga funcionando igual que en MySQL.
CREATE FUNCTION _gc_paso(acumulado text, valor text) RETURNS text AS $$
  SELECT CASE
    WHEN acumulado IS NULL THEN valor
    WHEN valor IS NULL THEN acumulado
    ELSE acumulado || ',' || valor
  END
$$ LANGUAGE sql IMMUTABLE;

CREATE AGGREGATE group_concat(text) (SFUNC = _gc_paso, STYPE = text);

-- La forma con separador: GROUP_CONCAT(x SEPARATOR ' / ') llega acá como
-- GROUP_CONCAT(x, ' / '). El estado lleva el texto acumulado y el separador.
CREATE FUNCTION _gc_paso_sep(acumulado text[], valor text, sep text) RETURNS text[] AS $$
  SELECT ARRAY[
    CASE
      WHEN valor IS NULL THEN acumulado[1]
      WHEN acumulado IS NULL OR acumulado[1] IS NULL THEN valor
      ELSE acumulado[1] || sep || valor
    END,
    sep]
$$ LANGUAGE sql IMMUTABLE;

CREATE FUNCTION _gc_cierre(acumulado text[]) RETURNS text
  AS 'SELECT acumulado[1]' LANGUAGE sql IMMUTABLE;

CREATE AGGREGATE group_concat(text, text) (
  SFUNC = _gc_paso_sep, STYPE = text[], FINALFUNC = _gc_cierre);

-- Fechas y horas.
CREATE FUNCTION curdate() RETURNS date AS 'SELECT CURRENT_DATE' LANGUAGE sql STABLE;
CREATE FUNCTION curtime() RETURNS time AS 'SELECT CURRENT_TIME::time' LANGUAGE sql STABLE;
CREATE FUNCTION year(t timestamp)  RETURNS int AS 'SELECT EXTRACT(YEAR FROM t)::int'  LANGUAGE sql IMMUTABLE;
CREATE FUNCTION month(t timestamp) RETURNS int AS 'SELECT EXTRACT(MONTH FROM t)::int' LANGUAGE sql IMMUTABLE;
CREATE FUNCTION day(t timestamp)   RETURNS int AS 'SELECT EXTRACT(DAY FROM t)::int'   LANGUAGE sql IMMUTABLE;
CREATE FUNCTION datediff(a timestamp, b timestamp) RETURNS int
  AS 'SELECT (a::date - b::date)' LANGUAGE sql IMMUTABLE;

-- NOW() devuelve timestamptz y las columnas del modelo son timestamp: sin
-- estas variantes, DATEDIFF(NOW(), fecha_ingreso) no encuentra la funcion.
CREATE FUNCTION datediff(a timestamptz, b timestamp) RETURNS int
  AS 'SELECT (a::date - b::date)' LANGUAGE sql STABLE;
CREATE FUNCTION datediff(a timestamptz, b timestamptz) RETURNS int
  AS 'SELECT (a::date - b::date)' LANGUAGE sql STABLE;
CREATE FUNCTION year(t timestamptz)  RETURNS int AS 'SELECT EXTRACT(YEAR FROM t)::int'  LANGUAGE sql STABLE;
CREATE FUNCTION month(t timestamptz) RETURNS int AS 'SELECT EXTRACT(MONTH FROM t)::int' LANGUAGE sql STABLE;
CREATE FUNCTION day(t timestamptz)   RETURNS int AS 'SELECT EXTRACT(DAY FROM t)::int'   LANGUAGE sql STABLE;

-- DATE_FORMAT: se traduce el patron de MySQL al de to_char.
CREATE FUNCTION date_format(t timestamp, patron text) RETURNS text AS $$
  SELECT to_char(t, replace(replace(replace(replace(replace(replace(
         replace(replace(replace(patron,
         '%Y','YYYY'), '%y','YY'),  '%m','MM'),  '%d','DD'),
         '%H','HH24'), '%i','MI'),  '%s','SS'),  '%M','Month'), '%W','Day'))
$$ LANGUAGE sql IMMUTABLE;

CREATE FUNCTION date_format(t timestamptz, patron text) RETURNS text
  AS 'SELECT date_format(t::timestamp, patron)' LANGUAGE sql STABLE;

-- Nombres alternativos que MySQL acepta.
CREATE FUNCTION lcase(t text) RETURNS text AS 'SELECT lower(t)' LANGUAGE sql IMMUTABLE;
CREATE FUNCTION ucase(t text) RETURNS text AS 'SELECT upper(t)' LANGUAGE sql IMMUTABLE;
CREATE FUNCTION rand() RETURNS double precision AS 'SELECT random()' LANGUAGE sql VOLATILE;
"""


def convertir_ddl(sql: str) -> str:
    """MySQL Workbench -> PostgreSQL. Solo las tablas: la vista va aparte."""
    sql = sql.split("-- 3. VISTAS")[0]

    # Directivas de sesion de Workbench: no tienen equivalente ni hacen falta.
    sql = re.sub(r"^SET\s+(@OLD|SQL_MODE|FOREIGN_KEY_CHECKS|UNIQUE_CHECKS).*$",
                 "", sql, flags=re.MULTILINE)
    sql = re.sub(r"^(DROP|CREATE)\s+SCHEMA.*$", "", sql, flags=re.MULTILINE)
    sql = re.sub(r"^USE\s+`?el_chip`?\s*;.*$", "", sql, flags=re.MULTILINE)

    sql = sql.replace("`", "")
    sql = sql.replace("el_chip.", "")

    # AUTO_INCREMENT -> IDENTITY. "BY DEFAULT" y no "ALWAYS" porque los
    # scripts de carga insertan algunos ids a mano.
    sql = re.sub(r"INT\s+(UNSIGNED\s+)?NOT NULL\s+AUTO_INCREMENT",
                 "INT GENERATED BY DEFAULT AS IDENTITY", sql)
    sql = sql.replace("INT UNSIGNED", "INT")
    sql = sql.replace("DATETIME", "TIMESTAMP")
    sql = re.sub(r"\)\s*ENGINE\s*=\s*InnoDB\s*;", ");", sql)

    # UNIQUE INDEX pasa a restriccion de tabla; INDEX comun sale afuera.
    sql = re.sub(r"UNIQUE INDEX\s+\w*\s*\(\s*(\w+)\s+ASC\s*\)\s*VISIBLE",
                 r"UNIQUE (\1)", sql)

    indices = []
    tabla_actual = [None]

    def sacar_indice(linea: str) -> str:
        m = re.match(r"\s*INDEX\s+(\w+)\s*\(\s*(\w+)\s+ASC\s*\)\s*VISIBLE,?\s*$", linea)
        if m and tabla_actual[0]:
            indices.append(f"CREATE INDEX {m.group(1)} ON {tabla_actual[0]}({m.group(2)});")
            return ""
        return linea

    salida = []
    for linea in sql.split("\n"):
        m = re.match(r"\s*CREATE TABLE IF NOT EXISTS\s+(\w+)", linea)
        if m:
            tabla_actual[0] = m.group(1)
        linea = sacar_indice(linea)
        if linea != "" or (salida and salida[-1] != ""):
            salida.append(linea)
    sql = "\n".join(salida)

    # Una coma colgada antes del parentesis de cierre si el ultimo elemento
    # de la tabla era un INDEX que acabamos de sacar.
    sql = re.sub(r",(\s*)\)", r"\1)", sql)

    return sql.strip() + "\n\n" + "\n".join(indices) + "\n"


def convertir_datos(sql: str) -> str:
    """Los INSERT son casi portables: cambian las comas invertidas y poco mas."""
    sql = re.sub(r"^USE\s+`?el_chip`?\s*;.*$", "", sql, flags=re.MULTILINE)
    sql = sql.replace("`", "")
    return sql.strip() + "\n"


# Clave primaria de cada tabla que el compendio puebla capturando el id.
CLAVES = {"cliente": "id_cliente", "equipo": "id_equipo", "orden_servicio": "nro_orden"}


def fijar_ids(sql: str) -> str:
    """
    El original inserta sin id y captura el que asigno el motor con
    LAST_INSERT_ID(). Aca escribimos el id a mano, tomando el valor de
    VARIABLES: asi el compendio deja siempre los mismos numeros que citan
    las Resoluciones, aunque la base se haya tocado antes.
    """
    patron = re.compile(
        r"INSERT INTO (\w+)\s*\(([^)]*)\)\s*VALUES\s*\(([^;]*)\);\s*\n"
        r"\s*SET @(\w+)\s*=\s*LAST_INSERT_ID\(\);",
        re.MULTILINE,
    )

    def reemplazo(m):
        tabla, columnas, valores, variable = m.groups()
        clave = CLAVES.get(tabla)
        if clave is None or variable not in VARIABLES:
            raise SystemExit(f"No se como fijar el id de {tabla} (@{variable})")
        return (f"INSERT INTO {tabla} ({clave}, {columnas.strip()}) VALUES "
                f"({VARIABLES[variable]}, {valores.strip()});")

    sql, cambios = patron.subn(reemplazo, sql)
    if cambios == 0:
        raise SystemExit("No se encontro ningun INSERT con LAST_INSERT_ID()")
    return sql


def convertir_compendio(sql: str) -> str:
    """Resuelve las variables de sesion a literales y saca lo que no aplica."""
    sql = sql.split("-- =====================================================================\n--  VERIFICACION")[0]
    sql = re.sub(r"^USE\s+`?el_chip`?\s*;.*$", "", sql, flags=re.MULTILINE)
    sql = sql.replace("`", "")

    # Antes de borrar los SET, aprovecharlos para fijar los ids a mano.
    sql = fijar_ids(sql)

    # Las lineas SET @x = ... desaparecen: sus valores ya estan en VARIABLES.
    sql = re.sub(r"^SET\s+@\w+\s*=.*?;\s*$", "", sql, flags=re.MULTILINE | re.DOTALL)
    sql = re.sub(r"^SET\s+@\w+\s*=[^;]*;", "", sql, flags=re.MULTILINE | re.DOTALL)

    # El SELECT ... CASE que valida las anclas no tiene sentido acá.
    sql = re.sub(r"SELECT\s*\n\s*CASE WHEN @cli_perez.*?AS estado_previo;",
                 "", sql, flags=re.DOTALL)

    for nombre, valor in sorted(VARIABLES.items(), key=lambda x: -len(x[0])):
        sql = sql.replace(f"@{nombre}", str(valor))

    # FROM DUAL no existe en Postgres; el WHERE NOT EXISTS sigue siendo valido.
    sql = sql.replace(" FROM DUAL\n", "\n")

    sql = sql.replace("DATETIME", "TIMESTAMP")
    sql = re.sub(r"\)\s*ENGINE\s*=\s*InnoDB\s*;", ");", sql)

    # Para verificar miramos solo el SQL: los comentarios del original hablan
    # de las variables, y hay direcciones de correo que tambien llevan arroba.
    codigo = re.sub(r"--[^\n]*", "", sql)
    codigo = re.sub(r"'[^']*'", "''", codigo)
    quedan = re.findall(r"@\w+", codigo)
    if quedan:
        raise SystemExit(f"Quedaron variables sin resolver: {sorted(set(quedan))}")

    return sql.strip() + "\n"


def secuencias_al_dia() -> str:
    """Tras insertar ids a mano, los contadores quedan atrasados."""
    return """
-- Los INSERT con id explicito no mueven el contador de IDENTITY. Sin esto,
-- el primer INSERT que haga un alumno choca con una clave duplicada.
DO $$
DECLARE r record; maximo bigint;
BEGIN
  FOR r IN
    SELECT c.table_name AS t, c.column_name AS c
    FROM information_schema.columns c
    WHERE c.table_schema = 'el_chip' AND c.is_identity = 'YES'
  LOOP
    EXECUTE format('SELECT COALESCE(MAX(%I), 0) FROM %I', r.c, r.t) INTO maximo;
    EXECUTE format('ALTER TABLE %I ALTER COLUMN %I RESTART WITH %s',
                   r.t, r.c, maximo + 1);
  END LOOP;
END $$;
"""


def main() -> None:
    ddl = convertir_ddl((CASO / "ElChip.sql").read_text(encoding="utf-8"))
    base = convertir_datos((CASO / "poblar_elchip.sql").read_text(encoding="utf-8"))
    comp = convertir_compendio((CASO / "poblar_elchip_compendio.sql").read_text(encoding="utf-8"))

    esquema = (
        "CREATE SCHEMA IF NOT EXISTS el_chip;\n"
        "SET search_path TO el_chip, public;\n\n"
        + ddl + "\n" + VISTA_POSTGRES + "\n" + COMPATIBILIDAD
    )
    base = base + secuencias_al_dia()
    comp = comp + secuencias_al_dia()

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(
        "// GENERADO por casos/el-chip/mysql_a_postgres.py — no editar a mano.\n"
        "// El original del modelo es casos/el-chip/ElChip.sql.\n\n"
        f"export const ESQUEMA = {json.dumps(esquema, ensure_ascii=False)};\n\n"
        f"export const DATOS_BASE = {json.dumps(base, ensure_ascii=False)};\n\n"
        f"export const DATOS_COMPENDIO = {json.dumps(comp, ensure_ascii=False)};\n",
        encoding="utf-8",
    )

    print(f"Generado {SALIDA.relative_to(RAIZ)}")
    print(f"  esquema     {len(esquema):>7,} caracteres")
    print(f"  base        {len(base):>7,}")
    print(f"  compendio   {len(comp):>7,}")


if __name__ == "__main__":
    main()
