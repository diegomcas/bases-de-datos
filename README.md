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
| `estudio.css` | lo que necesita un apunte largo: resaltador, índice lateral, sintaxis, ejemplos y una impresión para marcar en papel |
| `modelo.css` | los diagramas del esquema y la referencia de tablas, con tokens que se reskinean para pantalla y para papel |
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

### Los comandos

```bash
python herramientas/generar_indice.py    # arma index.html
python herramientas/generar_ciclos.py    # arma las páginas de ciclo
python herramientas/generar_apunte.py <página>   # resuelve el SQL de un apunte
python herramientas/generar_modelo.py    # arma el modelo y la referencia de los apuntes
python herramientas/verificar.py         # revisa todo antes de publicar

# control contra el motor de verdad, cuando cambian los ejemplos de un apunte
python herramientas/verificar_apunte_mysql.py <página>
```

`index.html` y `ciclos/*.html` **se generan**: editarlos a mano se pierde en la próxima
corrida. Lo que se toca son los `.toml` y la plantilla.

### El apunte de estudio

El apunte de SQL son **dos tomos** que reúnen en un texto continuo lo que estaba repartido
entre las presentaciones y las cajas de teoría de los talleres. Son para leer de corrido,
marcar con el resaltador y llevar impresos; los ejercicios siguen en los talleres,
enlazados al pie de cada tema.

| Tomo | Secciones | Qué cubre |
|---|---|---|
| `unidades/04-sql/apunte-sql.html` | §1 a §25 | Consultar, resumir, cruzar, anidar y modificar |
| `unidades/04-sql/apunte-sql-2.html` | §26 a §45 | Definir la base, fechas, vistas, procedimientos, disparadores, permisos, transacciones e índices |

**La numeración es continua entre los dos**: «§12» identifica una sola sección en todo el
material, y las referencias cruzadas funcionan sin aclarar de cuál tomo se habla.

Tres piezas lo sostienen, y sirven para cualquier apunte que venga después:

- **`assets/css/estudio.css`** — el resaltado, el índice lateral y la hoja impresa.
- **`assets/js/resaltador.js`** — marcar y subrayar con el mouse. Lo marcado se guarda en
  el navegador del alumno (`localStorage`), no viaja a ningún lado y vuelve al recargar.

  Cada marca se guarda con el índice de su párrafo, los dos offsets y **una copia del
  texto marcado**. Al abrir la página se busca primero en ese párrafo, después en los de
  alrededor y al final en todo el apunte, así que **corregir el texto o agregar secciones
  no borra lo que los alumnos marcaron**: la marca se reubica sola y se guarda el índice
  nuevo. Si el texto marcado ya no existe, la marca no se pinta pero **tampoco se borra**
  —el alumno recibe un aviso— y vuelve si ese párrafo regresa.

  El guardado es por navegador, así que para llevárselo a otra máquina o al celular el
  menú `⋯` de la barra abre dos puertas, con el mismo contenido: **bajar un archivo
  `.json`** o **copiar un código** (el mismo JSON comprimido con `CompressionStream` y
  pasado a base64; unas 60 marcas entran en 3 KB). Al traerlos, lo que viene **se suma**
  a lo que ya había y no se repite: una marca ya está si coincide el color y el texto
  marcado, o el color y la posición exacta. El archivo lleva las marcas de todas las
  páginas de estudio de ese navegador, no solo de la abierta, y sirve también para
  repartir un juego de marcas hecho por el docente.

  ```json
  { "formato": "marcas-bdd/1", "generado": "2026-09-19",
    "paginas": { "apunte-sql.html": [ {"b": 1, "d": 0, "h": 40, "t": "…", "c": "marca-amarilla"} ] } }
  ```

  Nada de esto sale del navegador del alumno por sí solo: no hay servidor, no lo ve el
  docente y no se sincroniza entre dispositivos salvo que el alumno mueva el archivo o
  el código.
- **`herramientas/generar_apunte.py`** — resuelve los bloques de SQL de la página.

**Ninguna salida de consulta se escribe a mano.** El ejemplo declara su consulta y con
qué juego de datos corre, y el generador la ejecuta y escribe la tabla:

```html
<div class="ejemplo" data-base="base" data-decimales="total" data-destacar="2">
  ...<pre><code data-sql>SELECT ...</code></pre>
  <div data-resultado></div>
</div>
```

Un ejemplo puede traer un `UPDATE` o un `DELETE` antes de su consulta: todo corre dentro
de una transacción que se deshace, así que los ejemplos siguientes encuentran la base como
estaba. Para que las tablas salgan como las ve el alumno, SQLite recibe el `LIKE` y el
orden de MySQL (`utf8mb4_0900_ai_ci`: sin distinguir mayúsculas ni tildes).

Lo que SQLite no puede reproducir —el contador de `AUTO_INCREMENT`, que en MySQL no vuelve
atrás después de un `DELETE`— se marca con `data-motor="mysql"`, y esa tabla la escribe
`verificar_apunte_mysql.py --escribir`.

```bash
python herramientas/generar_apunte.py unidades/04-sql/apunte-sql.html
```

Es idempotente: lee el SQL de la propia página publicada, así que se puede correr las
veces que haga falta y la página es su propio original. La base se arma en SQLite desde
`assets/consola/elchip.js` —el mismo modelo que usa la consola—, en sus dos juegos de
datos: `base` y `ampliado`. Si cambia el modelo o cambian los datos, se vuelve a correr y
las salidas se acomodan solas.

SQLite alcanza para el SQL de consulta y no pide servidor, pero el motor que usan los
alumnos es MySQL. El control contra el motor de verdad es un comando aparte:

```bash
python herramientas/verificar_apunte_mysql.py unidades/04-sql/apunte-sql.html
```

Corre cada consulta en MySQL y la compara con la tabla publicada, en dos esquemas
propios (`el_chip_ap_base` y `el_chip_ap_amp`) que borra al terminar: la `el_chip` que ya
esté cargada no se toca. Necesita un login-path, que se crea una sola vez:

```
mysql_config_editor set --login-path=prueba --user=root --password
```

### El modelo de la base

`casos/el-chip/modelo.html` es **la hoja de referencia del esquema**: cinco diagramas por
subsistema, la referencia completa de las 19 tablas con sus tipos y claves, y una lectura
de cómo cada flecha se convierte en un `JOIN`. Está pensada para imprimirse **una vez** y
quedar al lado de cualquier apunte o taller.

La escribe `herramientas/generar_modelo.py` leyendo `ElChip.sql`: los nombres, los tipos,
las claves primarias y las foráneas salen del esquema, nunca de lo que alguien recuerde.
Lo único escrito a mano es la composición —qué tabla entra en qué diagrama—, porque un
diagrama es una decisión editorial y no un volcado.

El mismo script escribe la referencia corta que los apuntes muestran en pantalla, en el
hueco `<div data-fichas>`: una sola fuente, tres destinos. En papel esa referencia no se
imprime —queda la línea que remite a la hoja del modelo—, así el alumno no imprime dos
veces lo mismo.

Los diagramas son SVG sin un solo color adentro: todo sale de los tokens de `modelo.css`,
que cambian en `@media print`. El mismo dibujo se ve oscuro en pantalla y en negro sobre
blanco en papel, sin generarlo dos veces. Los criterios de dibujo —presupuesto de tablas
por diagrama, conectores ortogonales de columna a columna, un acento por diagrama— vienen
de la guía [diagram-design](https://github.com/cathrynlavery/diagram-design), con la
paleta y las tipografías del sitio.

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
