# Bases de Datos · Ciclo 2026

Material completo de la materia **Bases de Datos** de 4.º año, publicado como sitio
navegable.

**→ [diegomcas.github.io/bases-de-datos](https://diegomcas.github.io/bases-de-datos/)**

Apuntes, presentaciones, casos de estudio y siete talleres de SQL con sus resoluciones,
organizados por trimestre y unidad. Todo el recorrido gira alrededor de un solo caso: el
taller de reparación de celulares de Martín, que aparece en la primera clase como un
relato hablado y termina, al final del año, convertido en una base que responde preguntas.

---

## Cómo empezar

Casi todos los ejercicios corren sobre la base de El Chip. Se arma una vez y sirve para
todo el año:

```sql
SOURCE casos/el-chip/ElChip.sql;                  -- estructura
SOURCE casos/el-chip/poblar_elchip.sql;           -- datos base
SOURCE casos/el-chip/poblar_elchip_compendio.sql; -- ampliación de los compendios
```

Los compendios de agrupación y subconsultas **necesitan el tercer script**. Sin él, la
mitad de los ejercicios devuelve una sola fila o ninguna.

---

## Cómo está organizado

```
index.html            portada: el año por trimestre y unidad  ← GENERADO
cronograma.html       las 39 clases con su objetivo y ejes
glosario.html         los términos de la materia
consola.html          la base de El Chip ejecutable en el navegador

materiales.toml       la biblioteca: qué material existe y en qué estado
ciclos/               un archivo por año + las páginas de cada recorrido
herramientas/         los generadores y el verificador

unidades/
  01-fundamentos/     por qué existe una base de datos
  02-diseno/          del pedido hablado al esquema de tablas
  03-calidad/         Codd y normalización
  04-sql/             los siete talleres, con consignas y resoluciones
  05-horizontes/      más allá del modelo relacional

casos/
  el-chip/            relato, DER, scripts y la aplicación funcionando
  biblioteca/         segundo caso, más chico

proyecto/             la propuesta del integrador
descargas/            los originales en PDF, DOCX y PPTX
assets/               hojas de estilo, tipografías e imágenes
```

Cada taller tiene dos archivos, `-consignas` y `-resoluciones`, enlazados **ejercicio por
ejercicio**: cada reto lleva a su solución y vuelve.

---

## El sistema de diseño

Las páginas no llevan estilos propios: comparten ocho hojas en `assets/css/`.

| Hoja | Para qué |
|---|---|
| `fuentes.css` | Inter, Outfit y Fira Code, servidas desde acá (114 KB, sin pedirle nada a terceros) |
| `base.css` | tokens, tipografía, encabezado, bloques de código, tablas anchas y navegación |
| `taller.css` | consignas, resoluciones, tablas de resultados |
| `apunte.css` | texto corrido de las clases |
| `documento.css` | informes y notas técnicas: cifras, decisiones, avisos, anexos |
| `presentacion.css` | diapositivas convertidas a página |
| `indice.css` | la portada |
| `consola.css` | la terminal de SQL |

Para armar una página nueva alcanza con enlazarlas y declarar el tema:

```html
<link rel="stylesheet" href="assets/css/fuentes.css">
<link rel="stylesheet" href="assets/css/base.css">
<link rel="stylesheet" href="assets/css/taller.css">
<body data-tema="consigna">
```

Los temas disponibles son `consigna`, `resolucion`, `indice`, `apunte` y `presentacion`.
**[`assets/componentes.html`](assets/componentes.html)** muestra todas las piezas con su
código: conviene copiar de ahí.

### Sobre el resaltado del SQL

Los colores están medidos, no elegidos a ojo. Los cuatro roles superan **7,5:1 de
contraste** sobre el fondo de código (WCAG AAA), y el brillo de cada uno está escalonado a
propósito: con protanopia o deuteranopia el tono se pierde y el brillo es la única pista
que queda. Antes de cambiar un color, medilo.

| Rol | Color | Contraste | Señal extra |
|---|---|---|---|
| Palabra clave | `#ff9ec9` | 10,4:1 | negrita |
| Literal | `#ffd166` | 13,7:1 | — |
| Comentario | `#8fa2c4` | 7,7:1 | itálica |
| Número | `#8ceacf` | 13,9:1 | — |

---

## La biblioteca y los ciclos

El material y el año son cosas distintas y viven separadas. Un taller de agrupación no es
«2026»: lo que pertenece a un año es qué material se usó, en qué orden y en qué semanas.

```
materiales.toml     la biblioteca: 31 piezas con su unidad, su caso y su estado
ciclos/2026.toml    el recorrido del año: trimestres, unidades, clases
```

La biblioteca **crece y no se borra**. Cada pieza tiene un estado:

| Estado | Qué significa |
|---|---|
| `vigente` | lo pide el programa del ciclo en curso |
| `ampliacion` | estuvo en el programa y sigue sirviendo |
| `borrador` | todavía no se publica |
| `retirado` | salió por estar mal; no se muestra |

Cuando un programa nuevo deja un material afuera, esa pieza pasa a `ampliacion` y aparece
sola en una franja al cierre de su unidad, marcada como tal. El alumno la encuentra donde
está el tema, y los recorridos de años anteriores siguen apuntando al material vivo: si un
taller se corrige, el ciclo viejo muestra la versión corregida.

La unidad se referencia **por nombre**, nunca por número: los números cambian con cada
programa.

### Los tres comandos

```bash
python herramientas/generar_indice.py    # arma index.html
python herramientas/generar_ciclos.py    # arma las páginas de ciclo
python herramientas/verificar.py         # revisa todo antes de publicar
```

`index.html` y `ciclos/*.html` **se generan**: editarlos a mano se pierde en la próxima
corrida. Lo que se toca son los `.toml` y la plantilla.

El verificador comprueba ocho cosas —enlaces, saltos entre consigna y resolución, nombres
aptos para URL, colisiones de mayúsculas, clases CSS sin definir, correspondencia entre el
manifiesto y los archivos, si el índice quedó viejo, y que nada privado haya quedado
versionado— y devuelve error si algo falla.

---

## Qué no está acá

Este repositorio es público. Quedan deliberadamente afuera, y así debe seguir:

- **Datos de estudiantes**: listados de curso y trabajos entregados.
- **Exámenes y sus claves**.
- **Guiones de clase** del docente.

Están en el `.gitignore`, con el motivo escrito al lado de cada regla. Antes de agregar
algo nuevo, la pregunta es si puede leerlo cualquiera.

---

## Licencia

Este material se distribuye bajo **[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es)**
(Atribución · No comercial · Compartir igual).

Podés **usarlo, copiarlo y adaptarlo** para dar clase, estudiar o preparar tu
propio material. Sólo hace falta que cites la autoría, indiques si hiciste cambios y
distribuyas lo que derives bajo la misma licencia. Lo único que no está permitido es el
uso comercial.

Si sos docente y querés usar los talleres en tu curso, adelante: para eso está publicado.

Los datos estadísticos citados en la propuesta de proyecto pertenecen a sus fuentes
—IFPI, SInCA del Ministerio de Cultura de la Nación, Kimball Group y Universidad de
Granada— y se usan con atribución.

---

## Créditos

Diego Cassini · Ciclo lectivo 2026
