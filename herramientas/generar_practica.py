#!/usr/bin/env python3
"""
Arma la práctica de los modelos de pregunta sobre El Chip.

    python herramientas/generar_practica.py
    python herramientas/generar_practica.py --mysql   # y contrasta con el motor

Escribe unidades/04-sql/practica-modelos-de-pregunta.html: ejercicios de
opción múltiple para trabajar en clase, uno por cada forma de preguntar, y
cada uno apuntado a un error que se repitió en el examen de SQL. Los que
llevan `retirado` quedan en el script y no se publican.

Ningún número de la página se escribe a mano. Cada ejercicio corre sus
consultas sobre el juego de datos ampliado —el mismo de la consola, en
assets/consola/elchip.js—, arma con eso las opciones y las tablas de la
resolución, y comprueba con un assert que la opción marcada como correcta
siga siéndolo. Si cambian los datos, el script falla en vez de publicar una
respuesta equivocada.

SQLite alcanza para armar la página sin servidor, pero el motor de los alumnos
es MySQL. Con --mysql, cada consulta que el script corrió se vuelve a correr
en un esquema de prueba (el_chip_ap_amp, que se borra al terminar) y se compara
fila por fila. Usa el login-path «prueba», igual que verificar_apunte_mysql.py.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generar_apunte as apunte  # noqa: E402  la base, el resaltado y las tablas

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "unidades" / "04-sql" / "practica-modelos-de-pregunta.html"

CON = apunte.bases()["ampliado"]
LETRAS = "abcd"
DINERO = {"total", "monto", "cobrado", "facturado", "precio_unitario"}


# ---------------------------------------------------------------------------
# Correr y mostrar
# ---------------------------------------------------------------------------

REGISTRO: dict[str, tuple] = {}   # todo lo que se corrió, para el contraste


def correr(sql: str):
    """Columnas y filas de la última sentencia que devuelve filas. Todo corre
    en una transacción que se deshace, así un UPDATE no llega al ejercicio
    siguiente."""
    if sql in REGISTRO:
        return REGISTRO[sql]
    columnas, filas = [], []
    CON.execute("BEGIN")
    try:
        for sentencia in apunte.sentencias(sql):
            paso = CON.execute(sentencia)
            if paso.description:
                columnas = [d[0] for d in paso.description]
                filas = paso.fetchall()
    finally:
        CON.rollback()
    REGISTRO[sql] = (columnas, filas)
    return columnas, filas


def cuantas(sql: str) -> int:
    return len(correr(sql)[1])


def tabla(sql: str, destacar=None, rotulo: str = "") -> str:
    """La salida de una consulta. `destacar` recibe la fila y dice si se marca."""
    columnas, filas = correr(sql)
    marcadas = {i for i, f in enumerate(filas) if destacar and destacar(dict(zip(columnas, f)))}
    cuerpo = apunte.formato_tabla(columnas, filas, DINERO, marcadas)
    cabeza = f'<p class="res-rotulo">{rotulo}</p>\n' if rotulo else ""
    return f'<div class="res-tabla">\n{cabeza}{cuerpo}\n</div>'


def plata(valor) -> str:
    return f"{valor:.2f}"


def sql_html(sql: str) -> str:
    return f'<pre class="ej-sql"><code>{apunte.resaltar(sql.strip())}</code></pre>'


def referencia(tabla_origen: str, *pares) -> str:
    """El recuadro de valores ya calculados, como en la primera hoja del examen.

    Trae varios resúmenes de la tabla y no solo el que hace falta: la cuenta
    a mano no evalúa SQL, y elegir cuál de los valores sirve, sí. Cada valor
    sale de correr su consulta."""
    items = []
    for rotulo, expresion, decimales in pares:
        valor = correr(f"SELECT {expresion} FROM {tabla_origen}")[1][0][0]
        texto = f"{valor:.2f}" if decimales else str(valor)
        items.append(f'<li><span class="ref-rot">{rotulo}</span> <strong>{texto}</strong></li>')
    return ('<div class="ej-ref">\n<p class="ref-titulo">Datos de referencia · '
            f'<code>{tabla_origen}</code></p>\n<ul>' + "".join(items) + "</ul>\n"
            '<p class="ref-nota">Se dan calculados: el ejercicio no espera que hagas la '
            "cuenta a mano.</p>\n</div>")


def variantes(*pares) -> str:
    filas = "".join(
        f'<div class="variante"><span class="variante-rot">{rot}</span>'
        f'<pre class="ej-sql"><code>{apunte.resaltar(sql.strip())}</code></pre></div>\n'
        for rot, sql in pares)
    return f'<div class="variantes">\n{filas}</div>'


# Las tablas de datos que acompañan a cada ejercicio: solo las columnas que
# el ejercicio necesita mirar.
TABLAS = {
    "cliente": "SELECT id_cliente, nombre, apellido FROM cliente ORDER BY id_cliente",
    "orden_servicio": "SELECT nro_orden, id_cliente, id_orden_estado, total, fecha_entrega "
                      "FROM orden_servicio ORDER BY nro_orden",
    "orden_servicio_pago": "SELECT nro_orden, id_metodo_pago, monto FROM orden_servicio_pago "
                           "ORDER BY nro_orden, id_metodo_pago",
    "metodo_pago": "SELECT id_metodo_pago, nombre FROM metodo_pago ORDER BY id_metodo_pago",
    "repuesto": "SELECT id_repuesto, nombre, precio_unitario FROM repuesto ORDER BY id_repuesto",
}


def datos(*nombres: str) -> str:
    bloques = []
    for nombre in nombres:
        columnas, filas = correr(TABLAS[nombre])
        cabeza = "".join(f"<th>{html.escape(c)}</th>" for c in columnas)
        cuerpo = []
        for fila in filas:
            celdas = []
            for c, v in zip(columnas, fila):
                texto = html.escape(apunte.celda(v, c, DINERO))
                clase = ' class="nulo"' if v is None else ""
                celdas.append(f"<td{clase}>{texto}</td>")
            cuerpo.append("<tr>" + "".join(celdas) + "</tr>")
        bloques.append(
            '<div class="dato">\n'
            f'<p class="dato-nombre">{nombre} · {len(filas)} filas</p>\n'
            '<div class="table-scroll"><table class="dato-tabla">\n'
            f"<thead><tr>{cabeza}</tr></thead>\n<tbody>\n" + "\n".join(cuerpo) +
            "\n</tbody></table></div>\n</div>")
    return ('<details class="ej-datos" open>\n<summary>Las tablas que usa</summary>\n'
            '<div class="datos-fila">\n' + "\n".join(bloques) + "\n</div>\n</details>")


# ---------------------------------------------------------------------------
# Los ejercicios
# ---------------------------------------------------------------------------

EJERCICIOS: list[dict] = []
RETIRADOS: list[dict] = []   # siguen corriendo sus asserts, pero no se publican

# En papel no se puede previsualizar un resultado, y un ejercicio que solo pide
# cuántas filas devuelve una consulta se vuelve una cuenta a mano. Esos quedan
# para una práctica con la consola.
SOLO_CUENTA = "pide solo cantidades de filas: sirve con la consola, no en papel"


def ejercicio(mecanica, titulo, tablas, enunciado, pregunta, opciones, correcta,
              error, resolucion, examen="", retirado="", debate="", ayuda=""):
    """`opciones` es una lista de (texto, por qué). `correcta` es el índice.
    Con `retirado` (el motivo) el ejercicio no sale en la página. `debate` es
    la consigna que el grupo discute antes de elegir, y `ayuda`, el recorrido
    por etapas que puede abrir si no avanza."""
    assert len(opciones) == 4
    # La resolución se arma acá mismo y no al escribir la página: las consultas
    # de cada ejercicio viven en variables que el ejercicio siguiente reutiliza.
    resolucion = resolucion()
    destino = RETIRADOS if retirado else EJERCICIOS
    destino.append(dict(mecanica=mecanica, titulo=titulo, tablas=tablas,
                        enunciado=enunciado, pregunta=pregunta, opciones=opciones,
                        correcta=correcta, error=error, resolucion=resolucion,
                        examen=examen, retirado=retirado, debate=debate, ayuda=ayuda))


# ── Una fila por cada qué ───────────────────────────────────────────────

Q = """
SELECT C.apellido, O.nro_orden, P.monto
FROM cliente C
JOIN orden_servicio O ON O.id_cliente = C.id_cliente
JOIN orden_servicio_pago P ON P.nro_orden = O.nro_orden
ORDER BY O.nro_orden;
"""
n_clientes = cuantas("SELECT * FROM cliente")
n_ordenes = cuantas("SELECT * FROM orden_servicio")
# sin fecha_pago: tres pagos se cargan con la hora del momento
n_pagos = cuantas("SELECT nro_orden, id_metodo_pago FROM orden_servicio_pago")
n_pagaron = cuantas("SELECT DISTINCT O.id_cliente FROM orden_servicio O "
                    "JOIN orden_servicio_pago P ON P.nro_orden = O.nro_orden")
assert cuantas(Q) == n_pagos
dobles = [f[0] for f in correr(
    "SELECT nro_orden FROM orden_servicio_pago GROUP BY nro_orden HAVING COUNT(*) > 1 "
    "ORDER BY nro_orden")[1]]
assert dobles[0] == 1
sin_pago = [f[0] for f in correr(
    "SELECT nro_orden FROM orden_servicio WHERE nro_orden NOT IN "
    "(SELECT nro_orden FROM orden_servicio_pago) ORDER BY nro_orden")[1]]

ejercicio(
    "¿Una fila por cada qué?",
    "Clientes, órdenes y pagos en una sola consulta",
    ["cliente", "orden_servicio", "orden_servicio_pago"],
    "<p>Esta consulta cruza tres tablas y muestra los pagos de las órdenes de los "
    "clientes:</p>" + sql_html(Q),
    "¿De qué hay exactamente una fila en el resultado?",
    [("Una por cada cliente",
      "El cruce no devuelve una fila por cliente. Un cliente con tres órdenes pagadas aparece "
      "varias veces, y uno sin órdenes no aparece."),
     ("Una por cada orden",
      "Sería así si la consulta terminara en <code>orden_servicio</code>. El segundo "
      "<code>JOIN</code> abre cada orden en tantas filas como pagos tenga, y deja afuera las "
      "que no tienen ninguno."),
     ("Una por cada pago registrado",
      "Hay una fila por pago. Cada una muestra además la orden y el cliente de ese pago, y "
      "por eso el cliente y la orden se repiten."),
     ("Una por cada cliente que hizo algún pago",
      f"Son {n_pagaron} los clientes distintos que aparecen, pero la consulta no los resume: "
      "cada uno figura una vez por cada pago.")],
    2,
    "Leer el resultado de un cruce como si tuviera una fila por cada registro de la primera "
    "tabla del <code>FROM</code>. El resultado tiene una fila por cada registro de la tabla "
    "más «fina» de la cadena, que acá es <code>orden_servicio_pago</code>.",
    lambda: (
        "<p>La cadena va de cliente a orden y de orden a pago. Cada <code>JOIN</code> conserva "
        "las combinaciones que encuentran pareja, así que el resultado termina con una fila "
        f"por pago: {n_pagos}. Las órdenes {' y '.join(map(str, sin_pago))} no tienen pagos y "
        "quedan afuera; la orden 1 tiene dos y aparece dos veces.</p>"
        + tabla(Q, rotulo="Lo que devuelve la consulta")),
)


# ── Recorrido por etapas ───────────────────────────────────────────────

Q = """
SELECT id_cliente, COUNT(*) AS ordenes
FROM orden_servicio
WHERE total > 0
GROUP BY id_cliente
HAVING COUNT(*) >= 2;
"""
_, ordenes = correr("SELECT nro_orden, id_cliente, total FROM orden_servicio ORDER BY nro_orden")
pasan = [o for o in ordenes if o[2] > 0]
grupos: dict[int, list] = {}
for o in pasan:
    grupos.setdefault(o[1], []).append(o)
quedan = {c: g for c, g in grupos.items() if len(g) >= 2}
# el recorrido hecho a mano tiene que coincidir con lo que dice el motor
assert len(pasan) == cuantas("SELECT * FROM orden_servicio WHERE total > 0")
assert len(grupos) == cuantas("SELECT id_cliente FROM orden_servicio WHERE total > 0 GROUP BY id_cliente")
assert sorted(quedan) == sorted(f[0] for f in correr(Q)[1])
sin_where = cuantas("SELECT id_cliente FROM orden_servicio GROUP BY id_cliente")
sin_where_fin = cuantas("SELECT id_cliente FROM orden_servicio GROUP BY id_cliente HAVING COUNT(*) >= 2")
etapas_ok = (len(pasan), len(grupos), len(quedan))
assert len(ordenes) - len(pasan) == 2 and len(ordenes) == 8


def recorrido() -> str:
    def fila(o, clase=""):
        c = f' class="{clase}"' if clase else ""
        return (f"<tr{c}><td>{o[0]}</td><td>{o[1]}</td><td>{plata(o[2])}</td></tr>")

    cab = "<thead><tr><th>nro_orden</th><th>id_cliente</th><th>total</th></tr></thead>"
    t1 = "".join(fila(o, "" if o[2] > 0 else "se-va") for o in ordenes)
    bloques = []
    for cliente, filas in sorted(grupos.items()):
        fuera = len(filas) < 2
        clase = "grupo se-va-grupo" if fuera else "grupo"
        bloques.append(
            f'<tbody class="{clase}">'
            f'<tr class="grupo-cab"><td colspan="3">id_cliente = {cliente}</td></tr>'
            + "".join(fila(o) for o in filas) +
            f'<tr class="grupo-calc"><td colspan="3"><span class="fn">COUNT(*)</span> = '
            f'{len(filas)}' + (" · no llega a 2" if fuera else " · pasa el HAVING") +
            "</td></tr></tbody>")
    return (
        '<div class="etapas">\n'
        '<div class="etapa"><p class="etapa-nombre"><span class="etapa-num">1</span> '
        f'<code>WHERE total &gt; 0</code> · quedan {len(pasan)} de {len(ordenes)} filas</p>'
        f'<table class="etapa-tabla">{cab}<tbody>{t1}</tbody></table></div>\n'
        '<div class="etapa"><p class="etapa-nombre"><span class="etapa-num">2</span> '
        f'<code>GROUP BY id_cliente</code> · {len(grupos)} grupos · '
        f'<span class="etapa-num">3</span> <code>HAVING</code> · quedan {len(quedan)}</p>'
        f'<table class="etapa-tabla">{cab}{"".join(bloques)}</table></div>\n'
        "</div>\n" + tabla(Q, rotulo="4 · Lo que devuelve la consulta"))


ejercicio(
    "Recorrido por etapas",
    "Clientes con dos órdenes o más",
    ["orden_servicio"],
    "<p>Se ejecuta:</p>" + sql_html(Q),
    "¿Cuántas filas pasan el <code>WHERE</code>, cuántos grupos arma el <code>GROUP BY</code> "
    "y cuántas filas devuelve la consulta?",
    [(f"{etapas_ok[0]} filas → {etapas_ok[1]} grupos → {etapas_ok[2]} filas",
      "El filtro de filas corre primero, los grupos se arman con lo que quedó y el "
      "<code>HAVING</code> descarta grupos."),
     (f"{len(ordenes)} filas → {sin_where} grupos → {sin_where_fin} filas",
      "Este recorrido saltea el <code>WHERE</code>: agrupa las ocho órdenes, incluidas las "
      "dos que tienen total 0."),
     (f"{etapas_ok[0]} filas → {etapas_ok[1]} grupos → {etapas_ok[1]} filas",
      "Acá falta aplicar el <code>HAVING</code>: uno de los grupos tiene una sola orden y "
      "no pasa."),
     (f"{etapas_ok[0]} filas → {etapas_ok[0]} grupos → {etapas_ok[2]} filas",
      "Un grupo junta todas las filas que comparten <code>id_cliente</code>; no hay un grupo "
      "por fila.")],
    0,
    "Mezclar los dos filtros. <code>WHERE</code> mira filas sueltas y corre antes de agrupar; "
    "<code>HAVING</code> mira grupos ya armados y corre después.",
    recorrido,
    examen="En el examen, la pregunta 9 era de este tipo y algunos respondieron como si el "
           "<code>HAVING</code> no estuviera.",
    retirado=SOLO_CUENTA,
)


# ── Del resultado a la consulta ────────────────────────────────────────

Q_I = """
SELECT M.nombre, COUNT(*) AS pagos
FROM metodo_pago M
JOIN orden_servicio_pago P ON P.id_metodo_pago = M.id_metodo_pago
GROUP BY M.id_metodo_pago, M.nombre
ORDER BY M.id_metodo_pago;
"""
Q_II = Q_I.replace("\nJOIN", "\nLEFT JOIN")
Q_III = Q_II.replace("COUNT(*)", "COUNT(P.nro_orden)")
r3 = correr(Q_III)[1]
assert len(r3) == cuantas("SELECT * FROM metodo_pago") and any(f[1] == 0 for f in r3)
assert cuantas(Q_I) < len(r3) and all(f[1] >= 1 for f in correr(Q_II)[1])
sin_uso = [f[0] for f in r3 if f[1] == 0]
assert len(r3) == 6 and len(sin_uso) == 2

ejercicio(
    "Del resultado a la consulta",
    "Cuántos pagos recibió cada método",
    ["metodo_pago", "orden_servicio_pago"],
    "<p>Una consulta devolvió este resultado:</p>"
    + tabla(Q_III, destacar=lambda f: f["pagos"] == 0)
    + "<p>Hay tres candidatas:</p>"
    + variantes(("I", Q_I), ("II", Q_II), ("III", Q_III)),
    "¿Cuál de las tres lo produjo?",
    [("La I",
      f"El <code>JOIN</code> descarta los métodos sin pagos: la I devuelve {cuantas(Q_I)} "
      "filas y en el resultado hay seis."),
     ("La II",
      "La II trae los seis métodos, pero <code>COUNT(*)</code> cuenta filas, y la fila que el "
      "<code>LEFT JOIN</code> arma para un método sin pagos también es una fila: mostraría 1."),
     ("La II y la III, que devuelven lo mismo",
      "Coinciden en los métodos que tienen pagos y difieren justo en los que no tienen: "
      "la II les pone 1 y la III les pone 0."),
     ("La III",
      "El <code>LEFT JOIN</code> conserva los seis métodos y <code>COUNT(P.nro_orden)</code> "
      "cuenta solo los valores cargados, así que un método sin pagos da 0.")],
    3,
    "Dos errores encadenados: creer que un grupo vacío aparece solo con valor 0, y creer que "
    "<code>COUNT(*)</code> sobre un <code>LEFT JOIN</code> devuelve 0 cuando no hay pareja.",
    lambda: (
        f"<p>{' y '.join(sin_uso)} no se usaron nunca. Para que aparezcan hace falta el "
        "<code>LEFT JOIN</code>, y para que muestren 0 hay que contar una columna de la tabla "
        "de la derecha, que en esas filas vale NULL.</p>"
        '<div class="res-fila">'
        + tabla(Q_I, rotulo="I · JOIN y COUNT(*)")
        + tabla(Q_II, destacar=lambda f: f["nombre"] in sin_uso, rotulo="II · LEFT JOIN y COUNT(*)")
        + tabla(Q_III, destacar=lambda f: f["nombre"] in sin_uso,
                rotulo="III · LEFT JOIN y COUNT(P.nro_orden)")
        + "</div>"),
    examen="Es el tema de las preguntas 19, 20 y 21 del examen, las de la editorial sin libros. "
           "La 20 fue una de las tres con menos aciertos.",
)


# ── Del SQL al castellano ──────────────────────────────────────────────

Q = """
SELECT id_cliente, COUNT(*) AS ordenes
FROM orden_servicio
GROUP BY id_cliente
HAVING COUNT(*) > 1;
"""
assert cuantas(Q) == 2

ejercicio(
    "Del SQL al castellano",
    "Qué pedido responde esta consulta",
    ["orden_servicio"],
    "<p>Alguien escribió esta consulta y no anotó para qué era:</p>" + sql_html(Q),
    "¿Qué pedido responde?",
    [("Las órdenes que tienen más de un cliente",
      "Los grupos son clientes, porque se agrupa por <code>id_cliente</code>. Además, en este "
      "modelo una orden tiene un solo cliente."),
     ("Los clientes que tienen más de una orden",
      "Se agrupa por cliente, se cuentan las filas de cada grupo —sus órdenes— y quedan los "
      "grupos con más de una."),
     ("Cuántas órdenes tiene cada uno de los clientes",
      "Eso es la consulta sin el <code>HAVING</code>. Con el <code>HAVING</code> ya no están "
      "todos los clientes."),
     ("Los clientes que tienen al menos una orden",
      "«Al menos una» es <code>COUNT(*) &gt;= 1</code>, que se cumple para todo grupo. "
      "La consulta pide más de una.")],
    1,
    "Leer la consulta de corrido sin identificar qué es un grupo. La pregunta que ordena la "
    "lectura es por qué columna se agrupa: eso dice de qué habla cada fila del resultado.",
    lambda: (
        "<p>Para leer una consulta con grupos conviene ir en este orden: de qué tabla salen "
        "las filas, por qué columna se agrupan, qué se calcula en cada grupo y qué grupos "
        "quedan.</p>" + tabla(Q, rotulo="Lo que devuelve")),
)


# ── Del castellano al SQL, con un hueco ────────────────────────────────

BASE5 = """
SELECT M.nombre, SUM(P.monto) AS cobrado
FROM metodo_pago M
JOIN orden_servicio_pago P ON P.id_metodo_pago = M.id_metodo_pago
GROUP BY M.id_metodo_pago, M.nombre
{hueco}
ORDER BY M.id_metodo_pago;
"""
HUECOS = ["HAVING SUM(P.monto) > 30000", "HAVING MAX(P.monto) > 30000",
          "HAVING COUNT(*) > 30000", "HAVING AVG(P.monto) > 30000"]
filas5 = [cuantas(BASE5.format(hueco=h)) for h in HUECOS]
assert filas5[0] == 3 and filas5[0] != filas5[1] and filas5[2] == filas5[3] == 0
assert correr("SELECT COUNT(*), SUM(P.monto), MAX(P.monto) FROM orden_servicio_pago P "
              "JOIN metodo_pago M ON M.id_metodo_pago = P.id_metodo_pago "
              "WHERE M.nombre = 'Efectivo'")[1][0][0] == 4

ejercicio(
    "Del castellano al SQL, con un hueco",
    "Métodos con los que se cobró más de $30.000",
    ["metodo_pago", "orden_servicio_pago"],
    "<p>Martín pide los métodos de pago con los que se cobró <strong>más de $30.000 en "
    "total</strong>. La consulta está escrita, salvo una cláusula:</p>"
    + sql_html(BASE5.format(hueco="________________________")),
    "¿Qué va en el hueco?",
    [(f"<code>{html.escape(HUECOS[0])}</code>",
      "«En total» es la suma de los montos del grupo."),
     (f"<code>{html.escape(HUECOS[1])}</code>",
      f"Eso pide que algún pago individual supere los $30.000. Devuelve {filas5[1]} métodos: "
      "deja afuera a Efectivo, que junta más de $30.000 con cuatro pagos chicos."),
     (f"<code>{html.escape(HUECOS[2])}</code>",
      "<code>COUNT(*)</code> cuenta pagos, no pesos: pediría más de 30.000 pagos por método."),
     (f"<code>{html.escape(HUECOS[3])}</code>",
      "El promedio por pago es otra medida: ningún método promedia más de $30.000 por pago.")],
    0,
    "Elegir la función de agregación por parecido y no por lo que pide el enunciado. "
    "«En total», «el más caro», «cuántos» y «en promedio» son cuatro funciones distintas.",
    lambda: (
        "<p>Las cuatro opciones corren. Cambia qué grupos pasan:</p>"
        '<div class="res-fila">'
        + "".join(tabla(BASE5.format(hueco=h), rotulo=html.escape(h)) for h in HUECOS[:2])
        + "</div>"
        f"<p>Con <code>COUNT(*)</code> y con <code>AVG</code> no pasa ningún grupo: "
        f"{filas5[2]} y {filas5[3]} filas.</p>"),
)


# ── Más, menos o igual ─────────────────────────────────────────────────

Q_J = """
SELECT C.id_cliente, C.apellido, O.nro_orden
FROM cliente C
JOIN orden_servicio O ON O.id_cliente = C.id_cliente
ORDER BY C.id_cliente, O.nro_orden;
"""
Q_L = Q_J.replace("\nJOIN", "\nLEFT JOIN")
n_j, n_l = cuantas(Q_J), cuantas(Q_L)
con_orden = cuantas("SELECT DISTINCT id_cliente FROM orden_servicio")
assert n_l == n_j + (n_clientes - con_orden)

ejercicio(
    "¿Más, menos o igual?",
    "Un JOIN que pasa a LEFT JOIN",
    ["cliente", "orden_servicio"],
    f"<p>Esta consulta devuelve {n_j} filas:</p>" + sql_html(Q_J)
    + "<p>Se cambia una sola palabra: <code>JOIN</code> pasa a ser <code>LEFT JOIN</code>.</p>",
    "¿Cuántas filas devuelve ahora?",
    [(f"Las mismas {n_j}",
      "Sería así si todos los clientes tuvieran alguna orden. Hay clientes que no tienen."),
     (f"Más: {n_l}",
      f"Se suman los {n_clientes - con_orden} clientes sin órdenes, cada uno en una fila con "
      "<code>nro_orden</code> en NULL."),
     (f"Menos: {con_orden}",
      f"{con_orden} es la cantidad de clientes que tienen órdenes. El <code>LEFT JOIN</code> "
      "no quita filas ni resume."),
     (f"Más: {n_clientes * n_ordenes}",
      f"{n_clientes * n_ordenes} sería cada cliente con cada orden, que es lo que da un cruce "
      "sin condición. El <code>ON</code> sigue estando.")],
    1,
    "No tener claro qué agrega un <code>LEFT JOIN</code>: las filas de la tabla izquierda que "
    "no encontraron pareja, con NULL en todas las columnas de la derecha. Nunca devuelve "
    "menos filas que el <code>JOIN</code>.",
    lambda: (
        "<p>Las filas marcadas son las que agrega el <code>LEFT JOIN</code>. El NULL de "
        "<code>nro_orden</code> no está guardado en ninguna tabla: lo pone el cruce.</p>"
        + tabla(Q_L, destacar=lambda f: f["nro_orden"] is None)),
    retirado=SOLO_CUENTA,
)


# ── La condición en dos lugares ────────────────────────────────────────

Q_W = """
SELECT id_cliente, SUM(total) AS facturado
FROM orden_servicio
WHERE total > 50000
GROUP BY id_cliente;
"""
Q_H = """
SELECT id_cliente, SUM(total) AS facturado
FROM orden_servicio
GROUP BY id_cliente
HAVING SUM(total) > 50000;
"""
n_w, n_h = cuantas(Q_W), cuantas(Q_H)
assert (n_w, n_h) == (1, 2)
assert [f[0] for f in correr(Q_W)[1]] == [1] and sorted(f[0] for f in correr(Q_H)[1]) == [1, 2]
assert cuantas("SELECT * FROM orden_servicio WHERE id_cliente = 2") == 2
assert correr(Q_W)[1][0][1] != [f for f in correr(Q_H)[1] if f[0] == 1][0][1]

ejercicio(
    "La condición en dos lugares",
    "Clientes que acumulan más de $50.000",
    ["orden_servicio"],
    "<p>Martín quiere los clientes que <strong>acumulan más de $50.000 entre todas sus "
    "órdenes</strong>. Hay dos consultas parecidas:</p>"
    + variantes(("I", Q_W), ("II", Q_H)),
    "¿Cuál responde el pedido?",
    [("La I",
      "La I descarta primero toda orden de $50.000 o menos y suma lo que queda. Responde otro "
      "pedido: cuánto suman las órdenes grandes de cada cliente."),
     ("Las dos: devuelven lo mismo",
      f"Devuelven distinta cantidad de filas: la I, {n_w}; la II, {n_h}."),
     ("Ninguna: para filtrar por una suma hace falta una subconsulta",
      "El <code>HAVING</code> filtra grupos por un valor calculado, como la suma. "
      "La II lo usa así y alcanza."),
     ("La II",
      "La II suma todas las órdenes de cada cliente y después se queda con los grupos cuya "
      "suma pasa de $50.000.")],
    3,
    "Poner la condición donde «suena» y no donde corresponde. Si la condición habla de cada "
    "orden, va en el <code>WHERE</code>; si habla del acumulado del cliente, va en el "
    "<code>HAVING</code>.",
    lambda: (
        "<p>El cliente 2 no tiene ninguna orden de más de $50.000, pero entre las dos que "
        "tiene supera ese monto. La I lo pierde y la II lo encuentra. En el cliente 1 las dos "
        "consultas coinciden en la fila y difieren en la suma.</p>"
        '<div class="res-fila">'
        + tabla(Q_W, rotulo="I · la condición en el WHERE")
        + tabla(Q_H, rotulo="II · la condición en el HAVING")
        + "</div>"),
)


# ── Corre, pero responde otra cosa (filas repetidas) ───────────────────

Q_MAL = """
SELECT C.id_cliente, C.apellido, SUM(O.total) AS facturado
FROM cliente C
JOIN orden_servicio O ON O.id_cliente = C.id_cliente
JOIN orden_servicio_pago P ON P.nro_orden = O.nro_orden
GROUP BY C.id_cliente, C.apellido
ORDER BY C.id_cliente;
"""
Q_BIEN = """
SELECT C.id_cliente, C.apellido, SUM(O.total) AS facturado
FROM cliente C
JOIN orden_servicio O ON O.id_cliente = C.id_cliente
GROUP BY C.id_cliente, C.apellido
ORDER BY C.id_cliente;
"""
mal1 = correr(Q_MAL)[1][0][2]
bien1 = correr(Q_BIEN)[1][0][2]
real1 = correr("SELECT SUM(total) FROM orden_servicio WHERE id_cliente = 1")[1][0][0]
assert bien1 == real1 and mal1 > bien1
assert cuantas("SELECT * FROM orden_servicio WHERE id_cliente = 1") == 3

ejercicio(
    "Corre, pero responde otra cosa",
    "El total facturado a cada cliente",
    ["cliente", "orden_servicio", "orden_servicio_pago"],
    "<p>Martín pide <strong>cuánto se le facturó a cada cliente</strong>, sumando el total de "
    "sus órdenes. Se escribe esta consulta, que corre sin problemas:</p>" + sql_html(Q_MAL)
    + f"<p>Al cliente 1 le informa ${plata(mal1)}, y sus tres órdenes suman ${plata(real1)}.</p>",
    "¿Cuál es el cambio mínimo que la corrige?",
    [("Agregar <code>DISTINCT</code> después del <code>SELECT</code>",
      "<code>DISTINCT</code> quita filas repetidas del resultado final, y ahí ya hay una fila "
      "por cliente. La suma inflada se calculó antes."),
     ("Sacar el cruce con <code>orden_servicio_pago</code>",
      "El pedido no usa ningún dato de los pagos. Ese cruce repite cada orden una vez por "
      "pago, y el total de la orden se suma repetido."),
     ("Cambiar los dos <code>JOIN</code> por <code>LEFT JOIN</code>",
      "Agregaría los clientes sin órdenes, pero las órdenes con dos pagos seguirían contando "
      "doble."),
     ("Agrupar también por <code>O.nro_orden</code>",
      "Daría una fila por orden, no por cliente, y cada orden con dos pagos seguiría sumando "
      "su total dos veces.")],
    1,
    "Cruzar una tabla de más. Cada cruce puede multiplicar filas, y una suma calculada sobre "
    "filas repetidas da un número que parece razonable y está mal. Antes de sumar conviene "
    "preguntarse de qué hay una fila en el cruce.",
    lambda: (
        "<p>La orden 1 tiene dos pagos: después del segundo cruce aparece en dos filas y su "
        "total entra dos veces en la suma. Lo mismo pasa con las órdenes "
        f"{', '.join(map(str, dobles[1:-1]))} y {dobles[-1]}.</p>"
        '<div class="res-fila">'
        + tabla(Q_MAL, destacar=lambda f: True, rotulo="Con el cruce de más")
        + tabla(Q_BIEN, rotulo="Sin ese cruce")
        + "</div>"),
)


# ── Corre, pero responde otra cosa (el NULL) ───────────────────────────

Q_IGUAL = """
SELECT C.nombre, C.apellido
FROM cliente C
LEFT JOIN orden_servicio O ON O.id_cliente = C.id_cliente
WHERE O.nro_orden = NULL;
"""
Q_IS = Q_IGUAL.replace("= NULL", "IS NULL")
n_is = cuantas(Q_IS)
assert cuantas(Q_IGUAL) == 0 and n_is == n_clientes - con_orden

ejercicio(
    "Corre, pero responde otra cosa",
    "Clientes que nunca trajeron un equipo",
    ["cliente", "orden_servicio"],
    "<p>Para listar los clientes que <strong>no tienen ninguna orden</strong> se escribe:</p>"
    + sql_html(Q_IGUAL),
    "¿Qué pasa al ejecutarla?",
    [(f"Devuelve los {n_is} clientes sin órdenes",
      "Eso devolvería con <code>IS NULL</code>. Con <code>=</code> la comparación nunca da "
      "verdadero."),
     (f"Devuelve los {n_clientes} clientes",
      "El <code>WHERE</code> sí filtra: deja pasar solo las filas donde la condición es "
      "verdadera, y acá no lo es en ninguna."),
     ("Devuelve 0 filas, sin ningún aviso",
      "Comparar con NULL usando <code>=</code> da «desconocido» para toda fila. Ninguna pasa "
      "el filtro, y el motor no lo considera un error."),
     ("No corre: NULL no se puede comparar con <code>=</code>",
      "La sentencia es válida y el motor la ejecuta. El problema está en el resultado.")],
    2,
    "Tratar a NULL como un valor más y suponer que, si la consulta está mal pensada, el motor "
    "avisa. Una consulta puede correr sin error y devolver una hoja en blanco.",
    lambda: (
        "<p>NULL significa «no se sabe», y preguntarle al motor si algo es igual a un valor "
        "que no se sabe da «desconocido». Para preguntar si un dato falta existe "
        "<code>IS NULL</code>:</p>" + sql_html(Q_IS) + tabla(Q_IS)),
    examen="Fue la pregunta 11 del examen, la de menos aciertos junto con otras dos. "
           "La respuesta más elegida fue que daba error de sintaxis.",
)


# ── Subconsulta en dos pasos ──────────────────────────────────────────

Q = """
SELECT nombre, precio_unitario
FROM repuesto
WHERE precio_unitario > (SELECT AVG(precio_unitario) FROM repuesto);
"""
promedio = correr("SELECT AVG(precio_unitario) FROM repuesto")[1][0][0]
n_rep = cuantas("SELECT * FROM repuesto")
n_caros = cuantas(Q)
assert n_caros == 4

ejercicio(
    "Subconsulta en dos pasos",
    "Repuestos más caros que el promedio",
    ["repuesto"],
    "<p>Se ejecuta:</p>" + sql_html(Q)
    + referencia("repuesto",
                 ("Cantidad de repuestos", "COUNT(*)", False),
                 ("Suma de precios", "SUM(precio_unitario)", True),
                 ("Precio promedio", "AVG(precio_unitario)", True),
                 ("Precio mínimo", "MIN(precio_unitario)", True),
                 ("Precio máximo", "MAX(precio_unitario)", True)),
    "¿Qué devuelve la consulta de adentro, y qué hace la de afuera con eso?",
    [("Un solo valor, el promedio; la de afuera lista los repuestos cuyo precio lo supera",
      "La de adentro se resuelve una vez y deja un número. La de afuera compara contra ese "
      "número el precio de cada repuesto."),
     ("Un valor por cada repuesto; la de afuera compara cada precio con el suyo",
      "<code>AVG</code> sin <code>GROUP BY</code> resume toda la tabla en una sola fila."),
     ("Un solo valor; la de afuera también queda resumida en una sola fila",
      "La que queda en una fila es la de adentro. La de afuera no agrega nada: lista los "
      "repuestos que pasan el filtro."),
     ("No corre: una consulta no puede ir dentro del <code>WHERE</code>",
      "Puede. Una subconsulta que devuelve un solo valor se usa en el <code>WHERE</code> como "
      "cualquier número.")],
    0,
    "Leer la consulta entera de una vez. Una subconsulta se resuelve por separado: primero "
    "la de adentro, se anota qué devuelve, y recién después se lee la de afuera con ese "
    "resultado en el lugar del paréntesis.",
    lambda: (
        "<p><strong>Paso 1.</strong> La de adentro devuelve un valor: "
        f"<code>{promedio:.2f}</code>.</p>"
        "<p><strong>Paso 2.</strong> La de afuera queda como "
        f"<code>WHERE precio_unitario &gt; {promedio:.2f}</code>:</p>" + tabla(Q)),
    examen="En la pregunta 10 del examen, casi un tercio del curso respondió que no se puede "
           "usar una consulta dentro del <code>WHERE</code>.",
)


# ── Dos caminos ───────────────────────────────────────────────────────

Q_IN = """
SELECT C.id_cliente, C.apellido
FROM cliente C
WHERE C.id_cliente IN (SELECT O.id_cliente
                       FROM orden_servicio O
                       JOIN orden_servicio_pago P ON P.nro_orden = O.nro_orden);
"""
Q_JN = """
SELECT C.id_cliente, C.apellido
FROM cliente C
JOIN orden_servicio O ON O.id_cliente = C.id_cliente
JOIN orden_servicio_pago P ON P.nro_orden = O.nro_orden;
"""
Q_JD = Q_JN.replace("SELECT C.id_cliente", "SELECT DISTINCT C.id_cliente")
caminos = (cuantas(Q_IN), cuantas(Q_JN), cuantas(Q_JD))
assert caminos == (n_pagaron, n_pagos, n_pagaron)

ejercicio(
    "Dos caminos al mismo pedido",
    "Clientes que hicieron algún pago",
    ["cliente", "orden_servicio", "orden_servicio_pago"],
    "<p>Se quieren los clientes que hicieron <strong>al menos un pago</strong>. "
    "Hay tres consultas:</p>" + variantes(("I", Q_IN), ("II", Q_JN), ("III", Q_JD)),
    "¿Cuántas filas devuelve cada una?",
    [(f"I: {caminos[0]} · II: {caminos[0]} · III: {caminos[0]}",
      "La II no resume: el cruce deja una fila por pago."),
     (f"I: {caminos[1]} · II: {caminos[1]} · III: {caminos[0]}",
      "<code>IN</code> pregunta si el cliente está en la lista. Que esté varias veces en la "
      "lista no lo repite en el resultado."),
     (f"I: {caminos[0]} · II: {caminos[1]} · III: {caminos[1]}",
      "<code>DISTINCT</code> quita las filas repetidas: en la III queda una por cliente."),
     (f"I: {caminos[0]} · II: {caminos[1]} · III: {caminos[0]}",
      "La I y la III responden el pedido. La II devuelve una fila por pago.")],
    3,
    "Contar pagos cuando se piden clientes. <code>IN</code> filtra las filas de la tabla de "
    "afuera y no las multiplica; el <code>JOIN</code> arma una fila por cada combinación.",
    lambda: (
        f"<p>La subconsulta de la I devuelve {caminos[1]} valores de <code>id_cliente</code>, "
        f"con repetidos, y aun así la I devuelve {caminos[0]} filas: una por cada cliente que "
        "figura en esa lista.</p>"
        '<div class="res-fila">'
        + tabla(Q_IN, rotulo="I · con IN")
        + tabla(Q_JN, rotulo="II · con JOIN")
        + tabla(Q_JD, rotulo="III · con JOIN y DISTINCT")
        + "</div>"),
    examen="En la pregunta 24 del examen, el error más común fue contar préstamos abiertos "
           "en lugar de socios.",
    retirado=SOLO_CUENTA,
)


# ── El estado después de un cambio ────────────────────────────────────

Q_UPD = """
UPDATE orden_servicio
SET fecha_entrega = '2026-06-05 10:00:00'
WHERE id_orden_estado = 3;
"""
Q_CNT = "SELECT COUNT(*), COUNT(fecha_entrega) FROM orden_servicio;"
antes = correr(Q_CNT)[1][0]
despues = correr(Q_UPD + Q_CNT)[1][0]
entregadas = cuantas("SELECT * FROM orden_servicio WHERE id_orden_estado = 3")
assert antes == (n_ordenes, 0) and despues == (n_ordenes, entregadas)

ejercicio(
    "El estado después de un cambio",
    "Cargar la fecha de entrega",
    ["orden_servicio"],
    f"<p>Las {n_ordenes} órdenes tienen <code>fecha_entrega</code> en NULL. Se cargan las "
    "fechas de las que están en estado 3, «Entregado»:</p>" + sql_html(Q_UPD)
    + "<p>Inmediatamente después se ejecuta:</p>" + sql_html(Q_CNT),
    "¿Qué muestra esta segunda consulta?",
    [(f"{n_ordenes} y {n_ordenes}",
      "<code>COUNT(fecha_entrega)</code> saltea las filas donde la fecha sigue en NULL."),
     (f"{entregadas} y {entregadas}",
      "El <code>UPDATE</code> cambia un dato en algunas filas; no borra las demás. "
      "<code>COUNT(*)</code> sigue contando todas."),
     (f"{n_ordenes} y {entregadas}",
      "<code>COUNT(*)</code> cuenta filas. <code>COUNT(fecha_entrega)</code> cuenta las filas "
      "que tienen la fecha cargada."),
     (f"{n_ordenes} y 0",
      "Ese era el estado anterior al <code>UPDATE</code>.")],
    2,
    "Dos cosas: suponer que <code>COUNT(columna)</code> cuenta filas, y leer el "
    "<code>WHERE</code> de un <code>UPDATE</code> como si fuera un filtro de lo que queda en "
    "la tabla.",
    lambda: (
        f"<p>El <code>UPDATE</code> toca las {entregadas} órdenes en estado 3. Las otras "
        f"{n_ordenes - entregadas} conservan el NULL, y <code>COUNT(fecha_entrega)</code> no "
        "las cuenta. Las dos funciones comparten la única fila del resultado.</p>"
        + tabla(Q_UPD + Q_CNT)
        + tabla(Q_UPD + "SELECT nro_orden, id_orden_estado, fecha_entrega FROM orden_servicio "
                        "ORDER BY nro_orden;",
                destacar=lambda f: f["fecha_entrega"] is None,
                rotulo="La tabla después del UPDATE")),
    examen="La pregunta 14 del examen pedía lo mismo sobre la fecha de devolución, y la 8 "
           "mostró que varios esperan una fila por cada función de agregación.",
)


# ---------------------------------------------------------------------------
# El recorrido por etapas, como ayuda
# ---------------------------------------------------------------------------
# El método de unidades/04-sql/orden-de-ejecucion.html: seguir la consulta en
# el orden en que la resuelve el motor, con las mismas columnas de punta a
# punta, las filas descartadas tachadas a la vista y los grupos como bloques.
# Igual que allá, no es un intérprete de SQL: la consulta se declara por
# partes y de ahí sale el estado de la tabla en cada etapa. La última etapa se
# compara con lo que devuelve la consulta de verdad.

TONOS = ["var(--bloque-cian)", "var(--bloque-violeta)", "var(--bloque-ambar)",
         "var(--bloque-rosa)", "var(--bloque-azul)", "var(--bloque-verde)"]


def _texto(columna: str, valor) -> str:
    return html.escape(apunte.celda(valor, columna.split(".")[-1], DINERO))


def _celdas(cols, datos, nuevas=()) -> str:
    """Las celdas de una fila de la tabla de trabajo. Una columna de una tabla
    que todavía no entró al cruce se muestra con un punto, no con NULL."""
    celdas = []
    for c in cols:
        if c not in datos:
            celdas.append('<td class="pendiente">·</td>')
        elif datos[c] is None:
            celdas.append('<td class="nulo">NULL</td>')
        else:
            clase = ' class="nuevo"' if c in nuevas else ""
            celdas.append(f"<td{clase}>{_texto(c, datos[c])}</td>")
    return "".join(celdas)


def _cabeza(titulos) -> str:
    return "<thead><tr>" + "".join(f"<th>{html.escape(t)}</th>" for t in titulos) + "</tr></thead>"


def _tabla_trabajo(cols, filas, nuevas=()) -> str:
    cuerpo = []
    for f in filas:
        clases = [] if f["estado"] == "queda" else [f["estado"]]
        if f.get("con_nulos"):
            clases.append("con-nulos")
        clase = f' class="{" ".join(clases)}"' if clases else ""
        cuerpo.append(f"<tr{clase}>{_celdas(cols, f['datos'], nuevas)}</tr>")
    return ('<div class="visor-scroll"><table class="visor-tabla">' + _cabeza(cols)
            + "<tbody>" + "".join(cuerpo) + "</tbody></table></div>")


def _tabla_grupos(cols, grupos, descartadas) -> str:
    cuerpo = []
    for i, g in enumerate(grupos):
        tono = f' style="--tono: {TONOS[i % len(TONOS)]}"'
        n = len(g["filas"])
        cuerpo.append(
            f'<tr class="grupo-cab"{tono}><td colspan="{len(cols)}"><span class="chapa"></span>'
            f'grupo «{html.escape(g["rotulo"])}» · {n} {"fila" if n == 1 else "filas"}</td></tr>')
        for f in g["filas"]:
            cuerpo.append(f'<tr class="del-grupo"{tono}>{_celdas(cols, f["datos"])}</tr>')
        if "valores" in g:
            cuentas = "<br>".join(
                f'<span class="fn">{fn}</span> {expr} → <span class="igual">{alias}</span>'
                for alias, fn, expr, _ in g["valores"])
            cuerpo.append(f'<tr class="grupo-calc"><td colspan="{len(cols)}">{cuentas}</td></tr>')
    for f in descartadas:
        cuerpo.append(f'<tr class="ida">{_celdas(cols, f["datos"])}</tr>')
    return ('<div class="visor-scroll"><table class="visor-tabla">' + _cabeza(cols)
            + "<tbody>" + "".join(cuerpo) + "</tbody></table></div>")


def _tabla_salida(titulos, filas, tachadas=()) -> str:
    cuerpo = []
    for i, fila in enumerate(filas):
        clase = ' class="se-va"' if i in tachadas else ""
        celdas = "".join(
            '<td class="nulo">NULL</td>' if v is None else f"<td>{_texto(t, v)}</td>"
            for t, v in zip(titulos, fila))
        cuerpo.append(f"<tr{clase}>{celdas}</tr>")
    return ('<div class="visor-scroll visor-salida"><table class="visor-tabla">'
            + _cabeza(titulos) + "<tbody>" + "".join(cuerpo) + "</tbody></table></div>")


def _n_filas(n: int) -> str:
    return f"{n} fila" if n == 1 else f"{n} filas"


def recorrer(c: dict) -> list[dict]:
    """Un estado por etapa. `c` declara la consulta:

    sql        la consulta completa, para comparar el final
    columnas   las columnas de la tabla de trabajo, con su alias (C.apellido)
    origen     (alias, tabla, orden)
    joins      [{tipo, alias, tabla, orden, on, texto, mirar}]
    where      [{texto, prueba, mirar}]
    group_by   columnas por las que se agrupa; `agregados` [(alias, 'COUNT(*)')]
    select     [(título, columna)] o [(título, '@alias')] para un agregado
    distinct, order_by [(título, descendente)], limit
    previa     {sql, mirar}: la subconsulta que se resuelve antes
    mirar      la pregunta que guía cada etapa, por nombre de etapa
    """
    cols = c["columnas"]
    mirar = c.get("mirar", {})
    etapas = []

    def cargar(alias, tabla, orden):
        propias = [k for k in cols if (k.split(".")[0] == alias if alias else True)]
        nombres = ", ".join(k.split(".")[-1] for k in propias)
        return [dict(zip(propias, f))
                for f in correr(f"SELECT {nombres} FROM {tabla} ORDER BY {orden}")[1]]

    def etapa(rotulo, nombre, dice, cuenta, cuerpo, leyenda, pregunta=""):
        etapas.append(dict(rotulo=rotulo, nombre=nombre, dice=dice, cuenta=cuenta,
                           cuerpo=cuerpo, leyenda=leyenda, mirar=pregunta))

    def vivas():
        return [f for f in filas if f["estado"] == "queda"]

    def asentar():
        """Lo que esta etapa descartó pasa a «descartado antes»."""
        for f in filas:
            if f["estado"] == "se-va":
                f["estado"] = "ida"

    # ---- la subconsulta, que se resuelve antes del recorrido de afuera ----
    if c.get("previa"):
        titulos, valores = correr(c["previa"]["sql"])
        etapa("subconsulta", "La consulta de adentro se resuelve primero",
              "Corre una sola vez, antes de que empiece el recorrido de afuera, y deja su "
              "resultado en el lugar del paréntesis.",
              f"<strong>{_n_filas(len(valores))}</strong> · {len(titulos)} "
              f"{'columna' if len(titulos) == 1 else 'columnas'}",
              sql_html(c["previa"]["sql"]) + _tabla_salida(titulos, valores),
              [("l-queda", "lo que devuelve la subconsulta")], c["previa"].get("mirar", ""))

    # ---- FROM ----
    alias, tabla, orden = c["origen"]
    filas = [dict(datos=d, estado="queda") for d in cargar(alias, tabla, orden)]
    etapa("FROM", "Las filas de la tabla",
          f"De acá salen las filas: la tabla <code>{tabla}</code> completa.",
          f"<strong>{_n_filas(len(filas))}</strong>",
          _tabla_trabajo(cols, filas), [("l-queda", "siguen en juego")], mirar.get("FROM", ""))

    # ---- JOIN … ON: se suma una tabla por vez ----
    for j in c.get("joins", []):
        derecha = cargar(j["alias"], j["tabla"], j["orden"])
        vacia = {k: None for k in derecha[0]}
        izquierdo = j["tipo"] == "LEFT JOIN"
        antes, nuevas, huerfanas, rellenadas = len(vivas()), [], 0, 0
        for f in filas:
            if f["estado"] != "queda":
                nuevas.append(f)
                continue
            parejas = [d for d in derecha if j["on"]({**f["datos"], **d})]
            for d in parejas:
                nuevas.append(dict(datos={**f["datos"], **d}, estado="queda"))
            if not parejas and izquierdo:
                rellenadas += 1
                nuevas.append(dict(datos={**f["datos"], **vacia}, estado="queda", con_nulos=True))
            elif not parejas:
                huerfanas += 1
                nuevas.append(dict(datos=dict(f["datos"]), estado="se-va"))
        filas = nuevas
        leyenda = [("l-queda", "siguen en juego")]
        if huerfanas:
            leyenda.append(("l-sale", "sin pareja: las descarta el JOIN"))
        if rellenadas:
            leyenda.append(("l-nula", "sin pareja: el LEFT JOIN las completa con NULL"))
        etapa(j["tipo"], f"Se suma la tabla {j['tabla']}",
              f"Cada fila busca sus parejas en <code>{j['tabla']}</code> con la condición "
              f"<code>{html.escape(j['texto'])}</code>. "
              + ("La que no encuentra ninguna queda igual, con NULL en las columnas nuevas."
                 if izquierdo else "La que no encuentra ninguna se descarta."),
              f"{_n_filas(antes)} → <strong>{_n_filas(len(vivas()))}</strong>"
              + (f' <span class="baja">(−{huerfanas} sin pareja)</span>' if huerfanas else "")
              + (f" · {rellenadas} con NULL" if rellenadas else ""),
              _tabla_trabajo(cols, filas, nuevas=set(vacia)), leyenda, j.get("mirar", ""))
        asentar()

    # ---- WHERE, condición por condición ----
    for cond in c.get("where", []):
        antes = len(vivas())
        for f in vivas():
            if not cond["prueba"](f["datos"]):
                f["estado"] = "se-va"
        quedan = len(vivas())
        leyenda = [("l-queda", "siguen en juego"), ("l-sale", "las descarta esta etapa")]
        if any(f["estado"] == "ida" for f in filas):
            leyenda.append(("l-ida", "ya estaban descartadas"))
        etapa("WHERE", "Se descartan filas",
              f"La condición <code>{html.escape(cond['texto'])}</code> se prueba fila por fila. "
              "Siguen las filas en las que da verdadero.",
              f"{_n_filas(antes)} → <strong>{_n_filas(quedan)}</strong> "
              f'<span class="baja">(−{antes - quedan})</span>',
              _tabla_trabajo(cols, filas), leyenda, cond.get("mirar", ""))
        asentar()

    # ---- GROUP BY y los agregados ----
    grupos = None
    if c.get("group_by"):
        por = c["group_by"]
        descartadas = [f for f in filas if f["estado"] != "queda"]
        mapa: dict[tuple, list] = {}
        for f in vivas():
            mapa.setdefault(tuple(f["datos"][k] for k in por), []).append(f)
        grupos = [dict(rotulo=" ".join(str(v) for v in clave), filas=suyas)
                  for clave, suyas in mapa.items()]
        leyenda = [("l-queda", "cada bloque es un grupo")]
        if descartadas:
            leyenda.append(("l-ida", "filas descartadas antes de agrupar"))
        etapa("GROUP BY", "Las filas se reparten en grupos",
              "Van al mismo grupo las filas que coinciden en "
              + " y ".join(f"<code>{k}</code>" for k in por) + ". Ninguna fila se pierde.",
              f"{_n_filas(len(vivas()))} → <strong>{len(grupos)} grupos</strong>",
              _tabla_grupos(cols, grupos, descartadas), leyenda, mirar.get("GROUP BY", ""))

        for g in grupos:
            g["valores"] = []
            for nombre, fn in c["agregados"]:
                assert fn == "COUNT(*)", "el recorrido solo sabe contar filas"
                n = len(g["filas"])
                expr = ("cuenta la fila del grupo = " if n == 1
                        else f"cuenta las {n} filas del grupo = ") + str(n)
                g["valores"].append((nombre, fn, expr, n))
        etapa("agregados", "Se calculan las funciones de cada grupo",
              "La función trabaja sobre las filas de cada bloque y deja un valor por grupo.",
              f"{len(grupos)} grupos · {len(c['agregados'])} "
              f"{'función' if len(c['agregados']) == 1 else 'funciones'}",
              _tabla_grupos(cols, grupos, descartadas), leyenda, mirar.get("agregados", ""))

    # ---- SELECT: la proyección ----
    titulos = [t for t, _ in c["select"]]
    if grupos is not None:
        salida = []
        for g in grupos:
            valores = {nombre: valor for nombre, _, _, valor in g["valores"]}
            salida.append([valores[de[1:]] if de.startswith("@") else g["filas"][0]["datos"][de]
                           for _, de in c["select"]])
        cuenta = (f"{_n_filas(sum(len(g['filas']) for g in grupos))} en {len(grupos)} grupos → "
                  f"<strong>{_n_filas(len(salida))}</strong>")
        nombre, dice = ("Cada grupo colapsa en una fila",
                        "De cada grupo queda una sola fila, con las columnas que pide el "
                        "<code>SELECT</code>.")
    else:
        salida = [[f["datos"][de] for _, de in c["select"]] for f in vivas()]
        cuenta = f"<strong>{_n_filas(len(salida))}</strong> · {len(titulos)} columnas"
        nombre, dice = ("Se arman las columnas de salida",
                        "De cada fila que sigue en juego se toman las columnas que pide el "
                        "<code>SELECT</code>. Las demás dejan de verse.")
    etapa("SELECT", nombre, dice, cuenta, _tabla_salida(titulos, salida),
          [("l-queda", "filas del resultado")], mirar.get("SELECT", ""))

    # ---- DISTINCT: compara filas ya proyectadas ----
    if c.get("distinct"):
        vistas, repetidas = set(), set()
        for i, fila in enumerate(salida):
            if tuple(fila) in vistas:
                repetidas.add(i)
            vistas.add(tuple(fila))
        leyenda = [("l-queda", "filas del resultado")]
        if repetidas:
            leyenda.append(("l-sale", "repetidas: las descarta DISTINCT"))
        etapa("DISTINCT", "Se descartan las filas repetidas",
              "Se comparan las filas ya armadas por el <code>SELECT</code>, completas, y de las "
              "que son iguales queda una.",
              f"{_n_filas(len(salida))} → <strong>{_n_filas(len(salida) - len(repetidas))}</strong> "
              f'<span class="baja">(−{len(repetidas)})</span>',
              _tabla_salida(titulos, salida, repetidas), leyenda, mirar.get("DISTINCT", ""))
        salida = [f for i, f in enumerate(salida) if i not in repetidas]

    # ---- ORDER BY ----
    if c.get("order_by"):
        for titulo, descendente in reversed(c["order_by"]):
            i = titulos.index(titulo)
            salida.sort(key=lambda fila: (fila[i] is not None, fila[i] or 0),
                        reverse=descendente)
        etapa("ORDER BY", "Se ordena el resultado",
              "Las filas son las mismas de la etapa anterior, en otro orden.",
              f"<strong>{_n_filas(len(salida))}</strong>", _tabla_salida(titulos, salida),
              [("l-queda", "filas del resultado")], mirar.get("ORDER BY", ""))

    # ---- LIMIT ----
    if c.get("limit"):
        tope = c["limit"]
        etapa("LIMIT", "Se corta el resultado",
              f"Se devuelven las primeras {tope} filas en el orden en que quedaron."
              if tope > 1 else "Se devuelve la primera fila en el orden en que quedaron.",
              f"{_n_filas(len(salida))} → <strong>{_n_filas(min(tope, len(salida)))}</strong>",
              _tabla_salida(titulos, salida, set(range(tope, len(salida)))),
              [("l-queda", "se devuelven"), ("l-sale", "las corta el LIMIT")],
              mirar.get("LIMIT", ""))
        salida = salida[:tope]

    # el final del recorrido tiene que ser lo que devuelve la consulta
    def normal(tabla_filas):
        return [[float(v) if isinstance(v, (int, float)) else v for v in f] for f in tabla_filas]
    reales, recorridas = normal(correr(c["sql"])[1]), normal(salida)
    if not c.get("order_by"):
        reales, recorridas = sorted(reales, key=repr), sorted(recorridas, key=repr)
    assert recorridas == reales, f"el recorrido no llega al resultado de\n{c['sql']}"
    return etapas


def recorrido_html(c: dict, titulo: str = "") -> str:
    etapas = recorrer(c)
    chips, paneles = [], []
    for i, e in enumerate(etapas, 1):
        actual = ' aria-current="step"' if i == 1 else ""
        chips.append(f'<button type="button" class="rec-chip"{actual}>{i} · {e["rotulo"]}</button>')
        leyenda = "".join(f'<span class="{clase}">{texto}</span>' for clase, texto in e["leyenda"])
        pregunta = (f'<div class="visor-nota"><strong>Para mirar.</strong> {e["mirar"]}</div>\n'
                    if e["mirar"] else "")
        paneles.append(
            f'<div class="rec-etapa"{"" if i == 1 else " hidden"}>\n'
            f'<div class="visor-titulo"><span class="visor-etapa">etapa {i} de {len(etapas)} · '
            f'{e["rotulo"]}</span><h3>{e["nombre"]}</h3></div>\n'
            f'<p class="visor-dice">{e["dice"]}</p>\n'
            f'<p class="visor-cuenta">{e["cuenta"]}</p>\n'
            f'{e["cuerpo"]}\n'
            f'<p class="visor-leyenda">{leyenda}</p>\n'
            f'{pregunta}</div>')
    cabeza = f'<p class="rec-titulo">{titulo}</p>\n' if titulo else ""
    return (
        '<div class="recorrido">\n' + cabeza
        + '<div class="rec-barra" role="group" aria-label="Etapas de la consulta">'
        + "".join(chips) + "</div>\n" + "\n".join(paneles) + "\n"
        '<div class="rec-nav"><button type="button" class="boton" data-ir="-1">Etapa anterior</button>'
        '<button type="button" class="boton" data-ir="1">Etapa siguiente</button></div>\n</div>')


def ayuda(*recorridos: str) -> str:
    """El desplegable con el recorrido, para el grupo que lo necesite."""
    return (
        '<details class="ej-ayuda">\n'
        "<summary>¿Necesitan ayuda? Recorran la consulta por etapas</summary>\n"
        '<p class="ayuda-intro">Este es el método de '
        '<a href="orden-de-ejecucion.html">El orden en que corre una consulta</a>: seguirla en '
        "el orden en que la resuelve el motor y mirar, en cada etapa, qué filas hay y cuáles se "
        "van. Avancen de a una etapa y contesten la pregunta de cada paso antes de pasar al "
        "siguiente.</p>\n" + "\n".join(recorridos) + "\n</details>")


# ---------------------------------------------------------------------------
# Para debatir en clase
# ---------------------------------------------------------------------------
# Cuatro ejercicios más difíciles. Ninguno pide ejecutar la consulta de memoria:
# el resultado está a la vista y la discusión es por qué sale eso.

# ── El WHERE que deshace un LEFT JOIN ──────────────────────────────────────

Q_WH = """
SELECT C.id_cliente, C.apellido, O.nro_orden
FROM cliente C
LEFT JOIN orden_servicio O ON O.id_cliente = C.id_cliente
WHERE O.id_orden_estado = 3
ORDER BY C.id_cliente, O.nro_orden;
"""
Q_SIN = """
SELECT C.id_cliente, C.apellido, O.nro_orden, O.id_orden_estado
FROM cliente C
LEFT JOIN orden_servicio O ON O.id_cliente = C.id_cliente
ORDER BY C.id_cliente, O.nro_orden;
"""
Q_ON = """
SELECT C.id_cliente, C.apellido, O.nro_orden
FROM cliente C
LEFT JOIN orden_servicio O ON O.id_cliente = C.id_cliente
                          AND O.id_orden_estado = 3
ORDER BY C.id_cliente, O.nro_orden;
"""
aparecen = sorted({f[0] for f in correr(Q_WH)[1]})
sin_ordenes = sorted(f[0] for f in correr(
    "SELECT id_cliente FROM cliente WHERE id_cliente NOT IN "
    "(SELECT id_cliente FROM orden_servicio) ORDER BY id_cliente")[1])
otro_estado = sorted(set(range(1, n_clientes + 1)) - set(aparecen) - set(sin_ordenes))
assert aparecen == [1, 2] and sin_ordenes and otro_estado
assert {f[0] for f in correr(Q_ON)[1]} == set(range(1, n_clientes + 1))
assert [f[2] for f in correr(Q_ON)[1] if f[2]] == [f[2] for f in correr(Q_WH)[1]]


def lista(numeros) -> str:
    numeros = [str(n) for n in numeros]
    return numeros[0] if len(numeros) == 1 else ", ".join(numeros[:-1]) + " y " + numeros[-1]


ejercicio(
    "¿Por qué falta?",
    "Todos los clientes, con sus órdenes entregadas",
    ["cliente", "orden_servicio"],
    "<p>Martín pide la lista de <strong>todos los clientes</strong> y, al lado de cada uno, "
    "sus órdenes entregadas (estado 3) si tiene alguna. Se usa un <code>LEFT JOIN</code> "
    "para que no falte ningún cliente:</p>" + sql_html(Q_WH)
    + f"<p>El resultado trae solo a los clientes {lista(aparecen)}:</p>"
    + tabla(Q_WH),
    "¿Por qué faltan los demás clientes?",
    [("El <code>LEFT JOIN</code> solo conserva los clientes que tienen alguna orden",
      "Eso hace el <code>JOIN</code>. El <code>LEFT JOIN</code> arma una fila para cada "
      "cliente sin órdenes, con NULL en las columnas de la orden."),
     ("El <code>WHERE</code> corre después del cruce y descarta toda fila donde "
      "<code>O.id_orden_estado</code> no vale 3, incluidas las que tienen NULL",
      "El cruce conserva a todos los clientes. Después el <code>WHERE</code> revisa fila por "
      "fila, y en la fila de un cliente sin órdenes <code>NULL = 3</code> no da verdadero."),
     ("El <code>ORDER BY</code> por <code>O.nro_orden</code> deja afuera las filas con NULL",
      "<code>ORDER BY</code> ordena las filas que llegan y no quita ninguna."),
     ("Falta un <code>GROUP BY C.id_cliente</code> para que haya una fila por cliente",
      "Agrupar resume las filas que quedaron. Las que el <code>WHERE</code> descartó ya no "
      "están para agruparse.")],
    1,
    "Suponer que el <code>LEFT JOIN</code> garantiza que la tabla izquierda llegue completa al "
    "resultado. Lo garantiza al salir del cruce; un <code>WHERE</code> sobre una columna de la "
    "tabla derecha vuelve a sacar las filas sin pareja.",
    lambda: (
        "<p>Este es el cruce antes del <code>WHERE</code>. Las filas marcadas son las que el "
        f"filtro descarta: las de los clientes {lista(sin_ordenes)}, que no tienen órdenes y "
        f"llevan NULL, y las de los clientes {lista(otro_estado)}, cuyas órdenes están en otro "
        "estado.</p>"
        + tabla(Q_SIN, destacar=lambda f: f["id_orden_estado"] != 3,
                rotulo="El LEFT JOIN sin el WHERE")
        + "<p>Una forma de corregirlo es llevar la condición al <code>ON</code>. Ahí decide "
        "qué órdenes se emparejan con cada cliente, y el cliente que no empareja ninguna "
        "queda igual en el resultado:</p>" + sql_html(Q_ON)
        + tabla(Q_ON, destacar=lambda f: f["nro_orden"] is None)),
    debate="¿Qué valor tiene <code>O.id_orden_estado</code> en la fila de un cliente que no "
           "tiene órdenes? ¿Y qué resultado da compararlo con 3?",
    ayuda=ayuda(recorrido_html(dict(
        sql=Q_WH,
        columnas=["C.id_cliente", "C.apellido", "O.nro_orden", "O.id_cliente", "O.id_orden_estado"],
        origen=("C", "cliente", "id_cliente"),
        joins=[dict(tipo="LEFT JOIN", alias="O", tabla="orden_servicio", orden="nro_orden",
                    on=lambda f: f["O.id_cliente"] == f["C.id_cliente"],
                    texto="O.id_cliente = C.id_cliente",
                    mirar="¿Qué clientes quedaron con NULL en las columnas de la orden? "
                          "¿Siguen en juego o se fueron?")],
        where=[dict(texto="O.id_orden_estado = 3",
                    prueba=lambda f: f["O.id_orden_estado"] == 3,
                    mirar="Revisen las filas tachadas una por una. ¿Qué valor tenía "
                          "<code>O.id_orden_estado</code> en cada una?")],
        select=[("id_cliente", "C.id_cliente"), ("apellido", "C.apellido"),
                ("nro_orden", "O.nro_orden")],
        order_by=[("id_cliente", False), ("nro_orden", False)],
        mirar={"FROM": "¿Están todos los clientes en este momento?",
               "SELECT": "¿En qué etapa se fue cada uno de los clientes que faltan?"}))),
)


# ── «No se usó» contra «se usó otro» ───────────────────────────────────────

Q_NE = """
SELECT DISTINCT O.nro_orden, O.total
FROM orden_servicio O
JOIN orden_servicio_pago P ON P.nro_orden = O.nro_orden
WHERE P.id_metodo_pago <> 1
ORDER BY O.nro_orden;
"""
Q_NOTIN = """
SELECT nro_orden, total
FROM orden_servicio
WHERE nro_orden NOT IN (SELECT nro_orden
                        FROM orden_servicio_pago
                        WHERE id_metodo_pago = 1)
ORDER BY nro_orden;
"""
con_efectivo = [f[0] for f in correr(
    "SELECT nro_orden FROM orden_servicio_pago WHERE id_metodo_pago = 1 ORDER BY nro_orden")[1]]
r_ne = [f[0] for f in correr(Q_NE)[1]]
r_notin = [f[0] for f in correr(Q_NOTIN)[1]]
coladas = [n for n in r_ne if n in con_efectivo]
assert coladas and 1 in coladas and not set(r_notin) & set(con_efectivo)
assert set(sin_pago) <= set(r_notin) and not set(sin_pago) & set(r_ne)
assert correr("SELECT nombre FROM metodo_pago WHERE id_metodo_pago = 1")[1][0][0] == "Efectivo"

ejercicio(
    "Lo que se pidió y lo que hace",
    "Órdenes en las que no se usó efectivo",
    ["orden_servicio", "orden_servicio_pago", "metodo_pago"],
    "<p>Martín pide <strong>las órdenes en las que no se usó efectivo</strong> (método 1). "
    "Se propone esta consulta:</p>" + sql_html(Q_NE)
    + "<p>Devuelve:</p>" + tabla(Q_NE, destacar=lambda f: f["nro_orden"] in con_efectivo),
    "¿Qué órdenes lista esta consulta?",
    [("Las órdenes en las que no se usó efectivo, como pidió Martín",
      f"La orden {coladas[0]} está en el resultado y tiene un pago en efectivo. "
      "El <code>WHERE</code> revisa cada pago por separado y deja pasar su otro pago."),
     ("Las órdenes que se pagaron únicamente en efectivo",
      "Una orden pagada solo en efectivo no tiene ningún pago que pase la condición "
      "<code>&lt;&gt; 1</code>, así que no aparecería."),
     ("Las órdenes que no tienen ningún pago registrado",
      f"Las órdenes {lista(sin_pago)} no tienen pagos y no aparecen: el <code>JOIN</code> "
      "las deja afuera antes de llegar al <code>WHERE</code>."),
     ("Las órdenes que tienen al menos un pago hecho con otro método",
      "Cada fila del cruce es un pago. La condición conserva los pagos que no son en "
      "efectivo, y el <code>DISTINCT</code> deja una fila por cada orden que tiene alguno.")],
    3,
    "Traducir «no se usó» como <code>&lt;&gt;</code>. Una condición del <code>WHERE</code> "
    "mira una fila por vez; que una orden no tenga ningún pago de cierto tipo es una "
    "afirmación sobre todos sus pagos juntos.",
    lambda: (
        f"<p>Las órdenes marcadas en el resultado ({lista(coladas)}) tienen un pago en "
        "efectivo y otro con un método distinto. Para el pedido de Martín se arma primero la "
        "lista de órdenes que sí usaron efectivo y se piden las que no están en ella:</p>"
        + sql_html(Q_NOTIN) + tabla(Q_NOTIN)
        + f"<p>Este resultado incluye las órdenes {lista(sin_pago)}, que todavía no tienen "
        "ningún pago. Queda para discutir si Martín las quiere en la lista.</p>"),
    debate="Busquen en el resultado una orden que tenga un pago en efectivo. "
           "¿Por qué pasó el filtro?",
    ayuda=ayuda(recorrido_html(dict(
        sql=Q_NE,
        columnas=["O.nro_orden", "O.total", "P.nro_orden", "P.id_metodo_pago", "P.monto"],
        origen=("O", "orden_servicio", "nro_orden"),
        joins=[dict(tipo="JOIN", alias="P", tabla="orden_servicio_pago",
                    orden="nro_orden, id_metodo_pago",
                    on=lambda f: f["P.nro_orden"] == f["O.nro_orden"],
                    texto="P.nro_orden = O.nro_orden",
                    mirar="Después del cruce, ¿de qué hay una fila: de cada orden o de cada "
                          "pago? ¿Qué órdenes se fueron acá?")],
        where=[dict(texto="P.id_metodo_pago <> 1",
                    prueba=lambda f: f["P.id_metodo_pago"] != 1,
                    mirar="Sigan a la orden 1. ¿Cuántas filas tenía antes de esta etapa y "
                          "qué pasó con cada una?")],
        select=[("nro_orden", "O.nro_orden"), ("total", "O.total")],
        distinct=True,
        order_by=[("nro_orden", False)],
        mirar={"SELECT": "¿Queda en estas filas algún rastro de los pagos que se descartaron?",
               "DISTINCT": "¿Había filas repetidas para sacar?"}))),
)


# ── Agrupar por un dato que se repite ──────────────────────────────────────

Q_NOM = """
SELECT C.nombre, C.apellido, COUNT(*) AS ordenes
FROM cliente C
JOIN orden_servicio O ON O.id_cliente = C.id_cliente
GROUP BY C.nombre, C.apellido
ORDER BY ordenes DESC, C.apellido, C.nombre;
"""
Q_ID = """
SELECT C.id_cliente, C.nombre, C.apellido, COUNT(*) AS ordenes
FROM cliente C
JOIN orden_servicio O ON O.id_cliente = C.id_cliente
GROUP BY C.id_cliente, C.nombre, C.apellido
ORDER BY C.id_cliente;
"""
homonimos = [f[0] for f in correr(
    "SELECT id_cliente FROM cliente WHERE nombre = 'Juan' AND apellido = 'Pérez' "
    "ORDER BY id_cliente")[1]]
por_id = {f[0]: f[3] for f in correr(Q_ID)[1]}
juntos = [f[2] for f in correr(Q_NOM)[1] if (f[0], f[1]) == ("Juan", "Pérez")][0]
assert homonimos == [1, 6] and juntos == por_id[1] + por_id[6] == 4 and por_id[1] == 3
assert cuantas(Q_NOM) == cuantas(Q_ID) - 1

ejercicio(
    "Corre, pero responde otra cosa",
    "Cuántas órdenes tiene cada cliente",
    ["cliente", "orden_servicio"],
    "<p>Martín pide <strong>cuántas órdenes tiene cada cliente</strong>, con nombre y "
    "apellido. La consulta:</p>" + sql_html(Q_NOM)
    + "<p>Devuelve:</p>"
    + tabla(Q_NOM, destacar=lambda f: (f["nombre"], f["apellido"]) == ("Juan", "Pérez"))
    + f"<p>En <code>orden_servicio</code>, el cliente 1 —Juan Pérez— figura en {por_id[1]} "
    f"órdenes, y el resultado le informa {juntos}.</p>",
    "¿De dónde sale la orden de más?",
    [("Hay dos clientes llamados Juan Pérez, y agrupar por nombre y apellido los junta en "
      "un solo grupo",
      f"Los clientes {lista(homonimos)} son personas distintas con el mismo nombre. "
      "El grupo se arma con las columnas del <code>GROUP BY</code>, y en esas dos columnas "
      "los dos clientes valen lo mismo."),
     ("El <code>JOIN</code> repite una de las órdenes del cliente 1",
      "Cada orden tiene un solo cliente, así que el cruce de cliente con orden deja una "
      "fila por orden, sin repetidas."),
     ("<code>COUNT(*)</code> suma una fila con NULL que no corresponde a ninguna orden",
      "Con <code>JOIN</code> no hay filas sin pareja. Las filas con NULL aparecerían con un "
      "<code>LEFT JOIN</code>."),
     ("Al agrupar por dos columnas, una orden se cuenta una vez por cada columna",
      "El <code>GROUP BY</code> agrupa por la combinación de las dos columnas. Cada fila cae "
      "en un solo grupo.")],
    0,
    "Agrupar por un dato que describe al cliente pero no lo identifica. Dos filas van al "
    "mismo grupo cuando coinciden en todas las columnas del <code>GROUP BY</code>; para que "
    "haya un grupo por cliente, entre esas columnas tiene que estar su clave.",
    lambda: (
        "<p>Con <code>id_cliente</code> en el <code>GROUP BY</code> cada cliente tiene su "
        "grupo, aunque comparta nombre y apellido con otro:</p>" + sql_html(Q_ID)
        + tabla(Q_ID, destacar=lambda f: f["id_cliente"] in homonimos)),
    debate="¿Qué filas del cruce caen en el grupo de Juan Pérez? Sigan cada una hasta la "
           "tabla <code>cliente</code>.",
    ayuda=ayuda(recorrido_html(dict(
        sql=Q_NOM,
        columnas=["C.id_cliente", "C.nombre", "C.apellido", "O.nro_orden", "O.id_cliente"],
        origen=("C", "cliente", "id_cliente"),
        joins=[dict(tipo="JOIN", alias="O", tabla="orden_servicio", orden="nro_orden",
                    on=lambda f: f["O.id_cliente"] == f["C.id_cliente"],
                    texto="O.id_cliente = C.id_cliente",
                    mirar="Después del cruce, ¿de qué hay una fila? ¿Alguna orden aparece "
                          "dos veces?")],
        group_by=["C.nombre", "C.apellido"],
        agregados=[("ordenes", "COUNT(*)")],
        select=[("nombre", "C.nombre"), ("apellido", "C.apellido"), ("ordenes", "@ordenes")],
        order_by=[("ordenes", True), ("apellido", False), ("nombre", False)],
        mirar={"GROUP BY": "Miren la columna <code>C.id_cliente</code> dentro de cada bloque. "
                           "¿Todas las filas de un grupo son del mismo cliente?",
               "agregados": "¿Qué está contando <code>COUNT(*)</code> en cada bloque?",
               "SELECT": "Al colapsar cada grupo en una fila, ¿qué columna de la tabla de "
                         "trabajo deja de verse?"}))),
)


# ── Dos consultas que hoy coinciden ────────────────────────────────────────

Q_MAX = """
SELECT nro_orden, total
FROM orden_servicio
WHERE total = (SELECT MAX(total) FROM orden_servicio);
"""
Q_LIM = """
SELECT nro_orden, total
FROM orden_servicio
ORDER BY total DESC
LIMIT 1;
"""
maximo = correr("SELECT MAX(total) FROM orden_servicio")[1][0][0]
assert correr(Q_MAX)[1] == correr(Q_LIM)[1] and cuantas(Q_MAX) == 1
assert correr(Q_MAX)[1][0][0] == 1
EMPATE = f"UPDATE orden_servicio SET total = {maximo:.2f} WHERE nro_orden = 2;\n"
assert cuantas(EMPATE + Q_MAX) == 2
# la fila que elige el LIMIT en un empate no está definida: se comprueba solo el importe
assert cuantas(EMPATE + "SELECT total FROM orden_servicio ORDER BY total DESC LIMIT 1;") == 1

ejercicio(
    "Dos caminos que hoy coinciden",
    "La orden de mayor importe",
    ["orden_servicio"],
    "<p>Para encontrar <strong>la orden de mayor importe</strong> hay dos consultas:</p>"
    + variantes(("I", Q_MAX), ("II", Q_LIM))
    + "<p>Con los datos de hoy las dos devuelven lo mismo:</p>" + tabla(Q_MAX),
    "¿En qué situación dejarían de devolver lo mismo?",
    [("En ninguna: son dos maneras de escribir la misma consulta",
      "Coinciden mientras el importe más alto lo tenga una sola orden. La I filtra por un "
      "valor y la II corta por cantidad de filas."),
     ("Si alguna orden tiene el total en NULL",
      "<code>MAX</code> saltea los NULL y el orden descendente los deja al final. Mientras "
      "haya otra orden con el total cargado, ninguna de las dos consultas llega a tomarlos."),
     ("Si dos órdenes empatan en el importe más alto",
      "La I devuelve todas las órdenes que tienen ese importe. La II devuelve una sola fila "
      "porque <code>LIMIT 1</code> corta ahí."),
     ("Si la tabla tiene una sola orden",
      "Con una sola orden, esa es la de mayor importe para las dos consultas.")],
    2,
    "Dar por equivalentes dos consultas porque coinciden sobre los datos que se tienen a la "
    "vista. Para compararlas hay que pensar qué datos podrían cargarse mañana.",
    lambda: (
        "<p>Para verlo se le pone a la orden 2 el mismo total que tiene la orden 1 y se "
        "vuelve a correr la I:</p>" + sql_html(EMPATE + Q_MAX.strip())
        + tabla(EMPATE + Q_MAX)
        + "<p>Con ese mismo cambio la II sigue devolviendo una fila. Cuál de las dos órdenes "
        "empatadas muestra depende del motor, porque el <code>ORDER BY</code> no dice cómo "
        "desempatar. Cuál conviene depende del pedido: «la orden de mayor importe» supone "
        "que hay una sola.</p>"),
    debate="Piensen qué órdenes podrían cargarse mañana y qué haría cada consulta con ellas.",
    ayuda=ayuda(
        recorrido_html(dict(
            sql=Q_MAX,
            columnas=["nro_orden", "id_cliente", "total"],
            origen=("", "orden_servicio", "nro_orden"),
            previa=dict(sql="SELECT MAX(total) FROM orden_servicio;",
                        mirar="¿Qué deja la subconsulta en el lugar del paréntesis: una "
                              "orden o un valor?"),
            where=[dict(texto=f"total = {maximo:.2f}",
                        prueba=lambda f: f["total"] == maximo,
                        mirar="¿De qué depende la cantidad de filas que pasan esta "
                              "condición?")],
            select=[("nro_orden", "nro_orden"), ("total", "total")]), "Consulta I"),
        recorrido_html(dict(
            sql=Q_LIM,
            columnas=["nro_orden", "id_cliente", "total"],
            origen=("", "orden_servicio", "nro_orden"),
            select=[("nro_orden", "nro_orden"), ("total", "total")],
            order_by=[("total", True)],
            limit=1,
            mirar={"ORDER BY": "¿Qué decide cuál queda primera entre dos filas que tienen el "
                               "mismo total?",
                   "LIMIT": "¿El <code>LIMIT</code> mira el valor de <code>total</code> "
                            "para decidir dónde cortar?"}), "Consulta II")),
)


# ---------------------------------------------------------------------------
# La página
# ---------------------------------------------------------------------------

ESTILO = """
    /* propio de esta página: la tarjeta de ejercicio con sus opciones, las
       tablas de datos compactas y el recorrido por etapas. */
    .practica { display: grid; gap: 22px; }
    .practica-intro { color: var(--text-body); line-height: 1.7; display: grid; gap: 10px; max-width: 78ch; }
    .practica-intro a, .indice-ej a { color: var(--accent); }

    .indice-ej { list-style: none; margin: 0; padding: 0; display: grid; gap: 4px;
                 grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
    .indice-ej a { text-decoration: none; display: flex; gap: 10px; align-items: baseline;
                   padding: 6px 10px; border-radius: var(--radio-chico); font-size: 0.92rem; }
    .indice-ej a:hover { background: var(--velo-medio); }
    .indice-num { font-family: 'Fira Code', monospace; color: var(--text-muted); font-size: 0.8rem; }
    .indice-mec { color: var(--text-main); }

    .barra-practica { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
    .boton { font: inherit; font-size: 0.88rem; cursor: pointer; color: var(--text-main);
             background: var(--velo-medio); border: 1px solid var(--linea-media);
             border-radius: var(--radio-chico); padding: 8px 14px; }
    .boton:hover { border-color: var(--accent); }
    .boton:focus-visible, .opc:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

    .ej { background: var(--bg-card); border: 1px solid var(--linea-media);
          border-radius: var(--radio); padding: 24px 26px; display: grid; gap: 16px;
          scroll-margin-top: 16px; min-width: 0; }
    .ej-cab { display: flex; gap: 14px; align-items: center; }
    .ej-num { font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.5rem;
              color: var(--accent); min-width: 1.6em; }
    .ej-mec { font-size: 0.76rem; letter-spacing: .1em; text-transform: uppercase;
              color: var(--accent); margin: 0 0 2px; }
    .ej h2 { font-size: 1.3rem; color: var(--text-main); margin: 0; }
    .ej p { color: var(--text-body); line-height: 1.65; margin: 0; }
    .ej-enun { display: grid; gap: 12px; min-width: 0; }
    .ej-preg { font-size: 1.08rem; color: var(--text-main); font-weight: 600; }
    .ej-sql { background: var(--bg-code); border: 1px solid var(--linea-sutil);
              border-radius: var(--radio-chico); padding: 14px 16px; margin: 0;
              font-size: 0.92rem; line-height: 1.55; overflow-x: auto; white-space: pre; }
    .ej-sql code { font-size: inherit; }

    .variantes { display: grid; gap: 10px; }
    .variante { display: grid; grid-template-columns: 2.2em minmax(0, 1fr); gap: 8px; align-items: start; }
    .variante-rot { font-family: 'Outfit', sans-serif; font-weight: 700; color: var(--text-muted);
                    padding-top: 13px; text-align: right; }

    .ej-datos { border: 1px solid var(--linea-sutil); border-radius: var(--radio-chico);
                padding: 8px 12px; background: var(--velo-sutil); }
    .ej-datos summary { cursor: pointer; font-size: 0.82rem; color: var(--text-muted); }
    .datos-fila { display: flex; flex-wrap: wrap; gap: 8px 22px; margin-top: 10px; align-items: flex-start; }
    .dato { min-width: 0; max-width: 100%; }
    .dato-nombre { font-family: 'Fira Code', monospace; font-size: 0.76rem; margin-bottom: 4px; }
    .ej .dato-nombre { color: var(--text-muted); }
    .dato-tabla { border-collapse: collapse; font-family: 'Fira Code', monospace; font-size: 0.74rem; }
    .dato-tabla th { text-align: left; color: var(--text-muted); font-weight: 500;
                     padding: 3px 9px; border-bottom: 1px solid var(--linea-media); white-space: nowrap; }
    .dato-tabla td { padding: 2px 9px; color: var(--text-body); white-space: nowrap;
                     border-bottom: 1px solid var(--linea-sutil); }
    .dato-tabla td.nulo, .etapa-tabla td.nulo { color: var(--bloque-ambar); font-style: italic; }

    .ej-opc { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
    .opc { width: 100%; display: grid; grid-template-columns: 30px minmax(0, 1fr); gap: 12px;
           align-items: center; text-align: left; font: inherit; font-size: 1rem; cursor: pointer;
           color: var(--text-main); background: var(--velo-sutil);
           border: 1px solid var(--linea-media); border-radius: var(--radio-chico); padding: 10px 14px; }
    .opc:hover { border-color: var(--accent); }
    .opc-letra { font-family: 'Fira Code', monospace; font-weight: 700; width: 28px; height: 28px;
                 display: grid; place-items: center; border-radius: 6px;
                 border: 1px solid var(--linea-media); color: var(--text-muted); }
    .opc-texto code { font-size: 0.9rem; }
    .opc.acierto { border-color: var(--bloque-verde); background: rgba(16, 185, 129, 0.10); }
    .opc.acierto .opc-letra { background: var(--bloque-verde); border-color: var(--bloque-verde); color: #06281d; }
    .opc.fallo { border-color: var(--bloque-carmin); background: rgba(244, 63, 94, 0.08); }
    .opc.fallo .opc-letra { border-color: var(--bloque-carmin); color: var(--bloque-carmin); }
    .opc-porque { font-size: 0.92rem; padding: 6px 14px 4px 56px; }
    .ej .opc-porque { color: var(--text-muted); }

    .ej-ver { justify-self: start; }
    /* display:grid le gana al atributo hidden si no se lo repone */
    .ej-res[hidden], .opc-porque[hidden] { display: none; }
    .ej-res { border-top: 1px solid var(--linea-media); padding-top: 16px; display: grid; gap: 12px; min-width: 0; }
    .ej-res h3 { font-size: 0.8rem; letter-spacing: .1em; text-transform: uppercase;
                 color: var(--bloque-verde); margin: 0; }
    .ej-ref { border: 1px solid var(--linea-media); border-left: 3px solid var(--accent);
              border-radius: 0 var(--radio-chico) var(--radio-chico) 0; padding: 10px 14px;
              display: grid; gap: 6px; }
    .ej .ref-titulo { font-size: 0.8rem; letter-spacing: .06em; text-transform: uppercase;
                      color: var(--accent); }
    .ej-ref ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap;
                 gap: 4px 26px; color: var(--text-body); }
    .ej-ref strong { font-family: 'Fira Code', monospace; color: var(--text-main); }
    .ref-rot { color: var(--text-muted); }
    .ej .ref-nota { font-size: 0.82rem; color: var(--text-muted); }
    .ej .ej-debate { border-left: 3px solid var(--accent); background: var(--velo-sutil);
                     padding: 10px 14px; border-radius: 0 var(--radio-chico) var(--radio-chico) 0; }
    .ej-debate strong { color: var(--accent); }
    .indice-debate { font-size: 0.72rem; letter-spacing: .08em; text-transform: uppercase;
                     color: var(--accent); margin-left: 6px; }
    /* la ayuda: el recorrido por etapas, con las clases del visor de
       orden-de-ejecucion.html para que se lea igual que en la clase */
    .ej-ayuda { border: 1px solid var(--linea-media); border-radius: var(--radio-chico);
                padding: 10px 14px; background: var(--velo-sutil); min-width: 0; }
    .ej-ayuda > summary { cursor: pointer; color: var(--accent); font-weight: 600; font-size: 0.95rem; }
    .ej-ayuda[open] > summary { margin-bottom: 10px; }
    .ej .ayuda-intro { font-size: 0.9rem; margin-bottom: 12px; max-width: 78ch; }
    .ayuda-intro a { color: var(--accent); }
    .recorrido { border: 1px solid var(--linea-media); border-radius: var(--radio-chico);
                 background: var(--bg-card); padding: 14px 16px; display: grid; gap: 12px;
                 min-width: 0; }
    .recorrido + .recorrido { margin-top: 12px; }
    .ej .rec-titulo { font-family: 'Outfit', sans-serif; font-weight: 700; color: var(--text-main); }
    .rec-barra { display: flex; flex-wrap: wrap; gap: 6px; }
    .rec-chip { font-family: 'Fira Code', monospace; font-size: 0.74rem; cursor: pointer;
                color: var(--text-muted); background: transparent;
                border: 1px solid var(--linea-media); border-radius: 999px; padding: 4px 10px; }
    .rec-chip:hover { color: var(--text-main); border-color: var(--accent); }
    .rec-chip[aria-current="step"] { color: #04222a; background: var(--accent);
                                     border-color: var(--accent); font-weight: 700; }
    .rec-chip:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
    .rec-etapa { min-width: 0; }
    .rec-etapa[hidden] { display: none; }
    .rec-nav { display: flex; gap: 10px; }
    .rec-nav .boton:disabled { opacity: .4; cursor: default; border-color: var(--linea-media); }
    .visor-titulo { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; margin-bottom: 4px; }
    .visor-titulo h3 { margin: 0; font-size: 1.02rem; color: var(--text-main); }
    .visor-etapa { font-family: 'Fira Code', monospace; font-size: 0.7rem; color: var(--accent);
                   border: 1px solid var(--accent); border-radius: 999px; padding: 2px 8px; }
    .ej .visor-dice { font-size: 0.9rem; margin: 8px 0 12px; }
    .ej .visor-cuenta { font-family: 'Fira Code', monospace; font-size: 0.76rem;
                        color: var(--text-muted); margin-bottom: 10px; }
    .visor-cuenta strong { color: var(--text-main); }
    .visor-cuenta .baja { color: var(--bloque-carmin); }
    .recorrido .ej-sql { margin-bottom: 10px; }
    .visor-scroll { max-height: 480px; overflow: auto; border: 1px solid var(--linea-sutil);
                    border-radius: var(--radio-chico); }
    .visor-tabla { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
    .visor-tabla th, .visor-tabla td { text-align: left; padding: 5px 10px;
                                       border-bottom: 1px solid var(--linea-sutil);
                                       font-family: 'Fira Code', ui-monospace, monospace;
                                       white-space: nowrap; }
    .visor-tabla thead th { position: sticky; top: 0; z-index: 1; background: var(--bg-theory);
                            color: var(--text-muted); font-size: 0.7rem; letter-spacing: .04em; }
    .visor-tabla td { color: var(--text-body); }
    .visor-tabla tr.se-va td { color: var(--bloque-carmin); text-decoration: line-through; }
    .visor-tabla td.nulo { color: var(--bloque-ambar); font-style: italic; opacity: .8; }
    .visor-tabla td.nuevo { color: var(--bloque-verde); }
    .visor-tabla td.pendiente { color: var(--text-muted); opacity: .45; }
    .visor-tabla tr.con-nulos td:first-child { border-left: 3px solid var(--bloque-ambar); }
    .visor-tabla tr.ida td { color: var(--text-muted); opacity: .35; text-decoration: line-through; }
    .visor-tabla tr.grupo-cab td { background: var(--velo-medio); color: var(--text-main);
                                   font-weight: 700; border-top: 1px solid var(--linea-media);
                                   padding-top: 9px; }
    .visor-tabla tr.grupo-cab .chapa { display: inline-block; width: 9px; height: 9px;
                                       border-radius: 2px; margin-right: 8px;
                                       background: var(--tono); vertical-align: middle; }
    .visor-tabla tr.del-grupo td:first-child { border-left: 3px solid var(--tono); }
    .visor-tabla tr.grupo-calc td { color: var(--text-muted); font-size: 0.75rem;
                                    white-space: normal; padding-bottom: 9px; }
    .visor-tabla tr.grupo-calc .fn { color: var(--bloque-verde); font-weight: 700; }
    .visor-tabla tr.grupo-calc .igual { color: var(--text-main); font-weight: 700; }
    .visor-salida { border-color: color-mix(in srgb, var(--bloque-verde) 40%, transparent); }
    .visor-salida .visor-tabla thead th { color: var(--bloque-verde); }
    .ej .visor-leyenda { display: flex; flex-wrap: wrap; gap: 14px; margin: 10px 0 0;
                         font-size: 0.74rem; color: var(--text-muted); }
    .visor-leyenda span::before { content: ''; display: inline-block; width: 8px; height: 8px;
                                  border-radius: 2px; margin-right: 6px; vertical-align: middle;
                                  background: currentColor; }
    .visor-leyenda .l-queda { color: var(--bloque-verde); }
    .visor-leyenda .l-sale { color: var(--bloque-carmin); }
    .visor-leyenda .l-ida { color: var(--text-muted); }
    .visor-leyenda .l-nula { color: var(--bloque-ambar); }
    .visor-nota { margin-top: 14px; padding: 10px 12px; border-left: 3px solid var(--bloque-ambar);
                  background: var(--velo-sutil); color: var(--text-body); font-size: 0.9rem; }
    .visor-nota strong { color: var(--bloque-ambar); }
    .ej-error { border-left: 3px solid var(--bloque-ambar); background: rgba(245, 158, 11, 0.07);
                padding: 10px 14px; border-radius: 0 var(--radio-chico) var(--radio-chico) 0; }
    .ej-error strong { color: var(--bloque-ambar); }
    .ej .ej-examen { font-size: 0.88rem; color: var(--text-muted); }
    .res-fila { display: flex; flex-wrap: wrap; gap: 6px 26px; align-items: flex-start; }
    .res-tabla { min-width: 0; max-width: 100%; }
    .res-tabla .result-table { width: auto; }
    .ej .res-rotulo { font-family: 'Fira Code', monospace; font-size: 0.78rem; color: var(--text-muted); }
    .ej .filas-devueltas { font-size: 0.78rem; color: var(--text-muted); font-family: 'Fira Code', monospace; }

    .etapas { display: flex; flex-wrap: wrap; gap: 10px 28px; align-items: flex-start; }
    .etapa { min-width: 0; }
    .ej .etapa-nombre { font-size: 0.82rem; color: var(--text-muted); margin-bottom: 6px; }
    .etapa-num { display: inline-grid; place-items: center; width: 1.5em; height: 1.5em;
                 border-radius: 50%; background: var(--accent); color: #04222a;
                 font-weight: 700; font-size: 0.78rem; }
    .etapa-tabla { border-collapse: collapse; font-family: 'Fira Code', monospace; font-size: 0.8rem; }
    .etapa-tabla th { text-align: left; color: var(--text-muted); font-weight: 500;
                      padding: 4px 12px; border-bottom: 1px solid var(--linea-media); }
    .etapa-tabla td { padding: 3px 12px; color: var(--text-body); }
    .etapa-tabla tr.se-va td { color: var(--bloque-carmin); text-decoration: line-through; }
    .etapa-tabla tr.grupo-cab td { background: var(--velo-medio); color: var(--text-main);
                                   font-weight: 700; border-top: 1px solid var(--linea-media); }
    .etapa-tabla tr.grupo-calc td { color: var(--text-muted); font-size: 0.76rem; padding-bottom: 8px; }
    .etapa-tabla .fn { color: var(--bloque-verde); font-weight: 700; }
    .etapa-tabla tbody.grupo td:first-child { border-left: 3px solid var(--accent); }
    .etapa-tabla tbody.se-va-grupo td { color: var(--bloque-carmin); text-decoration: line-through; }
    .etapa-tabla tbody.se-va-grupo td:first-child { border-left-color: var(--bloque-carmin); }
    .etapa-tabla tbody.se-va-grupo tr.grupo-calc td { text-decoration: none; }

    @media (max-width: 640px) {
      .ej { padding: 18px 14px; }
      .opc-porque { padding-left: 14px; }
    }
    @media print {
      .barra-practica, .ej-acciones, .ej-ayuda { display: none; }
      .ej { break-inside: avoid; }
    }
"""

GUION = """
document.querySelectorAll('.ej').forEach(function (ej) {
  var resolucion = ej.querySelector('.ej-res');
  var boton = ej.querySelector('.ej-ver');

  function abrir(ver) {
    resolucion.hidden = !ver;
    boton.textContent = ver ? 'Ocultar la resolución' : 'Ver la resolución';
    boton.setAttribute('aria-expanded', ver ? 'true' : 'false');
    if (ver) ej.querySelector('.opc[data-ok]').classList.add('acierto');
  }

  ej.querySelectorAll('.opc').forEach(function (opc) {
    opc.addEventListener('click', function () {
      opc.classList.add(opc.hasAttribute('data-ok') ? 'acierto' : 'fallo');
      opc.parentElement.querySelector('.opc-porque').hidden = false;
    });
  });

  boton.addEventListener('click', function () { abrir(resolucion.hidden); });

  ej.reiniciar = function () {
    abrir(false);
    ej.querySelectorAll('.opc').forEach(function (o) { o.classList.remove('acierto', 'fallo'); });
    ej.querySelectorAll('.opc-porque').forEach(function (p) { p.hidden = true; });
  };
});

document.querySelectorAll('.recorrido').forEach(function (rec) {
  var chips = rec.querySelectorAll('.rec-chip');
  var etapas = rec.querySelectorAll('.rec-etapa');
  var anterior = rec.querySelector('[data-ir="-1"]');
  var siguiente = rec.querySelector('[data-ir="1"]');
  var actual = 0;

  rec.ir = function (n) {
    actual = Math.max(0, Math.min(etapas.length - 1, n));
    etapas.forEach(function (e, i) { e.hidden = i !== actual; });
    chips.forEach(function (c, i) {
      if (i === actual) c.setAttribute('aria-current', 'step');
      else c.removeAttribute('aria-current');
    });
    anterior.disabled = actual === 0;
    siguiente.disabled = actual === etapas.length - 1;
  };

  chips.forEach(function (c, i) { c.addEventListener('click', function () { rec.ir(i); }); });
  anterior.addEventListener('click', function () { rec.ir(actual - 1); });
  siguiente.addEventListener('click', function () { rec.ir(actual + 1); });
  rec.ir(0);
});

document.getElementById('reiniciar').addEventListener('click', function () {
  document.querySelectorAll('.ej').forEach(function (ej) { ej.reiniciar(); });
  document.querySelectorAll('.recorrido').forEach(function (rec) { rec.ir(0); });
  document.querySelectorAll('.ej-ayuda').forEach(function (d) { d.open = false; });
  window.scrollTo({ top: 0 });
});
document.getElementById('plegar-datos').addEventListener('click', function () {
  var todas = document.querySelectorAll('.ej-datos');
  var abrir = !todas[0].open;
  todas.forEach(function (d) { d.open = abrir; });
});
"""


def tarjeta(n: int, e: dict) -> str:
    opciones = []
    for i, (texto, porque) in enumerate(e["opciones"]):
        ok = " data-ok" if i == e["correcta"] else ""
        opciones.append(
            f'<li><button type="button" class="opc"{ok}>'
            f'<span class="opc-letra">{LETRAS[i]}</span>'
            f'<span class="opc-texto">{texto}</span></button>\n'
            f'<p class="opc-porque" hidden>{porque}</p></li>')
    examen = f'<p class="ej-examen">{e["examen"]}</p>\n' if e["examen"] else ""
    debate = (f'<p class="ej-debate"><strong>Para debatir antes de elegir.</strong> '
              f'{e["debate"]}</p>\n' if e["debate"] else "")
    return (
        f'<section class="ej" id="ej-{n}" aria-labelledby="ej-{n}-titulo">\n'
        f'<div class="ej-cab"><span class="ej-num">{n}</span><div>'
        f'<p class="ej-mec">{e["mecanica"]}</p>'
        f'<h2 id="ej-{n}-titulo">{e["titulo"]}</h2></div></div>\n'
        f'{datos(*e["tablas"])}\n'
        f'<div class="ej-enun">{e["enunciado"]}</div>\n'
        f'{debate}'
        f'<p class="ej-preg">{e["pregunta"]}</p>\n'
        '<ol class="ej-opc">\n' + "\n".join(opciones) + "\n</ol>\n"
        + (e["ayuda"] + "\n" if e["ayuda"] else "") +
        '<div class="ej-acciones"><button type="button" class="boton ej-ver" '
        'aria-expanded="false">Ver la resolución</button></div>\n'
        '<div class="ej-res" hidden>\n'
        f'<h3>Respuesta: {LETRAS[e["correcta"]]}</h3>\n'
        f'{e["resolucion"]}\n'
        f'<p class="ej-error"><strong>El error al que apunta.</strong> {e["error"]}</p>\n'
        f'{examen}'
        "</div>\n</section>")


NUMEROS = ("", "Un", "Dos", "Tres", "Cuatro", "Cinco", "Seis", "Siete", "Ocho", "Nueve",
           "Diez", "Once", "Doce", "Trece", "Catorce", "Quince", "Dieciséis")


def pagina() -> str:
    cuantos = NUMEROS[len(EJERCICIOS)]
    de_debate = [n for n, e in enumerate(EJERCICIOS, 1) if e["debate"]]
    # el párrafo de la introducción los nombra como un tramo corrido al final
    assert de_debate == list(range(de_debate[0], len(EJERCICIOS) + 1))
    indice = "\n".join(
        f'<li><a href="#ej-{n}"><span class="indice-num">{n:02d}</span>'
        f'<span><span class="indice-mec">{e["mecanica"]}</span> · {e["titulo"]}'
        + ('<span class="indice-debate">debate</span>' if e["debate"] else "")
        + '</span></a></li>'
        for n, e in enumerate(EJERCICIOS, 1))
    tarjetas = "\n\n".join(tarjeta(n, e) for n, e in enumerate(EJERCICIOS, 1))
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Práctica · Los modelos de pregunta · Bases de Datos</title>
    <link rel="stylesheet" href="../../assets/css/fuentes.css">
    <link rel="stylesheet" href="../../assets/css/base.css">

    <style>{ESTILO}    </style>
</head>
<body data-tema="presentacion">
<!-- GENERADO por herramientas/generar_practica.py: los ejercicios se editan ahí. -->

    <header>
        <div class="header-container">
            <span class="badge">práctica</span>
            <h1>Los modelos de pregunta</h1>
            <p>{cuantos} ejercicios sobre El Chip para practicar cómo se va a preguntar en el recuperatorio de SQL</p>
            <a href="../../index.html" class="nav-alumno">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
                Unidad IV · SQL
            </a>
        </div>
    </header>

    <main>
        <nav class="migas" aria-label="Ubicación">
            <a href="../../index.html">Índice</a>
            <span class="sep" aria-hidden="true">›</span>
            <a href="../../index.html#u4a">Unidad IV · SQL</a>
            <span class="sep" aria-hidden="true">›</span>
            <span aria-current="page">Los modelos de pregunta</span>
        </nav>

<div class="practica">
  <div class="practica-intro">
    <p>Cada ejercicio muestra una forma de preguntar y apunta a un error que se repitió en el
       <a href="analisis-examen-sql.html">examen de SQL</a>. Todas las consultas corren: ninguna
       respuesta depende de adivinar si el motor da error. Se piensa la respuesta, se elige una
       opción y recién después se abre la resolución, que muestra la salida real de la consulta.</p>
    <p>Los datos son los de El Chip en su juego ampliado. Para probar cualquier consulta, abrí la
       <a href="../../consola.html">consola</a> y elegí <strong>2 · Compendio</strong>. El esquema
       completo está en <a href="../../casos/el-chip/modelo.html">la hoja del modelo</a>, y el
       recorrido de una consulta etapa por etapa, en
       <a href="orden-de-ejecucion.html">El orden en que corre una consulta</a>.</p>
    <p>Los ejercicios {de_debate[0]} a {de_debate[-1]} son más difíciles y se resuelven
       debatiendo en clase. Cada uno trae una consigna para discutir en grupo antes de elegir
       una opción, y el resultado de la consulta ya está a la vista. Si el grupo no avanza,
       debajo de las opciones hay una ayuda que recorre la consulta etapa por etapa, con el
       mismo método de <a href="orden-de-ejecucion.html">El orden en que corre una consulta</a>.</p>
  </div>

  <ol class="indice-ej">
{indice}
  </ol>

  <div class="barra-practica">
    <button type="button" class="boton" id="reiniciar">Empezar de nuevo</button>
    <button type="button" class="boton" id="plegar-datos">Plegar o desplegar las tablas</button>
  </div>

{tarjetas}
</div>
    </main>

<script>{GUION}</script>

</body>
</html>
"""


def contrastar() -> int:
    """Corre en MySQL todo lo que se corrió en SQLite y compara."""
    import verificar_apunte_mysql as motor

    def normal(valor):
        if valor is None or valor == "NULL":
            return "NULL"
        try:
            return round(float(valor), 2)
        except (TypeError, ValueError):
            return str(valor)

    esquema, scripts = motor.ESQUEMAS["ampliado"]
    print(f"Contraste con MySQL · armando {esquema} …")
    motor.armar(esquema, scripts)
    distintos = 0
    try:
        for sql, (columnas, filas) in REGISTRO.items():
            salida = motor.correr(esquema, sql.rstrip().rstrip(";") + ";")
            primera = " ".join(sql.split())[:70]
            if isinstance(salida, str):
                print(f"  {salida} · {primera}")
                distintos += 1
                continue
            _, del_motor = salida
            aca = sorted([str(normal(v)) for v in f] for f in filas)
            alla = sorted([str(normal(v)) for v in f] for f in del_motor)
            if aca != alla:
                print(f"  DIFIERE  {primera}")
                print(f"      página {aca}")
                print(f"      motor  {alla}")
                distintos += 1
    finally:
        motor.mysql(["-e", f"DROP SCHEMA IF EXISTS `{esquema}`;"])
    print(f"  {len(REGISTRO) - distintos} consultas coinciden, {distintos} difieren")
    return distintos


def main() -> None:
    SALIDA.write_text(pagina(), encoding="utf-8")
    letras = [LETRAS[e["correcta"]] for e in EJERCICIOS]
    reparto = " · ".join(f"{l} = {letras.count(l)}" for l in LETRAS)
    print(f"{SALIDA.name}: {len(EJERCICIOS)} ejercicios")
    print(f"  respuestas correctas: {' '.join(letras)}   ({reparto})")
    for e in RETIRADOS:
        print(f"  retirado: {e['mecanica']} · {e['titulo']} ({e['retirado']})")
    if "--mysql" in sys.argv:
        sys.exit(1 if contrastar() else 0)


if __name__ == "__main__":
    main()
