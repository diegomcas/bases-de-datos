#!/usr/bin/env python3
"""
Arma las páginas de los ciclos: una por año más el listado.

    python herramientas/generar_ciclos.py

Cada ciclo se conserva como recorrido, no como copia: la página lista qué
material entró ese año y en qué orden, y enlaza al material vivo. Si un
taller se corrige en 2028, el recorrido de 2026 apunta a la versión
corregida, que es lo que un alumno quiere encontrar.

Lee materiales.toml y todos los ciclos/<año>.toml. Aborta si un ciclo cita
material que no existe.
"""

from __future__ import annotations

import html
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CICLOS = RAIZ / "ciclos"

CABEZA = """<!DOCTYPE html>
<!-- ============================================================
     GENERADO por herramientas/generar_ciclos.py — no editar acá.
     Los datos salen de materiales.toml y de ciclos/<año>.toml.
     ============================================================ -->
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo} · Bases de Datos</title>
<link rel="stylesheet" href="{sube}assets/css/fuentes.css">
<link rel="stylesheet" href="{sube}assets/css/base.css">
<link rel="stylesheet" href="{sube}assets/css/apunte.css">
<link rel="stylesheet" href="{sube}assets/css/documento.css">
</head>
<body data-tema="apunte">

<header>
  <div class="header-container">
    <span class="badge">{insignia}</span>
    <h1>{h1}</h1>
    <p>{bajada}</p>
    <a href="{sube}index.html" class="nav-alumno">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
      Índice de la materia
    </a>
  </div>
</header>

<main>
"""

PIE = """
</main>

<!-- GENERADO por herramientas/generar_ciclos.py — no editar a mano.
     Los datos salen de materiales.toml y de ciclos/<año>.toml. -->
<footer>
  <p><strong>Bases de Datos</strong> · el material de cada año se conserva y se sigue corrigiendo</p>
  <p style="margin-top:12px;font-size:.82rem">
    Material bajo licencia
    <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es" rel="license">CC BY-NC-SA 4.0</a>
    · se puede usar y adaptar citando la fuente, sin fines comerciales.</p>
</footer>

</body>
</html>
"""


def e(s: str) -> str:
    return html.escape(str(s), quote=False)


def enlace_material(mat: dict) -> str:
    """El primer formato es el principal; desde ciclos/ hay que subir un nivel."""
    formatos = mat.get("formato", [])
    if not formatos:
        return e(mat["titulo"])
    principal = next((f for f in formatos if f.get("variante") == "principal"), formatos[0])
    return f'<a href="../{principal["href"]}">{e(mat["titulo"])}</a>'


def pagina_ciclo(ciclo: dict, por_id: dict) -> str:
    meta = ciclo["ciclo"]
    anio = meta["anio"]
    trimestres = {t["id"]: t for t in ciclo.get("trimestre", [])}

    usados = []
    for u in ciclo["unidad"]:
        for cl in u.get("clase", []):
            usados.extend(cl.get("materiales", []))

    faltan = [m for m in usados if m not in por_id]
    if faltan:
        raise SystemExit(f"ciclo {anio}: cita material inexistente {faltan}")

    partes = [CABEZA.format(
        titulo=f"Ciclo {anio}", sube="../", insignia=f"Ciclo {anio}",
        h1=f"El recorrido del ciclo {anio}",
        bajada=("Qué material entró ese año y en qué orden. Los enlaces llevan al material vivo: "
                "si algo se corrigió después, acá se ve corregido."))]

    partes.append('  <article class="apunte">')
    partes.append('    <div class="cifras">')
    for valor, etiqueta, color in [
        (meta["semanas"], "semanas de cursada", "bloque-azul"),
        (len([u for u in ciclo["unidad"] if u.get("rango")]), "unidades del programa", "bloque-violeta"),
        (sum(len(u.get("clase", [])) for u in ciclo["unidad"]), "bloques de clase", "bloque-verde"),
        (len(set(usados)), "piezas de material", "bloque-ambar"),
    ]:
        partes.append(f'      <div class="cifra" style="--c:var(--{color})">'
                      f"<b>{valor}</b><span>{etiqueta}</span></div>")
    partes.append("    </div>")

    banda = None
    for u in ciclo["unidad"]:
        tid = u.get("trimestre", "")
        if tid and tid != banda:
            banda = tid
            t = trimestres[tid]
            partes.append(f'    <h2>{e(t["numero"])} · {e(t["titulo"])}</h2>')
            partes.append(f"    <p>{e(t['nota'])}</p>")
        elif not tid and banda != "sin":
            banda = "sin"
            partes.append("    <h2>Material permanente</h2>")
            partes.append("    <p>Lo que acompaña todo el año, sin caer en una semana.</p>")

        # El número solo se antepone si ordena; los símbolos no dicen nada.
        prefijo = f'{e(u["numero"])} · ' if u.get("numero", "").strip("◆★ ") else ""
        rango = f" <em>({e(u['rango'])})</em>" if u.get("rango") else ""
        partes.append(f'    <h3>{prefijo}{e(u["titulo"])}{rango}</h3>')
        if u.get("subtitulo"):
            partes.append(f"    <p>{e(u['subtitulo'])}</p>")

        partes.append("    <ul>")
        for cl in u.get("clase", []):
            rotulo = " · ".join(x for x in (cl.get("numero"), cl.get("titulo")) if x)
            enlaces = [enlace_material(por_id[m]) for m in cl.get("materiales", [])]
            detalle = ""
            if enlaces:
                detalle = " — " + ", ".join(enlaces)
            elif cl.get("mencion"):
                detalle = ' — <span class="est est-dec">se nombra</span>'
            elif cl.get("pendientes"):
                detalle = ' — <span class="est est-par">en preparación</span>'
            partes.append(f"      <li><strong>{e(rotulo) if rotulo else 'Material'}</strong>{detalle}</li>")
        partes.append("    </ul>")

    # Lo que no entró en este ciclo y sigue publicado.
    fuera = [m for m in por_id.values()
             if m["id"] not in usados and m.get("estado") in ("vigente", "ampliacion")]
    if fuera:
        partes.append('    <div class="anexo">')
        partes.append('      <span class="anexo-rotulo">Fuera de este recorrido</span>')
        partes.append("      <h2>Material que este ciclo no usó</h2>")
        partes.append("      <p>Sigue publicado y disponible como ampliación.</p>")
        partes.append("      <ul>")
        for m in fuera:
            partes.append(f"        <li>{enlace_material(m)} — {e(m['descripcion'])}</li>")
        partes.append("      </ul>\n    </div>")

    partes.append("  </article>")
    return "\n".join(partes) + PIE


def pagina_listado(ciclos: list[dict]) -> str:
    partes = [CABEZA.format(
        titulo="Los ciclos", sube="../", insignia="Historia de la materia",
        h1="Los ciclos",
        bajada=("Cada año tiene su recorrido. El material no se duplica: los recorridos viejos "
                "apuntan a la versión vigente de cada pieza."))]
    partes.append('  <article class="apunte">')
    partes.append("    <ul>")
    for c in sorted(ciclos, key=lambda x: -x["ciclo"]["anio"]):
        meta = c["ciclo"]
        n = sum(len(cl.get("materiales", [])) for u in c["unidad"] for cl in u.get("clase", []))
        partes.append(f'      <li><strong><a href="{meta["anio"]}.html">Ciclo {meta["anio"]}</a></strong>'
                      f" — {meta['semanas']} semanas, {n} piezas de material.</li>")
    partes.append("    </ul>")
    partes.append("  </article>")
    return "\n".join(partes) + PIE


def main() -> None:
    biblioteca = tomllib.loads((RAIZ / "materiales.toml").read_text(encoding="utf-8"))
    por_id = {m["id"]: m for m in biblioteca["material"]}

    ciclos = []
    for archivo in sorted(CICLOS.glob("*.toml")):
        ciclo = tomllib.loads(archivo.read_text(encoding="utf-8"))
        ciclos.append(ciclo)
        destino = CICLOS / f"{ciclo['ciclo']['anio']}.html"
        destino.write_text(pagina_ciclo(ciclo, por_id), encoding="utf-8")
        print(f"  {destino.relative_to(RAIZ)}")

    (CICLOS / "index.html").write_text(pagina_listado(ciclos), encoding="utf-8")
    print(f"  ciclos/index.html · {len(ciclos)} ciclo(s)")


if __name__ == "__main__":
    main()
