#!/usr/bin/env python3
"""
Revisa el sitio antes de publicarlo.

    python herramientas/verificar.py

Devuelve 0 si está todo bien y 1 si algo falla, así sirve para correrlo
antes de un commit. Ocho comprobaciones:

    1  los enlaces internos resuelven
    2  cada ejercicio y su resolución se apuntan entre sí
    3  los nombres de archivo sirven como URL
    4  no hay dos rutas que difieran solo en mayúsculas
    5  toda clase CSS usada está definida en alguna hoja que la página carga
    6  el manifiesto y los archivos se corresponden
    7  el índice está al día respecto del manifiesto
    8  nada privado quedó versionado

La 5 mira, para cada página, solo las hojas que esa página enlaza. Un
verificador que compare contra una lista fija de hojas empieza a mentir
apenas se agrega una hoja nueva, que es lo que pasó con consola.css.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

RAIZ = Path(__file__).resolve().parent.parent

# Carpetas que no forman parte del sitio publicado.
FUERA = {"_backup", "_archivo", "_docente", "__pycache__", "Alumnos", "TP",
         "Examenes", ".git", "herramientas"}

# Lo que nunca puede estar versionado: datos de alumnos, material docente y
# el programa analítico, que es un documento institucional de la escuela.
PRIVADO = ("Alumnos/", "TP/", "Examenes/", "_docente/", "_backup/", "_archivo/",
           "descargas/programa-analitico.pdf", "respuesta_yolanda.txt")

fallas: list[str] = []

# La consola de Windows suele venir en cp1252 y se atraganta con los acentos.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass


def titulo(n: int, texto: str) -> None:
    print(f"\n{n}. {texto.upper()}")
    print("-" * 66)


def sin_ejemplos(txt: str) -> str:
    """Dentro de <pre> puede haber HTML de muestra que no son enlaces reales."""
    return re.sub(r"<pre[^>]*>.*?</pre>", "", txt, flags=re.DOTALL)


def del_sitio() -> list[Path]:
    salida = []
    for p in RAIZ.rglob("*"):
        if p.is_file() and not any(x in p.relative_to(RAIZ).parts for x in FUERA):
            salida.append(p)
    return salida


def main() -> None:
    archivos = del_sitio()
    reales = {p.relative_to(RAIZ).as_posix().lower() for p in archivos}
    htmls = [p for p in archivos if p.suffix == ".html"]

    # ---- 1. enlaces ----------------------------------------------------
    titulo(1, "enlaces internos")
    total = rotos = 0
    for h in htmls:
        txt = sin_ejemplos(h.read_text(encoding="utf-8"))
        for _, valor in re.findall(r'(href|src)="([^"]*)"', txt):
            if not valor or valor.startswith(("#", "http", "mailto:", "data:")):
                continue
            ruta = unquote(valor.split("#")[0])
            if not ruta:
                continue
            total += 1
            destino = (h.parent / ruta).resolve()
            try:
                rel = destino.relative_to(RAIZ).as_posix().lower()
            except ValueError:
                rel = ""
            if rel not in reales:
                print(f"  ROTO  {h.relative_to(RAIZ)} -> {valor}")
                rotos += 1
    print(f"  {total} enlaces, {rotos} rotos")
    if rotos:
        fallas.append(f"{rotos} enlaces rotos")

    # ---- 2. anclas ejercicio ↔ resolución -------------------------------
    titulo(2, "saltos entre consigna y resolución")
    saltos = colgados = 0
    for h in htmls:
        txt = h.read_text(encoding="utf-8")
        for destino, ancla in re.findall(r'href="([^"#]*\.html)#(reto-[\w-]+)"', txt):
            saltos += 1
            objetivo = h.parent / destino
            if not objetivo.exists() or f'id="{ancla}"' not in objetivo.read_text(encoding="utf-8"):
                print(f"  COLGADO  {h.name} -> {destino}#{ancla}")
                colgados += 1
    print(f"  {saltos} saltos, {colgados} colgados")
    if colgados:
        fallas.append(f"{colgados} saltos colgados")

    # ---- 3. nombres aptos para URL --------------------------------------
    titulo(3, "nombres de archivo")
    malos = [p.relative_to(RAIZ).as_posix() for p in archivos
             if re.search(r"[ áéíóúñÁÉÍÓÚÑ¿?¡!#%&]", p.name)]
    for m in malos:
        print(f"  RARO  {m}")
    print(f"  {len(archivos)} archivos, {len(malos)} con nombre problemático")
    if malos:
        fallas.append(f"{len(malos)} nombres problemáticos")

    # ---- 4. colisiones de mayúsculas ------------------------------------
    titulo(4, "mayúsculas · GitHub Pages corre en Linux")
    porminuscula = defaultdict(list)
    for p in archivos:
        porminuscula[p.relative_to(RAIZ).as_posix().lower()].append(p.relative_to(RAIZ).as_posix())
    choques = {k: v for k, v in porminuscula.items() if len(set(v)) > 1}
    for k, v in choques.items():
        print(f"  CHOQUE  {v}")
    print(f"  {len(choques)} colisiones")
    if choques:
        fallas.append(f"{len(choques)} colisiones de mayúsculas")

    # ---- 5. clases CSS ---------------------------------------------------
    titulo(5, "clases CSS")
    def selectores(css: str) -> set[str]:
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
        return set(re.findall(r"\.([a-zA-Z][\w-]*)", css))

    cache: dict[Path, set[str]] = {}
    sin_estilo = 0
    for h in htmls:
        txt = h.read_text(encoding="utf-8")
        definidas: set[str] = set()
        for hoja in re.findall(r'<link rel="stylesheet" href="([^"]+)"', txt):
            ruta = (h.parent / hoja).resolve()
            if ruta.exists():
                if ruta not in cache:
                    cache[ruta] = selectores(ruta.read_text(encoding="utf-8"))
                definidas |= cache[ruta]
        for propio in re.findall(r"<style>(.*?)</style>", txt, re.DOTALL):
            definidas |= selectores(propio)

        # El JS de la página construye HTML con class="..." adentro de cadenas;
        # eso no son clases del documento y hay que sacarlo antes de mirar.
        marcado = re.sub(r"<script[^>]*>.*?</script>", "", txt, flags=re.DOTALL)
        usadas: set[str] = set()
        for valor in re.findall(r'class="([^"]*)"', marcado):
            usadas |= {c for c in valor.split() if re.fullmatch(r"[a-zA-Z][\w-]*", c)}
        huerfanas = sorted(usadas - definidas)
        if huerfanas:
            print(f"  {h.relative_to(RAIZ)}")
            print(f"      sin estilo: {', '.join(huerfanas)}")
            sin_estilo += len(huerfanas)
    print(f"  {len(htmls)} páginas, {sin_estilo} clases sin estilo")
    if sin_estilo:
        fallas.append(f"{sin_estilo} clases sin estilo")

    # ---- 6. manifiesto ↔ archivos ---------------------------------------
    titulo(6, "manifiesto")
    biblioteca = tomllib.loads((RAIZ / "materiales.toml").read_text(encoding="utf-8"))
    por_id = {m["id"]: m for m in biblioteca["material"]}
    problemas = 0
    for m in biblioteca["material"]:
        for f in m.get("formato", []):
            if not (RAIZ / f["href"]).exists():
                print(f"  FALTA  {m['id']} apunta a {f['href']}")
                problemas += 1
    citados: set[str] = set()
    for archivo in sorted((RAIZ / "ciclos").glob("*.toml")):
        ciclo = tomllib.loads(archivo.read_text(encoding="utf-8"))
        for u in ciclo["unidad"]:
            for cl in u.get("clase", []):
                for mid in cl.get("materiales", []):
                    citados.add(mid)
                    if mid not in por_id:
                        print(f"  FANTASMA  {archivo.name} cita «{mid}»")
                        problemas += 1
    sueltos = [m["id"] for m in biblioteca["material"]
               if m["id"] not in citados and m.get("estado") == "vigente"]
    for s in sueltos:
        print(f"  SUELTO  «{s}» está vigente y ningún ciclo lo usa")
        problemas += 1
    print(f"  {len(por_id)} materiales, {len(citados)} citados, {problemas} problemas")
    if problemas:
        fallas.append(f"{problemas} problemas de manifiesto")

    # ---- 7. índice al día ------------------------------------------------
    titulo(7, "índice al día")
    r = subprocess.run([sys.executable, str(RAIZ / "herramientas" / "generar_indice.py"), "--revisar"],
                       capture_output=True, text=True)
    print("  " + (r.stdout.strip() or r.stderr.strip()))
    if r.returncode:
        fallas.append("el índice quedó desactualizado; correr generar_indice.py")

    # ---- 8. nada privado versionado --------------------------------------
    titulo(8, "nada privado versionado")
    versionados = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                                 cwd=RAIZ).stdout.split("\n")
    filtrados = [v for v in versionados if any(v.startswith(p) or v == p for p in PRIVADO)]
    for f in filtrados:
        print(f"  EXPUESTO  {f}")
    print(f"  {len(versionados)} archivos versionados, {len(filtrados)} que no deberían estarlo")
    if filtrados:
        fallas.append(f"{len(filtrados)} archivos privados versionados")

    # ---- veredicto --------------------------------------------------------
    print("\n" + "═" * 66)
    if fallas:
        print("HAY QUE REVISAR:")
        for f in fallas:
            print(f"  · {f}")
        sys.exit(1)
    print("Todo en orden.")


if __name__ == "__main__":
    main()
