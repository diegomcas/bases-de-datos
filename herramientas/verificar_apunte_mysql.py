#!/usr/bin/env python3
"""
Corre contra MySQL las consultas de un apunte y compara cada salida con la
tabla que está publicada en la página.

    python herramientas/verificar_apunte_mysql.py unidades/04-sql/apunte-sql.html

generar_apunte.py arma las tablas con SQLite, que alcanza para el SQL de
consulta y no necesita un servidor. Esto es el control contra el motor de
verdad: el que usan los alumnos y el que corrige el examen. Conviene correrlo
antes de publicar cambios en los ejemplos.

Opciones:

    --login-path=NOMBRE   el login-path de MySQL (por defecto, «prueba»).
                          Se crea una sola vez, en una ventana aparte:
                          mysql_config_editor set --login-path=prueba
                              --user=root --password
    --escribir            además, arma las tablas de los ejemplos marcados con
                          data-motor="mysql", que SQLite no puede reproducir
                          (el contador de AUTO_INCREMENT, por ejemplo)
    --dejar               no borra los esquemas de prueba al terminar

Trabaja en dos esquemas propios, el_chip_ap_base y el_chip_ap_amp, armados con
copias de los scripts del repo con el nombre del esquema cambiado: la base
el_chip que ya esté cargada no se toca. Al terminar los borra.
"""

import html
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
CASO = RAIZ / "casos" / "el-chip"
MYSQL = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

ESQUEMAS = {
    "base": ("el_chip_ap_base", ["ElChip.sql", "poblar_elchip.sql"]),
    "ampliado": ("el_chip_ap_amp", ["ElChip.sql", "poblar_elchip.sql",
                                    "poblar_elchip_compendio.sql"]),
}

login = "prueba"


def mysql(argumentos: list[str], entrada: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [MYSQL, f"--login-path={login}", "--default-character-set=utf8mb4"] + argumentos,
        input=entrada, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def armar(esquema: str, scripts: list[str]) -> None:
    for nombre in scripts:
        texto = (CASO / nombre).read_text(encoding="utf-8").replace("el_chip", esquema)
        r = mysql([], entrada=texto)
        if r.returncode != 0:
            print("\n  ERROR al cargar", nombre, "\n ", r.stderr.strip()[:500])
            sys.exit(1)


def preparar() -> None:
    for esquema, scripts in ESQUEMAS.values():
        print(f"  armando {esquema} …", end=" ", flush=True)
        armar(esquema, scripts)
        print("listo")


ESCRIBE = re.compile(
    r"\b(INSERT|UPDATE|DELETE|REPLACE|CREATE|ALTER|DROP|TRUNCATE|CALL|SAVEPOINT)\b", re.I)


def rearmar_si_escribe(etiqueta: str, sql: str) -> None:
    """El ROLLBACK devuelve las filas, pero no el contador de AUTO_INCREMENT.

    Dos ejemplos que insertan en la misma tabla se pisarían: el segundo
    recibiría un id más alto que el que muestra la página. Antes de cada
    ejemplo que escribe, el esquema se arma de nuevo."""
    if ESCRIBE.search(sql):
        esquema, scripts = ESQUEMAS[etiqueta]
        armar(esquema, scripts)


def limpiar() -> None:
    for esquema, _ in ESQUEMAS.values():
        mysql(["-e", f"DROP SCHEMA IF EXISTS `{esquema}`;"])
    print("  esquemas de prueba borrados")


def texto_plano(fragmento: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragmento))


def cierre_del_div(txt: str, desde: int) -> int:
    i = txt.index(">", desde) + 1
    prof = 1
    for m in re.finditer(r"<(/?)div\b[^>]*>", txt[i:]):
        prof += -1 if m.group(1) else 1
        if prof == 0:
            return i + m.start()
    raise ValueError("un <div> quedó sin cerrar")


def ejemplos(apunte: Path) -> list[dict]:
    txt = apunte.read_text(encoding="utf-8")
    salida = []
    for m in re.finditer(r'<div class="ejemplo"([^>]*)>', txt):
        atributos = m.group(1)
        fin = cierre_del_div(txt, m.start())
        bloque = txt[m.start():fin]
        codigo = re.search(r"<code data-sql>(.*?)</code>", bloque, re.S)
        hueco = re.search(r"<div data-resultado>", bloque)
        if not codigo or not hueco or "data-sin-tabla" in atributos:
            continue
        tabla = re.search(r'<table class="result-table">(.*?)</table>', bloque, re.S)
        titulo = re.search(r"<h4>(.*?)</h4>", bloque, re.S)
        dec = (re.search(r'data-decimales="([^"]*)"', atributos) or [None, ""])[1]
        des = (re.search(r'data-destacar="([^"]*)"', atributos) or [None, ""])[1]
        salida.append({
            "titulo": re.sub(r"\s+", " ", texto_plano(titulo.group(1))).strip() if titulo else "?",
            "base": (re.search(r'data-base="(\w+)"', atributos) or [None, "base"])[1],
            "sql": texto_plano(codigo.group(1)).strip(),
            "de_mysql": 'data-motor="mysql"' in atributos,
            "decimales": {c.strip() for c in dec.split(",") if c.strip()},
            "destacar": {int(n) for n in des.split(",") if n.strip().isdigit()},
            "ini_hueco": m.start() + hueco.start(),
            "columnas": [texto_plano(c).strip()
                         for c in re.findall(r"<th>(.*?)</th>", tabla.group(1), re.S)] if tabla else [],
            "filas": [[texto_plano(c).strip() for c in re.findall(r"<td>(.*?)</td>", f, re.S)]
                      for f in re.findall(r"<tr[^>]*>(.*?)</tr>", tabla.group(1), re.S)
                      if "<td>" in f] if tabla else [],
        })
    return salida


def escribir_los_de_mysql(apunte: Path, casos: list[dict]) -> int:
    """Rellena las tablas de los ejemplos marcados con data-motor="mysql".

    generar_apunte.py los deja en blanco porque SQLite no los reproduce; acá
    se los llena con la salida del motor, con el mismo formato que el resto.
    """
    sys.path.insert(0, str(Path(__file__).parent))
    from generar_apunte import formato_tabla

    pendientes = [c for c in casos if c["de_mysql"]]
    if not pendientes:
        return 0

    txt = apunte.read_text(encoding="utf-8")

    # Dos pasadas. Primero se ejecuta TODO en el orden del apunte —el mismo que
    # sigue la verificación—, porque un ejemplo hereda el estado que dejó el
    # anterior: si se corriera al revés, el EXPLAIN «sin índice» vería el índice
    # que crea el ejemplo siguiente. Recién después se reemplazan los huecos, y
    # eso sí de atrás para adelante, para que no se corran las posiciones.
    resueltos = []
    for caso in casos:
        rearmar_si_escribe(caso["base"], caso["sql"])
        salida = correr(ESQUEMAS[caso["base"]][0], caso["sql"])
        if not caso["de_mysql"]:
            continue
        if isinstance(salida, str):
            print(f"  {salida}\n    en: {caso['titulo'][:60]}")
            continue
        columnas, filas = salida
        resueltos.append((caso, formato_tabla(columnas, filas,
                                              caso["decimales"], caso["destacar"])))

    escritos = 0
    for caso, contenido in sorted(resueltos, key=lambda x: x[0]["ini_hueco"], reverse=True):
        ini = caso["ini_hueco"]
        fin = cierre_del_div(txt, ini) + len("</div>")
        txt = txt[:ini] + f"<div data-resultado>{contenido}</div>" + txt[fin:]
        escritos += 1
    apunte.write_text(txt, encoding="utf-8")
    return escritos


def correr(esquema: str, sql: str):
    # el ejemplo puede traer un UPDATE o un DELETE antes de su consulta: va
    # dentro de una transacción que se deshace, para no dejar tocada la base.
    # Solo la consulta final imprime algo, así que la salida sigue siendo una.
    envuelto = f"START TRANSACTION;\n{sql}\nROLLBACK;"
    r = mysql(["--batch", "--raw", "-D", esquema], entrada=envuelto)
    if r.returncode != 0:
        return "ERROR " + r.stderr.strip().splitlines()[0][:200]
    lineas = r.stdout.rstrip("\n").split("\n")
    if lineas == [""]:
        return [], []
    return lineas[0].split("\t"), [l.split("\t") for l in lineas[1:]]


def main() -> None:
    global login
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    for a in sys.argv[1:]:
        if a.startswith("--login-path="):
            login = a.split("=", 1)[1]
    if not argumentos:
        print(__doc__)
        sys.exit(1)

    apunte = Path(argumentos[0])
    if not apunte.is_absolute():
        apunte = RAIZ / argumentos[0]

    print("1. ESQUEMAS DE PRUEBA")
    preparar()

    casos = ejemplos(apunte)

    if "--escribir" in sys.argv:
        print("\n2. TABLAS QUE SOLO PUEDE ARMAR MYSQL")
        escritos = escribir_los_de_mysql(apunte, casos)
        print(f"  {escritos} escritas")
        casos = ejemplos(apunte)
        print(f"\n3. CONSULTAS DE {apunte.name} ({len(casos)})")
    else:
        print(f"\n2. CONSULTAS DE {apunte.name} ({len(casos)})")
    iguales = distintos = 0
    for i, caso in enumerate(casos, 1):
        rearmar_si_escribe(caso["base"], caso["sql"])
        salida = correr(ESQUEMAS[caso["base"]][0], caso["sql"])
        if isinstance(salida, str):
            print(f"  {i:2}. {caso['titulo'][:56]:56} {salida}")
            distintos += 1
            continue
        columnas, filas = salida

        problemas = []
        # con cero filas, mysql --batch no imprime el encabezado
        if columnas and columnas != caso["columnas"]:
            problemas.append(f"columnas: página {caso['columnas']} vs motor {columnas}")
        if len(filas) != len(caso["filas"]):
            problemas.append(f"filas: página {len(caso['filas'])} vs motor {len(filas)}")
        else:
            for n, (pagina, motor) in enumerate(zip(caso["filas"], filas)):
                if pagina != motor:
                    problemas.append(f"fila {n + 1}: página {pagina} vs motor {motor}")

        if problemas:
            distintos += 1
            print(f"  {i:2}. {caso['titulo'][:56]:56} DIFIERE")
            for p in problemas[:4]:
                print(f"        {p}")
        else:
            iguales += 1
            print(f"  {i:2}. {caso['titulo'][:56]:56} ok ({len(filas)})")

    print(f"\n3. RESULTADO\n  {iguales} coinciden, {distintos} difieren")

    if "--dejar" not in sys.argv:
        print("\n4. LIMPIEZA")
        limpiar()

    sys.exit(1 if distintos else 0)


if __name__ == "__main__":
    main()
