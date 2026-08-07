#!/usr/bin/env python3
"""
Arma index.html desde la biblioteca y el recorrido del ciclo.

    python herramientas/generar_indice.py            escribe index.html
    python herramientas/generar_indice.py --revisar  compara y no escribe

Tres archivos mandan:

    materiales.toml              la biblioteca; crece y no se borra
    ciclos/<año>.toml            qué material entró ese año y en qué orden
    herramientas/plantilla-indice.tpl   el armazón de la página

El material que el ciclo no nombra, pero cuyo estado es «ampliacion»,
aparece en una franja al final de su unidad. Así el alumno encuentra el
material de años anteriores donde está el tema, sin salir del recorrido.

El generador aborta si el manifiesto y el recorrido no se corresponden:
un id citado que no existe, o material vigente que nadie usa. Sin esa
verificación, en dos ciclos el manifiesto miente.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

ICONOS = {
    "presentacion": '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>',
    "base": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
    "documento": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>',
    "libro": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    "relato": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "der": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><path d="M10 6.5h4a1 1 0 0 1 1 1V14"/>',
    "codigo": '<path d="M16 18l6-6-6-6M8 6l-6 6 6 6"/>',
    "agrupacion": '<path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6"/><rect x="12" y="8" width="3" height="10"/><rect x="17" y="5" width="3" height="13"/>',
    "reporte": '<path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6"/><rect x="12" y="8" width="3" height="10"/><rect x="17" y="4" width="3" height="14"/>',
    "taller": '<rect x="3" y="3" width="18" height="18" rx="2"/><rect x="8" y="8" width="8" height="8" rx="1"/>',
    "calendario": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "consola": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M6 9l3 3-3 3M12 15h5"/>',
    "estrella": '<path d="M12 2l2.4 7.4H22l-6 4.6 2.3 7.4-6.3-4.6L5.7 21.4 8 14 2 9.4h7.6z"/>',
    "verificado": '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    "conjuntos": '<circle cx="9" cy="12" r="6"/><circle cx="15" cy="12" r="6"/>',
    "rayo": '<path d="M13 2L3 14h8l-1 8 10-12h-8z"/>',
    "musica": '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
}

FLECHA = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
          'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
          '<path d="M5 12h14M12 5l7 7-7 7"/></svg>')


def icono(nombre: str) -> str:
    cuerpo = ICONOS.get(nombre)
    if cuerpo is None:
        raise SystemExit(f"icono desconocido: {nombre!r}. Los válidos son {sorted(ICONOS)}")
    return ('<span class="rec-ico"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f"{cuerpo}</svg></span>")


def recurso(mat: dict, ampliacion: bool = False) -> str:
    marca = ""
    if mat.get("marca"):
        marca = f'<span class="marca-estado">{html.escape(mat["marca"])}</span>'
    elif ampliacion:
        marca = '<span class="marca-estado">Ampliación</span>'

    # Un solo formato va en línea; varios, uno por renglón.
    formatos = mat.get("formato", [])
    clase = lambda f: ("fmt " + f["variante"]) if f.get("variante") else "fmt"
    if len(formatos) == 1:
        f = formatos[0]
        bloque = f'<span class="formatos"><a class="{clase(f)}" href="{f["href"]}">{f["texto"]}</a></span>'
    else:
        partes = [f'          <a class="{clase(f)}" href="{f["href"]}">{f["texto"]}</a>' for f in formatos]
        bloque = '<span class="formatos">\n' + "\n".join(partes) + "\n        </span>"

    return (
        '      <div class="rec">\n'
        f"        {icono(mat['icono'])}\n"
        f'        <span class="rec-txt"><strong>{mat["titulo"]}{marca}</strong>\n'
        f'          <span>{mat["descripcion"]}</span></span>\n'
        f"        {bloque}\n"
        "      </div>"
    )


def envolver(texto: str, ancho: int, sangria: str) -> str:
    """Corta el párrafo a mano: el original está envuelto y conviene no ensuciar el diff."""
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        if actual and len(actual) + 1 + len(p) > ancho:
            lineas.append(actual)
            actual = p
        else:
            actual = f"{actual} {p}".strip()
    if actual:
        lineas.append(actual)
    return ("\n" + sangria).join(lineas)


def bloque_consola(unidad: dict) -> str:
    texto = unidad.get("consola_texto") or (
        "El Chip cargado en el navegador, sin instalar nada. Dejala abierta al lado mientras "
        "hacés los talleres. Todavía no se probó en el aula.")
    return (
        '  <div class="abrir-consola">\n'
        '    <span class="ac-ico"><svg width="21" height="21" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M6 9l3 3-3 3M12 15h5"/>'
        "</svg></span>\n"
        '    <span class="ac-txt"><strong>Abrí la base antes de empezar'
        '<span class="marca-estado">En revisión</span></strong>\n'
        f"      <span>{texto}</span></span>\n"
        '    <a class="ac-ir" href="consola.html" target="consola-elchip" rel="noopener">Abrir la consola\n'
        f"      {FLECHA}</a>\n"
        "  </div>\n"
    )


def generar(biblioteca: dict, ciclo: dict) -> str:
    por_id = {m["id"]: m for m in biblioteca["material"]}
    usados: set[str] = set()
    salida: list[str] = []
    banda_puesta: set[str] = set()
    trimestres = {t["id"]: t for t in ciclo.get("trimestre", [])}

    for u in ciclo["unidad"]:
        tid = u.get("trimestre", "")
        if tid and tid not in banda_puesta:
            t = trimestres[tid]
            banda_puesta.add(tid)
            if t.get("rotulo"):
                salida.append(f'<!--{t["rotulo"]}-->\n')
            salida.append(
                f'<div class="trimestre" id="{t["id"]}" style="--t:var(--{t["color"]})">\n'
                f'  <span class="trimestre-num">{t["numero"]}</span>\n'
                f'  <h2>{t["titulo"]}</h2>\n'
                f'  <span>{t["nota"]}</span>\n'
                "</div>\n")

        partes = []
        if u.get("rotulo"):
            partes.append(f'<!--{u["rotulo"]}-->\n')
        partes += [f'<section class="unidad" id="{u["id"]}" style="--c:var(--{u["color"]})">',
                  '  <div class="u-cab">',
                  f'    <div class="u-num">{u["numero"]}</div>',
                  '    <div class="u-tit">',
                  f'      <h3>{u["titulo"]}</h3>']
        if u.get("subtitulo"):
            partes.append(f'      <p>{u["subtitulo"]}</p>')
        partes.append("    </div>")
        if u.get("rango"):
            partes.append(f'    <div class="u-clases">{u["rango"]}</div>')
        partes.append("  </div>")
        if u.get("intro"):
            partes.append(f'  <p class="u-intro">{envolver(u["intro"], 96, "     ")}</p>')
        partes.append("")
        if u.get("consola"):
            partes.append(bloque_consola(u))

        for cl in u.get("clase", []):
            cuerpo = []
            if cl.get("numero") or cl.get("titulo"):
                cuerpo.append('  <div class="clase">')
                cuerpo.append(f'    <div class="c-cab"><span class="c-num">{cl["numero"]}</span>'
                              f'<h4>{cl["titulo"]}</h4></div>')
                if cl.get("nota"):
                    cuerpo.append(f'    <p class="c-nota">{envolver(cl["nota"], 92, "       ")}</p>')
                cuerpo.append('    <div class="recursos">')
                sangria = ""
            else:
                cuerpo.append('  <div class="recursos">')
                sangria = ""

            for mid in cl.get("materiales", []):
                if mid not in por_id:
                    raise SystemExit(f"el ciclo cita «{mid}», que no está en materiales.toml")
                usados.add(mid)
                cuerpo.append(recurso(por_id[mid]))
            if cl.get("mencion"):
                cuerpo.append('      <div class="mencion">\n        '
                              + envolver(cl["mencion"], 92, "        ") + "\n      </div>")
            for p in cl.get("pendientes", []):
                cuerpo.append(f'      <div class="pendiente"><span class="punto"></span>\n        {p}</div>')

            cuerpo.append("    </div>" if cl.get("numero") or cl.get("titulo") else "  </div>")
            if cl.get("numero") or cl.get("titulo"):
                cuerpo.append("  </div>")
            partes.append("\n".join(cuerpo) + "\n")

        # Franja de ampliación: lo que no pide este ciclo y sigue sirviendo.
        extra = [m for m in biblioteca["material"]
                 if m.get("estado") == "ampliacion" and m.get("unidad") == u["titulo"]]
        if extra:
            partes.append('  <div class="ampliacion">')
            partes.append('    <h4>Ampliación</h4>')
            partes.append('    <p>Fuera del programa de este año, sobre el mismo tema.</p>')
            partes.append('    <div class="recursos">')
            for m in extra:
                usados.add(m["id"])
                partes.append(recurso(m, ampliacion=True))
            partes.append("    </div>\n  </div>\n")

        partes.append("</section>\n")
        salida.append("\n".join(partes))

    huerfanos = [m["id"] for m in biblioteca["material"]
                 if m["id"] not in usados and m.get("estado") in ("vigente", "ampliacion")]
    if huerfanos:
        raise SystemExit("material vigente que ningún ciclo usa: " + ", ".join(huerfanos))

    return "\n".join(salida).rstrip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ciclo", default="2026")
    ap.add_argument("--revisar", action="store_true", help="compara sin escribir")
    args = ap.parse_args()

    biblioteca = tomllib.loads((RAIZ / "materiales.toml").read_text(encoding="utf-8"))
    ciclo = tomllib.loads((RAIZ / "ciclos" / f"{args.ciclo}.toml").read_text(encoding="utf-8"))
    plantilla = (RAIZ / "herramientas" / "plantilla-indice.tpl").read_text(encoding="utf-8")

    anio, mes, dia = (int(x) for x in ciclo["ciclo"]["inicio"].split("-"))
    etapas = []
    for i, e in enumerate(ciclo["etapa"]):
        if i == 0:
            etapas.append(f'  if (sem <= {e["hasta"]})      etapa = \'{e["texto"]}\';')
        elif i < len(ciclo["etapa"]) - 1:
            etapas.append(f'  else if (sem <= {e["hasta"]}) etapa = \'{e["texto"]}\';')
        else:
            etapas.append(f"  else                etapa = '{e['texto']}';")

    pagina = plantilla
    for marca, valor in [
        ("contenido", generar(biblioteca, ciclo)),
        ("ciclo_titulo", ciclo["ciclo"]["titulo"]),
        ("ciclo_semanas", str(ciclo["ciclo"]["semanas"])),
        ("ciclo_anio", str(ciclo["ciclo"]["anio"])),
        ("ciclo_inicio", f"new Date({anio}, {mes - 1}, {dia})"),
        ("ciclo_etapas", "\n".join(etapas)),
    ]:
        pagina = pagina.replace("{{" + marca + "}}", valor)

    if sobran := re.findall(r"\{\{(\w+)\}\}", pagina):
        raise SystemExit(f"marcadores sin resolver: {sobran}")

    destino = RAIZ / "index.html"
    if args.revisar:
        norma = lambda s: re.sub(r"\s+", " ", s).strip()
        actual = destino.read_text(encoding="utf-8")
        igual = norma(actual) == norma(pagina)
        print("coincide con index.html" if igual else "DIFIERE de index.html")
        sys.exit(0 if igual else 1)

    destino.write_text(pagina, encoding="utf-8")
    print(f"index.html generado · {len(biblioteca['material'])} materiales · ciclo {args.ciclo}")


if __name__ == "__main__":
    main()
