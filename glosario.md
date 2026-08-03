# 📖 Glosario Integral de Cátedra: Bases de Datos e Ingeniería de Software

Este glosario combina los conceptos específicos de la materia con los procesos y herramientas del desarrollo profesional de software.

---

## 🏗️ 1. Fundamentos y Arquitectura de Datos
*   **Sistema de Gestión de Bases de Datos (SGBD);** DBMS (*Database Management System*), el "motor" de la base; el programa de la base; software que permite administrar y controlar el acceso a los datos, asegurando su integridad y seguridad (ej: MySQL, PostgreSQL).
*   **Independencia de Datos;** Transparencia física/lógica; que no se rompa nada si cambio de lugar los archivos; capacidad de modificar el esquema de la base de datos en un nivel sin tener que alterar los niveles superiores (separar cómo se guarda de cómo se usa).
*   **Abstracción de Datos;** Niveles de visión (ANSI/SPARC); las capas de la base; simplificación de la complejidad del almacenamiento real para mostrar solo lo que el usuario o el programador necesita ver.

## 🎨 2. Diseño y Modelado (Conceptual y Lógico)
*   **Entidad;** Tabla (a veces confundido en la práctica), Objeto; la "cosa" o el concepto; representación de un objeto del mundo real (físico o abstracto) sobre el cual se desea guardar información.
*   **Atributo;** Campo, Columna, *Property*; los datos de la tabla; característica o propiedad que describe a una entidad (ej: el "Nombre" de un Alumno).
*   **Relación;** *Relationship*, Asociación; el "vínculo" o la "flechita" del diagrama; conexión lógica entre dos o más entidades que indica cómo interactúan entre sí.
*   **Cardinalidad;** Multiplicidad, Grado de relación; el "uno a muchos" o "muchos a muchos"; define cuántas instancias de una entidad pueden asociarse con cuántas instancias de otra.
*   **Mapeo Relacional;** Pasaje a tablas, Transformación; proceso de convertir el diagrama (DER) en un esquema de tablas y columnas siguiendo reglas lógicas.
*   **Propagación de Clave;** *Key Migration*; cuando la PK de una tabla "viaja" a otra para convertirse en FK; técnica fundamental para representar relaciones 1:N.

## ⛓️ 3. El Modelo Relacional e Integridad
*   **Clave Primaria;** *Primary Key*, PK, "La Primary"; el ID, el código único; campo o conjunto de campos que identifican de forma unívoca a un registro en una tabla, impidiendo duplicados.
*   **Clave Foránea;** *Foreign Key*, FK, Clave ajena; el "vínculo" a otra tabla, el ID de afuera; campo en una tabla que hace referencia a la Clave Primaria de otra, estableciendo la relación entre ambas.
*   **Integridad Referencial;** Consistencia de enlaces; que no haya "huérfanos"; regla que asegura que si existe una clave foránea, esta debe apuntar a una clave primaria válida existente.
*   **Normalización;** *Refactoring* de tablas, "Limpiar" la base; separar las tablas para que no se repitan datos; proceso de organizar los datos para minimizar la redundancia y evitar problemas al insertar, borrar o editar información.

## 💻 4. Implementación y Operaciones (SQL)
*   **Consultas;** *Queries*; pedirle cosas a la base; sentencias escritas en SQL para recuperar información específica de una o más tablas.
*   **Join;** Combinación de tablas, "Cruzar" tablas; juntar los datos; operación de SQL que permite combinar registros de dos o más tablas basándose en un campo común (normalmente PK y FK).
*   **Restricción;** *Constraint*; los límites o reglas; validaciones automáticas; reglas que se aplican a las columnas para limitar los tipos de datos que pueden ingresar (ej: `NOT NULL`, `UNIQUE`).
*   **Transacción;** *Transaction*, Unidad de trabajo; el "todo o nada"; conjunto de operaciones que se ejecutan como una sola unidad: o se guardan todas con éxito o no se guarda ninguna (manteniendo la propiedad ACID).
*   **Procedimiento Almacenado;** *Stored Procedure*, SP; "scripts" en la base; funciones guardadas; programa guardado dentro de la base de datos que puede ser ejecutado para realizar tareas repetitivas o complejas.
*   **Disparador;** *Trigger*; el "sensor" o automatismo; algo que salta solo; código que se ejecuta automáticamente cuando ocurre un evento específico (como un `INSERT` o `DELETE`) en una tabla.

## 🚀 5. Nuevos Paradigmas y Analítica
*   **NoSQL;** No Relacional, *Schemaless*; bases de datos "sin tablas" (generalmente); sistemas de almacenamiento de datos que no utilizan el modelo relacional tradicional, ideales para grandes volúmenes de datos desestructurados.
*   **ETL;** *Extract, Transform, Load*; limpieza y carga de datos; el "pasaje" de datos; proceso de extraer datos de distintas fuentes, transformarlos para que sean útiles y cargarlos en un destino (como un Data Warehouse).

---

## 📋 6. Requerimientos e Ingeniería de Software
*   **Requerimiento Funcional;** *Feature* / *Functional Requirement*; "Lo que tiene que hacer el sistema"; descripción de un servicio o función que el software debe ser capaz de realizar (ej: "el sistema debe permitir el registro de alumnos").
*   **Requerimiento No Funcional;** *Quality Attribute* / *Constraint*; "Cómo tiene que andar" (rápido, seguro, etc.); restricciones o propiedades del sistema como el rendimiento, la seguridad, la disponibilidad o el lenguaje de programación.
*   **Historia de Usuario;** *User Story*; "El pedido del usuario"; breve explicación de una funcionalidad contada desde la perspectiva del usuario final (ej: "Como alumno, quiero ver mis notas...").
*   **Alcance del Proyecto;** *Scope*; "Hasta dónde llegamos"; límite acordado de lo que se va a desarrollar y lo que queda fuera para evitar que el proyecto crezca infinitamente.
*   **Ciclo de Vida del Software;** SDLC (*Software Development Life Cycle*); "El paso a paso del proyecto"; las etapas por las que pasa un programa desde que nace como idea hasta que se retira (Análisis, Diseño, Codificación, Testeo, Mantenimiento).
*   **Metodología Ágil;** *Agile*; "Trabajar por iteraciones / pedacitos"; forma de trabajo que prioriza entregas rápidas y constantes de software funcional en lugar de planificar todo un año de antemano.
*   **Iteración;** *Sprint*; "El tramo de trabajo" (generalmente de 2 semanas); periodo corto de tiempo en el que el equipo se compromete a terminar un conjunto específico de tareas.
*   **Deuda Técnica;** *Technical Debt*; "El código 'atado con alambre' que hay que arreglar después"; el costo futuro de haber elegido una solución rápida y sucia ahora en lugar de una bien diseñada.

## 🏗️ 7. Arquitectura y Entornos de Desarrollo
*   **Arquitectura Cliente-Servidor;** *Client-Server*; "El frente y el fondo"; modelo donde una aplicación (cliente) le pide datos a otra (servidor de base de datos), que es como solemos trabajar en la materia.
*   **Entorno de Producción;** *Production* / *Prod*; "El vivo" / "Donde están los usuarios reales"; el servidor o lugar final donde el software está funcionando de verdad con datos reales.
*   **Entorno de Desarrollo / Pruebas;** *Staging* / *Dev* / *QA*; "El laboratorio"; lugar donde los programadores prueban el código y la base de datos sin riesgo de romper los datos reales de los usuarios.
*   **Despliegue;** *Deploy* / *Release*; "Subir la app"; el proceso de pasar el código que programamos en nuestra PC al servidor para que otros puedan usarlo.

## 🛠️ 8. Herramientas y Código (Tipos de Test)
*   **Repositorio;** *Repo* / *Git*; "Donde está el código"; lugar centralizado (como GitHub) donde se guarda el código fuente y se lleva el historial de todos los cambios realizados.
*   **Integración de Cambios;** *Merge* / *Pull Request (PR)*; "Combinar el código"; proceso de unir el código que hizo un programador con el código principal del proyecto asegurando que no haya conflictos.
*   **Refactorización;** *Refactoring*; "Limpiar o emprolijar el código"; cambiar la estructura interna del código para que sea más legible y mantenible, sin cambiar lo que hace (muy similar a la Normalización en BD).
*   **Pruebas Unitarias;** *Unit Testing*; "Testear una funcioncita"; verificar que una pequeña pieza de código (como una función o un método) funcione correctamente de forma aislada.
*   **Pruebas de Integración;** *Integration Testing*; "Probar que todo encaje"; "Cruzar los módulos"; validar que dos o más componentes del sistema (por ejemplo, el código de la app y la base de datos) interactúen correctamente entre sí.
*   **Pruebas de Regresión;** *Regression Testing*; "Que no se rompa lo viejo"; "Re-testear"; volver a ejecutar pruebas sobre funcionalidades que ya andaban para asegurar que los cambios nuevos no introdujeron errores en lo que ya funcionaba.
*   **Pruebas de Extremo a Extremo;** *End-to-End Testing* (E2E) / *System Testing*; "El recorrido completo"; "El flujo de punta a punta"; simular el camino real que haría un usuario en la aplicación, desde que abre el navegador hasta que guarda un dato en la base.
*   **Pruebas de Aceptación;** *User Acceptance Testing* (UAT); "El okey del cliente"; "La entrega final"; etapa donde el usuario o cliente real prueba el software para confirmar que cumple con lo que pidió originalmente.
*   **Pruebas de Humo;** *Smoke Testing*; "Que no salga humo al prenderlo"; "Testeo rápido"; un conjunto de pruebas mínimas y veloces para verificar que la aplicación al menos arranca y no tiene fallos críticos que impidan seguir probando.
*   **Pruebas de Rendimiento;** *Performance Testing* / *Stress Testing*; "Ver si aguanta"; "Pruebas de carga"; medir cómo responde el sistema cuando hay muchísimos usuarios al mismo tiempo o una cantidad enorme de datos en la base.
*   **Pruebas de Usabilidad;** *Usability Testing* / UX *Testing*; "Ver si es fácil de usar"; "Prueba de botones"; evaluar qué tan intuitivo y cómodo resulta el programa para una persona real.
*   **Pruebas de Caja Negra;** *Black Box Testing*; "Probar sin ver el código"; "Testeo de afuera"; probar el sistema basándose solo en las entradas y salidas, sin conocer cómo está programado por dentro.
*   **Pruebas de Caja Blanca;** *White Box Testing*; "Probar viendo el código"; "Testeo de lógica"; diseñar pruebas conociendo la estructura interna, los algoritmos y el flujo del código fuente.
