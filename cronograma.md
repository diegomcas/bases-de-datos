# 🗓️ Cronograma Detallado: Bases de Datos I (Ciclo 2026)

Este documento detalla la planificación pedagógica semana a semana, especificando el carácter de la clase, los objetivos, los ejes temáticos y la actividad de taller propuesta.

---

## 🟢 1° TRIMESTRE: "El Arte de Modelar la Realidad"

### Clase 1: El Valor de los Datos (02/03 - 06/03)
*   **Carácter:** Teórico-Práctico (T-P).
*   **Objetivo:** Diferenciar técnicamente entre dato, información y conocimiento.
*   **Ejes Temáticos:**
    *   Definiciones base: ¿Qué es un dato? ¿Cuándo se convierte en información?
    *   El ciclo de procesamiento: Entrada -> Proceso -> Salida.
    *   Contextualización: Los datos en una institución escolar (Ej: Una nota vs. el promedio anual).
*   **Actividad Taller:** "Mapeo de Realidad". Los alumnos identifican en un ticket de supermercado o una libreta de calificaciones qué es dato crudo y qué información procesada.

### Clase 2: Del Archivo a la Base de Datos (09/03 - 13/03)
*   **Carácter:** Teórico (T).
*   **Objetivo:** Comprender las limitaciones de los sistemas de archivos tradicionales y la necesidad de un DBMS.
*   **Ejes Temáticos:**
    *   Problemas de los archivos planos: Redundancia, inconsistencia, dificultad de acceso y aislamiento.
    *   Definición de **DBMS (SGBD)**: El software que hace de "aduana" entre el usuario y los datos.
    *   Ventajas competitivas: Integridad, seguridad y concurrencia.
*   **Actividad Taller:** Análisis de caso. Comparar una planilla Excel compartida por 5 personas vs. una base de datos centralizada.

### Clase 3: La Arquitectura de los Datos (16/03 - 20/03)
*   **Carácter:** Teórico-Práctico (T-P).
*   **Objetivo:** Entender los niveles de abstracción para garantizar la independencia de datos.
*   **Ejes Temáticos:**
    *   **Modelo ANSI/SPARC:** Nivel Interno (bits/discos), Conceptual (lógica de negocio) y Externo (vistas de usuario).
    *   Independencia Física vs. Independencia Lógica.
*   **Actividad Taller:** "Taller de Capas". Dibujar cómo un cambio en el formato de un número de teléfono afecta (o no) a la aplicación visual y al almacenamiento en disco.

### Clase 4: Roles, Ética y Seguridad (23/03 - 27/03)
*   **Carácter:** Debate / Práctico (P).
*   **Objetivo:** Identificar a los actores del ecosistema de datos y la responsabilidad legal/ética.
*   **Ejes Temáticos:**
    *   Usuarios de BD: El DBA (Administrador), el Desarrollador y el Usuario Final.
    *   Seguridad Básica: Confidencialidad, Integridad y Disponibilidad (Tríada CIA).
    *   Ética: Manejo de datos sensibles y privacidad (Ley de Protección de Datos Personales).
*   **Actividad Taller:** Debate guiado. "El dilema del DBA": ¿Qué hacer si se detecta un acceso no autorizado de un directivo a sueldos de colegas?

### Clase 5: Ingeniería de Requerimientos (30/03 - 03/04)
*   **Carácter:** Taller de Análisis (T-P).
*   **Objetivo:** Aprender a extraer la lógica de negocio de una entrevista o texto.
*   **Ejes Temáticos:**
    *   Requerimientos Funcionales vs No Funcionales.
    *   Identificación de Reglas de Negocio.
    *   La ambigüedad del lenguaje natural y cómo resolverla.
*   **Actividad Taller:** "Caza de Reglas". Se entrega un texto desordenado de un cliente y los alumnos deben listar las 10 reglas de datos más importantes.

### Clase 6: Modelado Conceptual Integral (DER) (06/04 - 10/04)
    https://app.diagrams.net/
*   **Carácter:** Teórico-Práctico (T-P).
*   **Objetivo:** Dominar la abstracción gráfica de la realidad mediante el modelo Entidad-Relación completo.
*   **Ejes Temáticos:**
    *   **Componentes del DER:** Entidades (Fuertes/Débiles), Atributos (Simples, Compuestos, Multivaluados) y Relaciones.
    *   **Cardinalidad y Participación:** 1:1, 1:N, N:M y restricciones de participación (Total/Parcial).
    *   **El Poder de las Claves:** Superclave, Clave Candidata y Clave Primaria (PK). Claves Naturales vs. Subrogadas.
*   **Actividad Taller:** "Modelado Express". Los alumnos deben diseñar el DER completo de un sistema de biblioteca o videoclub en una sola sesión, identificando entidades, relaciones, cardinalidades y claves.

### Clase 7: Del Dibujo a la Tabla (13/04 - 17/04)
    https://dev.mysql.com/downloads/installer/
    https://dev.mysql.com/downloads/workbench/
*   **Carácter:** Técnico (T-P).
*   **Objetivo:** Ejecutar el pasaje del modelo conceptual (DER) al modelo lógico (Relacional).
*   **Ejes Temáticos:**
    *   Reglas de Transformación: Conversión de relaciones N:M y 1:N.
    *   Propagación de Claves: La aparición de la Clave Foránea (FK).
    *   Tratamiento de atributos complejos en el modelo de tablas.
*   **Actividad Taller:** "La Gran Transformación". Los alumnos pasan su DER de papel a un esquema de tablas (filas y columnas).

### Clase 8: Diseño Físico e Índices (20/04 - 24/04)
*   **Carácter:** Laboratorio (P).
*   **Objetivo:** Entender cómo se guardan los datos en el hardware.
*   **Ejes Temáticos:**
    *   Tipos de datos según el motor (VARCHAR, INT, DECIMAL).
    *   ¿Qué es un Índice? Analogía con el índice de un libro.
    *   Costo de almacenamiento vs Velocidad de consulta.
*   **Actividad Taller:** "Diccionario de Datos". Crear un documento técnico que especifique el tipo exacto y longitud de cada campo de la BD escolar.

### Clase 9: Taller de Refuerzo - Modelado y Pasaje (27/04 - 01/05)
*   **Carácter:** Taller Intensivo (P).
*   **Objetivo:** Consolidar la lógica de diseño y la transformación a tablas con casos complejos.
*   **Ejes Temáticos:**
    *   Resolución de dudas sobre cardinalidades complejas.
    *   Práctica de normalización intuitiva durante el pasaje a tablas.
*   **Actividad Taller:** "Desafío de Diseño". Modelar un sistema de turnos médicos con múltiples especialidades y obras sociales.

### Clase 10: Clínica de Diseño y Pre-Parcial (04/05 - 08/05)
*   **Carácter:** Consulta / Simulacro (P).
*   **Objetivo:** Pulir detalles finales y prepararse para la evaluación.
*   **Ejes Temáticos:**
    *   Repaso general de la Unidad I y II.
    *   Simulacro de examen con corrección en tiempo real.
*   **Actividad Taller:** "Auditoría de Pares". Los alumnos intercambian sus diseños y deben encontrar errores de lógica o violaciones de reglas de negocio.

### Clase 11: Repaso e Integración (11/05 - 15/05)
*   **Carácter:** Evaluación.
*   **Objetivo:** Validar los conocimientos de diseño y modelado de la primera etapa.
*   **Actividad Taller:** **1er EXAMEN PARCIAL (Diseño y Modelado).**

---

## 🟡2° TRIMESTRE: "La Teoría de la Calidad"

### Clase 12: Las Reglas de Edgar Codd (18/05 - 22/05)
*   **Carácter:** Teórico (T).
*   **Objetivo:** Comprender el rigor científico detrás del modelo relacional.
*   **Ejes Temáticos:**
    *   Historia: El paper de 1970 de IBM.
    *   Integridad de Entidad (No PK nula) e Integridad Referencial (No FK huérfana).
*   **Actividad Taller:** "Auditoría de Datos". Se entrega una base "rota" y los alumnos deben señalar qué reglas de integridad se están violando.

### Clase 13: Álgebra Relacional I (25/05 - 29/05)
*   **Carácter:** Teórico-Matemático (T-P).
*   **Objetivo:** Pensar en conjuntos antes de escribir SQL.
*   **Ejes Temáticos:**
    *   Operaciones Unarias: Selección ($\sigma$) y Proyección ($\pi$).
    *   Operaciones Binarias: Unión, Diferencia y Producto Cartesiano.
*   **Actividad Taller:** "Consultas en Papel". Resolver pedidos usando símbolos matemáticos.

### Clase 14: Álgebra Relacional II: Joins (01/06 - 05/06)
*   **Carácter:** Práctico (P).
*   **Objetivo:** Dominar la operación de reunión de tablas.
*   **Ejes Temáticos:**
    *   Natural Join, Theta Join y Outer Joins.
    *   Intersección y División relacional.
*   **Actividad Taller:** "Cruzando Datos". Escribir las expresiones algebraicas para unir `ALUMNOS` con `NOTAS`.

### Clase 15: Normalización I: El Caos de la Redundancia (08/06 - 12/06)
*   **Carácter:** Clínica de Datos (T-P).
*   **Objetivo:** Identificar por qué los datos repetidos destruyen sistemas.
*   **Ejes Temáticos:**
    *   Anomalías de Inserción, Modificación y Borrado.
    *   Concepto de Atomicidad y **Primera Forma Normal (1FN).**
*   **Actividad Taller:** "Desarmando el Excel". Llevar una planilla de asistencia gigante a 1FN eliminando grupos repetidos.

---

### Clase 16: Dependencias Funcionales (15/06 - 19/06)
*   **Carácter:** Teórico-Práctico (T-P).
*   **Objetivo:** Identificar los vínculos lógicos entre atributos que determinan la estructura de una tabla.
*   **Ejes Temáticos:**
    *   Definición de DF: Determinante y Dependiente.
    *   Tipos de dependencias: Parcial, Transitiva y Completa.
    *   Axiomas de Armstrong y Cálculo de cierres de atributos.
*   **Actividad Taller:** "Cierre de Atributos". Ejercicios en pizarra para identificar claves candidatas a partir de un conjunto de dependencias.

### Clase 17: Normalización II: 2FN y 3FN (22/06 - 26/06)
*   **Carácter:** Teórico-Práctico (T-P).
*   **Objetivo:** Refinar el diseño eliminando dependencias parciales y transitivas para evitar anomalías.
*   **Ejes Temáticos:**
    *   **Segunda Forma Normal (2FN):** Eliminación de dependencias parciales.
    *   **Tercera Forma Normal (3FN):** Eliminación de dependencias transitivas.
    *   Descomposición sin pérdida de información (Lossless Join).
*   **Actividad Taller:** "Resolución de Anomalías". Aplicar 2FN y 3FN a un caso de "Gestión de Pedidos" con redundancia evidente.

### Clase 18: Normalización III: Forma Normal Boyce-Codd (29/06 - 03/07)
*   **Carácter:** Teórico-Práctico (T-P).
*   **Objetivo:** Alcanzar el máximo rigor de integridad en esquemas con múltiples claves candidatas superpuestas.
*   **Ejes Temáticos:**
    *   Limitaciones de la 3FN.
    *   Definición de **FNBC (BCNF)**: Todo determinante debe ser clave candidata.
    *   Análisis de casos complejos de superposición de claves.
*   **Actividad Taller:** "El Desafío de Codd". Resolver casos "bordes" donde la 3FN falla y la FNBC es necesaria para garantizar la consistencia.

---

## ❄️ RECESO INVERNAL (06/07 - 17/07)
*Pausa lectiva para la consolidación de conceptos y descanso.*

---

### Clase 21: Desnormalización y Performance (20/07 - 24/07)
*   **Carácter:** Teórico-Estratégico (T).
*   **Objetivo:** Entender cuándo y por qué sacrificar la pureza del diseño en favor de la velocidad de lectura.
*   **Ejes Temáticos:**
    *   El costo de los Joins en sistemas de gran escala.
    *   Concepto de redundancia controlada.
    *   Casos de uso: Data Warehousing y reportes de alta performance.
*   **Actividad Taller:** Debate guiado: "Pureza vs. Velocidad". Analizar un sistema que requiere miles de lecturas por segundo frente a uno de alta transaccionalidad.

### Clase 22: SQL I: Definición de Datos (DDL) (27/07 - 31/07)
*   **Carácter:** Laboratorio (P).
*   **Objetivo:** Traducir el modelo físico a sentencias ejecutables en un motor real (MySQL).
*   **Ejes Temáticos:**
    *   Tipos de datos en SQL (INT, VARCHAR, DATE, DECIMAL).
    *   Sentencias base: `CREATE`, `ALTER` y `DROP`.
    *   Restricciones de integridad: `NOT NULL`, `UNIQUE`, `DEFAULT`, `CHECK`.
    *   Definición de PK y FK por script.
*   **Actividad Taller:** "Script de Nacimiento". Los alumnos escriben el código SQL completo para crear la base de datos de su proyecto escolar.

### Clase 23: SQL II: Manipulación Básica (DML) (03/08 - 07/08)
*   **Carácter:** Laboratorio (P).
*   **Objetivo:** Aprender las operaciones fundamentales de persistencia y consulta simple.
*   **Ejes Temáticos:**
    *   Operaciones de actualización: `INSERT`, `UPDATE` y `DELETE`.
    *   Consulta básica: `SELECT`, `FROM` y alias.
    *   Filtrado con `WHERE` y operadores lógicos/comparativos.
    *   Ordenamiento con `ORDER BY`.
*   **Actividad Taller:** "Poblando el Sistema". Insertar datos reales en las tablas creadas y realizar las primeras búsquedas de información específica.

### Clase 24: Consolidación y 2do Examen (10/08 - 14/08)
*   **Carácter:** Evaluación.
*   **Objetivo:** Validar el dominio de la Normalización, Álgebra Relacional y SQL básico.
*   **Actividad Taller:** **2do EXAMEN PARCIAL (Teoría Relacional, Normalización y SQL Inicial).**

### Clase 25: SQL III: El Poder de los Joins (17/08 - 21/08)
*   **Carácter:** Laboratorio (P).
*   **Objetivo:** Consultar múltiples tablas simultáneamente de forma eficiente.
*   **Ejes Temáticos:**
    *   Inner Joins vs. Outer Joins (`LEFT`, `RIGHT`, `FULL`).
    *   Joins de múltiples tablas y Self-joins.
    *   Manejo de valores `NULL` en consultas de unión.
*   **Actividad Taller:** "Cruce de Datos Maestro". Resolver un set de 15 consultas complejas que requieren vincular al menos 3 tablas para obtener la respuesta.

### Clase 26: SQL IV: Agregación y Grupos (24/08 - 28/08)
*   **Carácter:** Laboratorio (P).
*   **Objetivo:** Obtener métricas y resúmenes estadísticos directamente del motor de BD.
*   **Ejes Temáticos:**
    *   Funciones de agregado: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.
    *   Agrupamiento de datos: `GROUP BY`.
    *   Filtrado de grupos: `HAVING`.
*   **Actividad Taller:** "Tablero de Control". Generar reportes de gestión: promedios por curso, totales de ventas mensuales y detección de máximos/mínimos.

---

## 🟠 3° TRIMESTRE: "Programación, Optimización y Proyecto Final"

### Clase 27: SQL V: Subconsultas y Lógica Avanzada (31/08 - 04/09)
*   **Carácter:** Técnico (T-P).
*   **Objetivo:** Resolver problemas de negocio complejos mediante la anidación de consultas.
*   **Ejes Temáticos:**
    *   Subconsultas escalares, de lista y de tabla.
    *   Operadores `IN`, `EXISTS`, `ANY`, `ALL`.
    *   Subconsultas correlacionadas vs. Joins: ¿Cuándo usar cada una?
*   **Actividad Taller:** "Inception SQL". Resolver desafíos del tipo "¿Quiénes tienen un promedio superior al promedio general de su curso?".

### Clase 28: Vistas y Seguridad de Acceso (07/09 - 11/09)
*   **Carácter:** Técnico (T-P).
*   **Objetivo:** Abstraer la complejidad para el usuario y proteger datos sensibles.
*   **Ejes Temáticos:**
    *   Creación y gestión de **Vistas (VIEW)**.
    *   Gestión de Usuarios y Roles.
    *   Control de acceso: Sentencias `GRANT` y `REVOKE`.
*   **Actividad Taller:** "Capas de Seguridad". Diseñar vistas específicas para que diferentes roles (Profesor, Alumno, Administrativo) vean solo lo que les corresponde.

### Clase 29: Transacciones y Propiedades ACID (14/09 - 18/09)
*   **Carácter:** Teórico-Práctico (T-P).
*   **Objetivo:** Garantizar la consistencia de los datos en entornos concurrentes y ante fallos.
*   **Ejes Temáticos:**
    *   Concepto de Transacción: Inicio, `COMMIT` y `ROLLBACK`.
    *   Propiedades **ACID** (Atomicidad, Consistencia, Aislamiento, Durabilidad).
    *   Niveles de aislamiento y bloqueos (Locks).
*   **Actividad Taller:** "El Simulacro del Cajero". Ejecutar manualmente una transferencia bancaria simulando una caída del servidor a mitad del proceso para verificar la recuperación.

### Clase 30: Programación en BD: Stored Procedures I (21/09 - 25/09)
*   **Carácter:** Programación (P).
*   **Objetivo:** Automatizar lógica de negocio dentro del motor de base de datos.
*   **Ejes Temáticos:**
    *   Introducción a SQL Procedural (PL/SQL o MySQL Scripts).
    *   Variables, tipos de datos locales y parámetros (`IN`, `OUT`).
    *   Estructuras de decisión: `IF-THEN-ELSE` y `CASE`.
*   **Actividad Taller:** "Procedimientos Base". Crear un SP para registrar una venta que valide el stock disponible antes de realizar el `INSERT`.

### Clase 31: Programación en BD: Stored Procedures II (28/09 - 02/10)
*   **Carácter:** Programación (P).
*   **Objetivo:** Manejar flujos de datos iterativos y control de errores.
*   **Ejes Temáticos:**
    *   Bucles: `WHILE`, `LOOP` y `REPEAT`.
    *   Manejo de Excepciones y Handlers.
    *   Introducción al uso de Cursores.
*   **Actividad Taller:** "Procesamiento en Lote". Desarrollar un procedimiento que recorra todas las facturas impagas y genere automáticamente una nota de débito por mora.

### Clase 32: Triggers: El Motor Reactivo (05/10 - 09/10)
*   **Carácter:** Programación (P).
*   **Objetivo:** Implementar reglas de integridad automática que reaccionan a eventos de datos.
*   **Ejes Temáticos:**
    *   Eventos `BEFORE` / `AFTER` para `INSERT`, `UPDATE` y `DELETE`.
    *   Uso de pseudo-filas `NEW` y `OLD`.
    *   Casos de uso: Auditoría, sincronización de datos y reglas de negocio complejas.
*   **Actividad Taller:** "Log de Auditoría". Programar un trigger que guarde en una tabla secundaria cada cambio realizado en la tabla de sueldos (quién, cuándo y valor anterior).

### Clase 33: Optimización de Consultas (12/10 - 16/10)
*   **Carácter:** Laboratorio (P).
*   **Objetivo:** Diagnosticar y corregir cuellos de botella en el rendimiento de la BD.
*   **Ejes Temáticos:**
    *   Análisis de planes de ejecución (`EXPLAIN`).
    *   Optimización de Índices (B-Tree vs. Hash).
    *   Buenas prácticas en la escritura de SQL (Sargability).
*   **Actividad Taller:** "Carrera de Consultas". Comparar el tiempo de ejecución de una consulta ineficiente sobre un millón de registros antes y después de aplicar índices estratégicos.

### Clase 34: Introducción al Mundo NoSQL (19/10 - 23/10)
*   **Carácter:** Teórico-Exploratorio (T).
*   **Objetivo:** Conocer alternativas al modelo relacional para datos no estructurados.
*   **Ejes Temáticos:**
    *   El Teorema CAP y la consistencia eventual.
    *   Tipos de NoSQL: Documentales (MongoDB), Clave-Valor (Redis), Grafos (Neo4j).
    *   Estructuras JSON y BSON.
*   **Actividad Taller:** "Modelado Documental". Traducir un DER relacional pequeño a una estructura de documentos JSON jerárquicos.

### Clase 35: Business Intelligence y ETL (26/10 - 30/10)
*   **Carácter:** Teórico (T).
*   **Objetivo:** Entender el ciclo de vida del dato para la toma de decisiones.
*   **Ejes Temáticos:**
    *   OLTP vs. OLAP.
    *   El proceso **ETL** (Extraer, Transformar y Cargar).
    *   Modelado Dimensional: El Modelo Estrella (Star Schema).
*   **Actividad Taller:** "Diseño de Cubo". Diseñar las dimensiones y la tabla de hechos para analizar las ventas históricas de una cadena de retail.

### Clase 36: TPI: Lanzamiento e Integración (02/11 - 06/11)
*   **Carácter:** Taller de Proyecto (P).
*   **Objetivo:** Iniciar la construcción final del Trabajo Práctico Integrador.
*   **Ejes Temáticos:**
    *   Arquitectura del proyecto.
    *   Carga de datos de prueba volumétricos (Mock Data).
*   **Actividad Taller:** Setup inicial: Creación del repositorio, ejecución del script DDL final y carga masiva de datos para pruebas de stress.

### Clase 37: TPI: Implementación Lógica y Programación (09/11 - 13/11)
*   **Carácter:** Taller de Proyecto (P).
*   **Objetivo:** Integrar la lógica procedural y reactiva en el proyecto.
*   **Ejes Temáticos:**
    *   Desarrollo de SP y Triggers críticos.
    *   Validación de Reglas de Negocio en el motor.
*   **Actividad Taller:** Codificación intensiva de la capa de programación de la base de datos, asegurando que toda la lógica resida en el motor.

### Clase 38: TPI: Testing, Seguridad y Documentación (16/11 - 20/11)
*   **Carácter:** Taller de Proyecto (P).
*   **Objetivo:** Asegurar la calidad técnica y la entregabilidad del producto.
*   **Ejes Temáticos:**
    *   Pruebas de integridad referencial.
    *   Documentación técnica: Diccionario de Datos y Diagrama Final.
*   **Actividad Taller:** "Control de Calidad". Pruebas cruzadas entre grupos para detectar fallos de seguridad o inconsistencias en los datos.

### Clase 39: Defensa Final y Cierre del Ciclo (23/11 - 27/11)
*   **Carácter:** Evaluación Final.
*   **Objetivo:** Demostrar las competencias adquiridas mediante la defensa del proyecto integrador.
*   **Actividad Taller:** **PRESENTACIÓN Y DEFENSA ORAL DEL TPI.** Demostración funcional del sistema y respuesta a consultas técnicas del tribunal docente.
