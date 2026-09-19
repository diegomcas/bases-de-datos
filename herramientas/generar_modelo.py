#!/usr/bin/env python3
"""
Arma la página del modelo de una base: los diagramas y la referencia de tablas.

    python herramientas/generar_modelo.py

Escribe casos/el-chip/modelo.html. Todo sale de casos/el-chip/ElChip.sql: los
nombres de tabla, los de columna, los tipos y las claves foráneas. Si el modelo
cambia, se corre esto de nuevo y la página no puede quedar mintiendo.

Lo único que se escribe a mano es la COMPOSICIÓN —qué tabla entra en qué
diagrama y dónde se ubica—, porque un buen diagrama es una decisión editorial,
no un volcado automático del esquema.

Criterios de dibujo (de la guía diagram-design, con los tokens del sitio):

  · Presupuesto por diagrama: 5 tablas, 6 aristas. Un esquema de 19 tablas no
    es un diagrama, son cinco: cada uno cuenta una parte.
  · Conectores ortogonales con esquinas redondeadas, nunca diagonales, y cada
    clave foránea sale de SU fila de columna y llega a SU fila de columna.
  · Dos anclajes nunca comparten un punto: se abren ±8 px sobre la fila.
  · El acento se reserva a una tabla por diagrama, la que el diagrama explica.
  · Nada de sombras; radios de 6 px; el mono solo para lo técnico.
"""

import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from modelo_esquema import leer  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
FUENTE = RAIZ / "casos" / "el-chip" / "ElChip.sql"
SALIDA = RAIZ / "casos" / "el-chip" / "modelo.html"

ANCHO_CAJA = 208
ALTO_CABECERA = 30
ALTO_FILA = 22
RADIO = 8


# ---------------------------------------------------------------------------
# La composición: qué cuenta cada diagrama
# ---------------------------------------------------------------------------

DIAGRAMAS = [
    {
        "id": "orden",
        "titulo": "La orden de trabajo",
        "bajada": "El centro del modelo. Cada orden apunta a quién la trajo, "
                  "quién la recibió y en qué estado está.",
        "focal": "orden_servicio",
        "izq": ["cliente", "empleado", "orden_estado"],
        "der": ["orden_servicio"],
        "pie": "Las tres claves foráneas de <code>orden_servicio</code> son "
               "<code>NOT NULL</code>: una orden no existe sin cliente, sin empleado y sin estado.",
    },
    {
        "id": "equipo",
        "titulo": "Qué equipo entró y con qué problema",
        "bajada": "Una orden puede traer varios equipos, y cada equipo puede entrar "
                  "con varios problemas. Esa tabla del medio guarda las tres cosas juntas.",
        "focal": "orden_servicio_has_equipo",
        "izq0": ["marca"],
        "izq": ["equipo", "problema"],
        "der": ["orden_servicio_has_equipo"],
        "pie": "La clave primaria de la tabla del medio son sus tres columnas juntas: "
               "el mismo equipo puede volver en otra orden, y en la misma orden puede "
               "tener más de un problema.",
    },
    {
        "id": "repuesto",
        "titulo": "Qué repuestos lleva cada arreglo",
        "bajada": "El catálogo de qué se necesita para resolver cada problema, "
                  "con la cantidad y lo que se cobra.",
        "focal": "problema_has_repuesto",
        "izq": ["problema", "repuesto"],
        "der": ["problema_has_repuesto"],
        "pie": "<code>precio_unitario</code> aparece en las dos tablas y no es una repetición: "
               "el de <code>repuesto</code> es el precio de hoy, y el de esta tabla es el que "
               "se cobró en ese arreglo.",
    },
    {
        "id": "pago",
        "titulo": "Cómo se pagó",
        "bajada": "Una orden se puede pagar con varios métodos a la vez: "
                  "una parte en efectivo y otra con tarjeta.",
        "focal": "orden_servicio_pago",
        "izq": ["orden_servicio", "metodo_pago"],
        "der": ["orden_servicio_pago"],
        "pie": "Por eso la clave primaria es la pareja <code>nro_orden</code> + "
               "<code>id_metodo_pago</code>: cada combinación entra una sola vez.",
        "recorta": {"orden_servicio": ["nro_orden", "total"]},
    },
    {
        "id": "contacto",
        "titulo": "Los datos de contacto",
        "bajada": "Un cliente puede tener varios teléfonos, varios correos y varias "
                  "direcciones. Las tres tablas tienen la misma forma.",
        "focal": "cliente",
        "izq": ["cliente"],
        "der": ["telefono", "email", "direccion"],
        "pie": "Cada una apunta además a su propio catálogo de tipo —"
               "<code>telefonotipo</code>, <code>emailtipo</code> y <code>direcciontipo</code>—, "
               "que son tablas de dos columnas y quedan fuera del dibujo.",
    },
]

# tablas que el mapa general agrupa en cada bloque
BLOQUES = [
    ("La orden", ["orden_servicio", "cliente", "empleado", "orden_estado", "rol"], 1),
    ("El trabajo", ["orden_servicio_has_equipo", "equipo", "marca", "problema",
                    "problema_has_repuesto", "repuesto"], 2),
    ("El cobro", ["orden_servicio_pago", "metodo_pago"], 3),
    ("El contacto", ["telefono", "email", "direccion",
                     "telefonotipo", "emailtipo", "direcciontipo"], 4),
]


# ---------------------------------------------------------------------------
# Dibujo
# ---------------------------------------------------------------------------

def esc(t) -> str:
    return html.escape(str(t))


def alto_caja(n_filas: int) -> int:
    return ALTO_CABECERA + n_filas * ALTO_FILA + 6


def caja(tabla, x, y, columnas, focal=False) -> tuple[str, dict]:
    """Devuelve el SVG de la tabla y dónde quedó cada fila de columna."""
    alto = alto_caja(len(columnas))
    clase = "dg-focal" if focal else "dg-caja"
    p = [f'<g class="{clase}">']
    # 1. máscara opaca: ningún conector se transparenta bajo la caja
    p.append(f'<rect x="{x}" y="{y}" width="{ANCHO_CAJA}" height="{alto}" rx="6" class="dg-mask"/>')
    p.append(f'<rect x="{x}" y="{y}" width="{ANCHO_CAJA}" height="{alto}" rx="6" class="dg-borde"/>')
    p.append(f'<rect x="{x}" y="{y}" width="{ANCHO_CAJA}" height="{ALTO_CABECERA}" rx="6" class="dg-banda"/>')
    p.append(f'<rect x="{x}" y="{y + ALTO_CABECERA - 6}" width="{ANCHO_CAJA}" height="6" class="dg-banda"/>')
    p.append(f'<line x1="{x}" y1="{y + ALTO_CABECERA}" x2="{x + ANCHO_CAJA}" '
             f'y2="{y + ALTO_CABECERA}" class="dg-hairline"/>')
    p.append(f'<text x="{x + 10}" y="{y + 20}" class="dg-tabla">{esc(tabla.nombre)}</text>')

    filas = {}
    for i, col in enumerate(columnas):
        c = tabla.columna(col)
        fy = y + ALTO_CABECERA + i * ALTO_FILA
        centro = fy + ALTO_FILA / 2
        filas[col] = centro
        if i % 2:
            p.append(f'<rect x="{x + 1}" y="{fy}" width="{ANCHO_CAJA - 2}" '
                     f'height="{ALTO_FILA}" class="dg-fila-par"/>')
        clase_col = "dg-col dg-col-clave" if (c.pk or c.fk) else "dg-col"
        p.append(f'<text x="{x + 10}" y="{centro + 3.5}" class="{clase_col}">{esc(col)}</text>')
        p.append(f'<text x="{x + ANCHO_CAJA - 10}" y="{centro + 3.5}" class="dg-tipo" '
                 f'text-anchor="end">{esc(c.tipo.lower())}</text>')
        marcas = [m for m in c.marcas if m in ("PK", "FK")]
        if marcas:
            ancho = 17 * len(marcas) + 2 * (len(marcas) - 1)
            mx = x + ANCHO_CAJA - 10 - 7.2 * len(c.tipo) - 8 - ancho
            for j, marca in enumerate(marcas):
                p.append(f'<rect x="{mx + j * 19}" y="{centro - 6}" width="17" height="12" '
                         f'rx="2" class="dg-chip dg-chip-{marca.lower()}"/>')
                p.append(f'<text x="{mx + j * 19 + 8.5}" y="{centro + 3}" '
                         f'class="dg-chip-txt" text-anchor="middle">{marca}</text>')
    p.append("</g>")
    return "\n".join(p), filas


def codo(x1, y1, x2, y2, salida="derecha") -> str:
    """Ruta ortogonal con esquinas redondeadas. Nunca una diagonal."""
    if abs(y1 - y2) < 1:
        return f"M {x1} {y1} L {x2} {y2}"
    mx = (x1 + x2) / 2
    r = min(RADIO, abs(x2 - x1) / 2, abs(y2 - y1) / 2)
    baja = y2 > y1
    hx = 1 if x2 > x1 else -1
    vy = 1 if baja else -1
    return (f"M {x1} {y1} "
            f"L {mx - r * hx} {y1} "
            f"Q {mx} {y1} {mx} {y1 + r * vy} "
            f"L {mx} {y2 - r * vy} "
            f"Q {mx} {y2} {mx + r * hx} {y2} "
            f"L {x2} {y2}")


def diagrama(tablas, spec) -> str:
    """Compone el diagrama. Las posiciones se calculan: apilar a mano lleva a
    que una caja de cinco columnas se monte sobre la de abajo."""
    tres = bool(spec.get("izq0"))
    ancho = 850 if tres else 590
    carriles = ([(spec.get("izq0", []), 24), (spec["izq"], 320), (spec["der"], 616)]
                if tres else
                [(spec["izq"], 24), (spec["der"], 330)])
    aire = 26      # entre dos cajas del mismo carril
    margen = 18

    def alto_columna(nombres):
        alto = 0
        for n in nombres:
            cols = spec.get("recorta", {}).get(n) or tablas[n].columnas
            alto += alto_caja(len(cols)) + aire
        return alto - aire if nombres else 0

    alto_contenido = max(alto_columna(n) for n, _ in carriles)
    alto = alto_contenido + margen * 2

    puestas = {}
    for nombres, x in carriles:
        y = margen + (alto_contenido - alto_columna(nombres)) / 2
        for n in nombres:
            t_ = tablas[n]
            columnas = spec.get("recorta", {}).get(n) or [c.nombre for c in t_.columnas]
            puestas[n] = (x, round(y), columnas, t_)
            y += alto_caja(len(columnas)) + aire

    partes = [f'<svg viewBox="0 0 {ancho} {round(alto)}" class="dg" role="img" '
              f'aria-label="{esc(spec["titulo"])}">',
              '<defs><marker id="dg-punta" markerWidth="7" markerHeight="6" '
              'refX="6.5" refY="3" orient="auto">'
              '<polygon points="0 0, 7 3, 0 6" class="dg-punta"/></marker></defs>']

    # los conectores primero: las cajas se pintan encima
    anclajes: dict[tuple, int] = {}
    for nombre, (x, y, columnas, t_) in puestas.items():
        for col in columnas:
            c = t_.columna(col)
            if not c.fk or c.fk[0] not in puestas:
                continue
            destino, col_destino = c.fk
            dx, dy, dcols, _ = puestas[destino]
            if col_destino not in dcols:
                continue
            oy = y + ALTO_CABECERA + columnas.index(col) * ALTO_FILA + ALTO_FILA / 2
            ey = dy + ALTO_CABECERA + dcols.index(col_destino) * ALTO_FILA + ALTO_FILA / 2
            # dos claves que llegan a la misma fila se abren, para que ninguna
            # tape a la otra en el punto de anclaje
            clave = (destino, col_destino)
            n_previas = anclajes.get(clave, 0)
            anclajes[clave] = n_previas + 1
            if n_previas:
                ey += 7 if n_previas % 2 else -7
            if x > dx:
                ox, ex = x, dx + ANCHO_CAJA
            else:
                ox, ex = x + ANCHO_CAJA, dx
            partes.append(f'<path d="{codo(ox, oy, ex, ey)}" class="dg-fk" '
                          f'marker-end="url(#dg-punta)"/>')

    for nombre, (x, y, columnas, t_) in puestas.items():
        svg, _ = caja(t_, x, y, columnas, focal=(nombre == spec["focal"]))
        partes.append(svg)

    partes.append("</svg>")
    return chr(10).join(partes)


def mapa_general(tablas) -> str:
    ancho, alto = 590, 250
    p = [f'<svg viewBox="0 0 {ancho} {alto}" class="dg" role="img" '
         f'aria-label="Mapa general del modelo">']
    pos = {"La orden": (200, 95), "El trabajo": (30, 20),
           "El cobro": (400, 20), "El contacto": (400, 175)}
    caja_w, caja_h = 160, 56
    centro = (200 + caja_w / 2, 95 + caja_h / 2)
    for nombre, (x, y) in pos.items():
        if nombre == "La orden":
            continue
        cx, cy = x + caja_w / 2, y + caja_h / 2
        ox = centro[0] + (caja_w / 2 if cx > centro[0] else -caja_w / 2)
        ex = x + (0 if cx > centro[0] else caja_w)
        p.append(f'<path d="{codo(ox, centro[1], ex, cy)}" class="dg-fk"/>')
    for nombre, miembros, _ in BLOQUES:
        x, y = pos[nombre]
        focal = nombre == "La orden"
        p.append(f'<g class="{"dg-focal" if focal else "dg-caja"}">')
        p.append(f'<rect x="{x}" y="{y}" width="{caja_w}" height="{caja_h}" rx="6" class="dg-mask"/>')
        p.append(f'<rect x="{x}" y="{y}" width="{caja_w}" height="{caja_h}" rx="6" class="dg-borde"/>')
        p.append(f'<text x="{x + caja_w / 2}" y="{y + 23}" class="dg-tabla" '
                 f'text-anchor="middle">{esc(nombre)}</text>')
        p.append(f'<text x="{x + caja_w / 2}" y="{y + 41}" class="dg-tipo" '
                 f'text-anchor="middle">{len(miembros)} tablas</text>')
        p.append("</g>")
    p.append("</svg>")
    return "\n".join(p)



# ---------------------------------------------------------------------------
# La referencia que los apuntes muestran sin salir de la página
# ---------------------------------------------------------------------------

# Las tablas de contacto y los catálogos de tipo no aparecen en los ejemplos de
# los apuntes; la hoja del modelo las tiene todas.
EN_LOS_APUNTES = ["cliente", "orden_servicio", "orden_estado", "empleado",
                  "equipo", "marca", "problema", "repuesto", "metodo_pago",
                  "orden_servicio_pago", "orden_servicio_has_equipo",
                  "problema_has_repuesto", "telefono", "email"]

APUNTES = ["unidades/04-sql/apunte-sql.html", "unidades/04-sql/apunte-sql-2.html"]


def fichas_compactas(tablas) -> str:
    """El mismo contenido que la hoja del modelo, en versión corta.

    Se escribe desde el esquema, no a mano: así el apunte no puede quedar
    nombrando una columna que la base ya no tiene."""
    piezas = ['<div class="fichas-tablas">']
    for nombre in EN_LOS_APUNTES:
        t = tablas[nombre]
        piezas.append('  <div class="ficha-tabla">')
        piezas.append(f'    <h4>{esc(nombre)}</h4>')
        piezas.append("    <ul>")
        for c in t.columnas:
            if c.pk and c.fk:
                marca = '<span class="pk">%s</span> <span class="fk">↗</span>' % esc(c.nombre)
            elif c.pk:
                marca = '<span class="pk">%s</span>' % esc(c.nombre)
            elif c.fk:
                marca = '<span class="fk">%s</span>' % esc(c.nombre)
            else:
                marca = esc(c.nombre)
            piezas.append(f"      <li>{marca}</li>")
        piezas.append("    </ul>")
        piezas.append("  </div>")
    piezas.append("</div>")
    piezas.append('<p>El modelo entero —las {n} tablas, con los tipos de cada columna y los '
                  'diagramas de cómo se unen— está en <a href="../../casos/el-chip/modelo.html">'
                  'la hoja del modelo</a>.</p>'.format(n=len(tablas)))
    return chr(10).join(piezas)


def poner_en_los_apuntes(tablas) -> int:
    bloque = fichas_compactas(tablas)
    tocados = 0
    for ruta in APUNTES:
        p = RAIZ / ruta
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8")
        ini = txt.find("<div data-fichas>")
        if ini == -1:
            continue
        fin = txt.index("</div>", ini)
        # el cierre correcto es el del propio marcador, que está vacío o trae
        # lo que escribimos la vez anterior: se busca contando anidamiento
        prof, i = 1, ini + len("<div data-fichas>")
        import re as _re
        for m in _re.finditer("<(/?)div[ >/]", txt[i:]):
            prof += -1 if m.group(1) else 1
            if prof == 0:
                fin = i + m.start()
                break
        txt = txt[:ini] + "<div data-fichas>" + chr(10) + bloque + chr(10) + txt[fin:]
        p.write_text(txt, encoding="utf-8")
        tocados += 1
    return tocados


# ---------------------------------------------------------------------------
# La página
# ---------------------------------------------------------------------------

def ficha(t) -> str:
    filas = []
    for c in t.columnas:
        marcas = " ".join(f'<span class="marca-{m.lower()}">{m}</span>' for m in c.marcas)
        destino = (f'<span class="apunta">→ {esc(c.fk[0])}.{esc(c.fk[1])}</span>'
                   if c.fk else "")
        filas.append(f"<tr><td><code>{esc(c.nombre)}</code></td>"
                     f"<td><code>{esc(c.tipo.lower())}</code></td>"
                     f"<td>{marcas} {destino}</td></tr>")
    return (f'<div class="tabla-modelo" id="t-{esc(t.nombre)}">\n'
            f'  <h4><code>{esc(t.nombre)}</code></h4>\n'
            f'  <table class="tabla-apunte">\n'
            f'    <thead><tr><th>Columna</th><th>Tipo</th><th>Claves</th></tr></thead>\n'
            f'    <tbody>\n      ' + "\n      ".join(filas) + "\n    </tbody>\n  </table>\n</div>")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    tablas = leer(FUENTE)

    secciones = []
    for spec in DIAGRAMAS:
        secciones.append(
            f'<section class="bloque-modelo" id="{spec["id"]}">\n'
            f'  <h3>{spec["titulo"]}</h3>\n'
            f'  <p>{spec["bajada"]}</p>\n'
            f'  <figure class="figura-modelo">\n{diagrama(tablas, spec)}\n'
            f'    <figcaption>{spec["pie"]}</figcaption>\n  </figure>\n</section>'
        )

    orden_fichas = [n for _, miembros, _ in BLOQUES for n in miembros]
    fichas = "\n".join(ficha(tablas[n]) for n in orden_fichas if n in tablas)

    total_fk = sum(1 for t in tablas.values() for c in t.columnas if c.fk)
    plantilla = (RAIZ / "herramientas" / "plantilla-modelo.html").read_text(encoding="utf-8")
    pagina = (plantilla
              .replace("{{MAPA}}", mapa_general(tablas))
              .replace("{{DIAGRAMAS}}", "\n\n".join(secciones))
              .replace("{{FICHAS}}", fichas)
              .replace("{{N_TABLAS}}", str(len(tablas)))
              .replace("{{N_FK}}", str(total_fk)))
    SALIDA.write_text(pagina, encoding="utf-8")
    print(f"{SALIDA.relative_to(RAIZ)}: {len(tablas)} tablas, {total_fk} claves foráneas, "
          f"{len(DIAGRAMAS)} diagramas")
    n = poner_en_los_apuntes(tablas)
    print(f"referencia puesta en {n} apunte(s), con {len(EN_LOS_APUNTES)} tablas")


if __name__ == "__main__":
    main()
