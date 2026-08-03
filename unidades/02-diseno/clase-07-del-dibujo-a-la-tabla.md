# Clase 7: Del Dibujo a la Tabla (Mapeo Relacional)

## 🎯 Objetivo de la Clase
Aprender a transformar un modelo conceptual (Diagrama Entidad-Relación) en un modelo lógico (Esquema Relacional o de Tablas), aplicando las reglas de normalización implícita y propagación de claves.

---

## 1. Introducción: ¿Por qué transformar?
El **DER** es excelente para comunicarnos con el cliente y entender el negocio (visión conceptual). Sin embargo, las computadoras y los **SGBD** (como MySQL) no entienden de "diamantes" o "elipses". Ellos entienden de **Tablas, Filas y Columnas**.

El **Modelo Relacional** es el estándar de la industria que permite esta implementación física.

---

## 2. Reglas de Oro para la Transformación

### Regla 1: Entidades Regulares (Fuertes)
Toda entidad del DER se convierte en una **Tabla**.
*   El nombre de la entidad se convierte en el nombre de la tabla (preferentemente en plural).
*   Los atributos se convierten en **Columnas**.
*   El atributo subrayado se convierte en la **Clave Primaria (PK)**.

### Regla 2: Relaciones 1:N (Uno a Muchos) -> Propagación de Clave
Es la relación más común. **No se crea una tabla nueva.**
*   Se toma la PK del lado "1" y se agrega como una nueva columna en la tabla del lado "N".
*   Esta nueva columna se llama **Clave Foránea (FK)**.
*   *Mnemotecnia:* "La clave del fuerte viaja hacia el débil" o "El hijo (N) lleva el apellido del padre (1)".

### Regla 3: Relaciones N:M (Muchos a Muchos) -> Tabla Intermedia
Las relaciones muchos a muchos no se pueden representar directamente con una columna extra.
*   Se crea una **Tabla Nueva** (llamada tabla asociativa o puente).
*   El nombre suele ser la combinación de ambas entidades (ej: `alumnos_materias`).
*   Esta tabla tendrá, al menos, dos columnas: las PKs de ambas entidades relacionadas.
*   Ambas columnas juntas forman una **PK Compuesta**, y cada una por separado es una **FK**.
*   Si la relación tenía atributos propios (ej: "Nota" o "Cantidad"), estos van en esta tabla.

### Regla 4: Entidades Débiles
Las entidades débiles dependen de una entidad fuerte para existir (ej: un `item_factura` depende de una `factura`).
*   Se crea una tabla para la entidad débil.
*   Su PK suele ser una **PK Compuesta**: la PK de la entidad fuerte de la cual depende + un discriminante propio (ej: un nro de renglón).
*   La PK de la entidad fuerte viaja como FK y a la vez forma parte de la PK de la tabla débil.

### Regla 5: Atributos Especiales
*   **Compuestos:** Se "aplanan". (Ej: *Dirección* con *Calle* y *Número* se convierte en dos columnas separadas en la misma tabla).
*   **Multivaluados:** Se crea una tabla separada para ellos (Ej: *Teléfonos* de un cliente).
*   **Derivados:** Normalmente **no se mapean** (se calculan por consulta SQL).

---

## 3. Caso Práctico: "El Chip" 🔧

Apliquemos las reglas al caso de nuestro servicio técnico.

### Paso 1: Mapeo de Entidades Base
| Entidad DER | Tabla Relacional | PK |
| :--- | :--- | :--- |
| CLIENTE | `clientes` | `id_cliente` |
| EQUIPO | `equipos` | `id_equipo` |
| EMPLEADO | `empleados` | `id_empleado` |
| ORDEN_SERVICIO | `ordenes_servicio` | `nro_orden` |
| REPUESTO | `repuestos` | `id_repuesto` |
| PROBLEMA | `problemas` | `id_problema` |

### Paso 2: Aplicando Relaciones 1:N
1.  **CLIENTE (1) --- <posee> --- (N) EQUIPO**
    *   La PK de `clientes` (`id_cliente`) viaja a `equipos`.
    *   `equipos` queda con: `id_equipo (PK), tipo, marca, modelo, nro_serie, id_cliente (FK)`.
2.  **EQUIPO (1) --- <genera> --- (N) ORDEN**
    *   La PK de `equipos` (`id_equipo`) viaja a `ordenes_servicio`.
3.  **EMPLEADO (1) --- <registra> --- (N) ORDEN**
    *   La PK de `empleados` (`id_empleado`) viaja a `ordenes_servicio`.

### Paso 3: Aplicando Relaciones N:M
1.  **ORDEN (N) --- <requiere> --- (M) REPUESTO**
    *   Nueva tabla: `ordenes_repuestos`.
    *   Columnas: `nro_orden (PK, FK), id_repuesto (PK, FK), cantidad`.
2.  **ORDEN (N) --- <presenta> --- (M) PROBLEMA**
    *   Nueva tabla: `ordenes_problemas`.
    *   Columnas: `nro_orden (PK, FK), id_problema (PK, FK)`.

---

## 4. El Esquema Final (Diccionario de Datos)

*   **clientes** (**id_cliente**, nombre, apellido, telefono, email)
*   **equipos** (**id_equipo**, tipo, marca, modelo, nro_serie, *id_cliente*)
*   **empleados** (**id_empleado**, usuario, password, rol)
*   **ordenes_servicio** (**nro_orden**, fecha_ingreso, fecha_entrega, estado, mano_obra, metodo_pago, descuento, total, *id_equipo*, *id_empleado*)
*   **repuestos** (**id_repuesto**, nombre, stock, precio_unitario)
*   **problemas** (**id_problema**, descripcion)
*   **ordenes_repuestos** (**nro_orden**, **id_repuesto**, cantidad)
*   **ordenes_problemas** (**nro_orden**, **id_problema**)

---

## 🛠️ Actividad de Taller: "La Gran Transformación"
1.  Tomar el DER diseñado en la Clase 6 (Sistema de Biblioteca o Videoclub).
2.  Dibujar en papel o herramienta digital el esquema de tablas resultante.
3.  Identificar claramente con una flecha cada **Clave Foránea (FK)** y a qué **Clave Primaria (PK)** apunta.
4.  **Bonus:** Instalar [MySQL Workbench](https://dev.mysql.com/downloads/workbench/) para la próxima clase.

---
*Material preparado para la Cátedra de Bases de Datos - Ciclo 2026*
