#!/usr/bin/env python3
"""
Lee un script de estructura de MySQL y devuelve el esquema: tablas, columnas,
tipos, claves primarias y foráneas.

Lo usa generar_modelo.py. Se mantiene aparte para poder comprobarlo solo:

    python herramientas/modelo_esquema.py casos/el-chip/ElChip.sql
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


class Columna:
    def __init__(self, nombre, tipo, nula, defecto, auto):
        self.nombre = nombre
        self.tipo = tipo
        self.nula = nula
        self.defecto = defecto
        self.auto = auto
        self.pk = False
        self.fk = None          # (tabla, columna) a la que apunta

    @property
    def marcas(self) -> list[str]:
        """Los chips de restricción, en el orden en que se leen."""
        m = []
        if self.pk:
            m.append("PK")
        if self.fk:
            m.append("FK")
        if self.auto:
            m.append("AI")
        if not self.nula and not self.pk:
            m.append("NN")
        return m


class Tabla:
    def __init__(self, nombre):
        self.nombre = nombre
        self.columnas: list[Columna] = []

    def columna(self, nombre):
        for c in self.columnas:
            if c.nombre == nombre:
                return c
        return None

    @property
    def pk(self) -> list[str]:
        return [c.nombre for c in self.columnas if c.pk]


def leer(ruta: Path) -> dict[str, Tabla]:
    sql = ruta.read_text(encoding="utf-8", errors="replace")
    sql = re.sub(r"--[^\n]*", "", sql)

    tablas: dict[str, Tabla] = {}
    for m in re.finditer(
        r"CREATE TABLE(?: IF NOT EXISTS)? `?(?:\w+`?\.`?)?(\w+)`?\s*\((.*?)\)\s*ENGINE",
        sql, re.S | re.I,
    ):
        tabla = Tabla(m.group(1))
        cuerpo = m.group(2)

        for linea in cuerpo.split("\n"):
            linea = linea.strip().rstrip(",")
            if not linea:
                continue

            col = re.match(r"`(\w+)`\s+([A-Z]+(?:\([\d,\s]+\))?)(.*)", linea, re.I)
            if col:
                resto = col.group(3)
                defecto = re.search(r"DEFAULT\s+([^\s,]+)", resto, re.I)
                tabla.columnas.append(Columna(
                    col.group(1),
                    col.group(2).upper().replace(" ", ""),
                    "NOT NULL" not in resto.upper(),
                    defecto.group(1) if defecto else None,
                    "AUTO_INCREMENT" in resto.upper(),
                ))
                continue

            pk = re.match(r"PRIMARY KEY\s*\((.*?)\)", linea, re.I)
            if pk:
                for nombre in re.findall(r"`(\w+)`", pk.group(1)):
                    c = tabla.columna(nombre)
                    if c:
                        c.pk = True

        tablas[tabla.nombre] = tabla

    # las claves foráneas se declaran dentro del mismo CREATE TABLE
    for m in re.finditer(
        r"CREATE TABLE(?: IF NOT EXISTS)? `?(?:\w+`?\.`?)?(\w+)`?\s*\((.*?)\)\s*ENGINE",
        sql, re.S | re.I,
    ):
        origen = tablas[m.group(1)]
        for fk in re.finditer(
            r"FOREIGN KEY\s*\(`(\w+)`\)\s*REFERENCES\s+`?(?:\w+`?\.`?)?(\w+)`?\s*\(`(\w+)`\)",
            m.group(2), re.I | re.S,
        ):
            c = origen.columna(fk.group(1))
            if c:
                c.fk = (fk.group(2), fk.group(3))

    return tablas


def main() -> None:
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "casos/el-chip/ElChip.sql"
    if not ruta.is_absolute():
        ruta = RAIZ / ruta
    tablas = leer(ruta)
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"{len(tablas)} tablas en {ruta.name}\n")
    for t in tablas.values():
        print(f"  {t.nombre}  (PK: {', '.join(t.pk) or '—'})")
        for c in t.columnas:
            destino = f"  →  {c.fk[0]}.{c.fk[1]}" if c.fk else ""
            print(f"      {c.nombre:26} {c.tipo:14} {' '.join(c.marcas):12}{destino}")
        print()


if __name__ == "__main__":
    main()
