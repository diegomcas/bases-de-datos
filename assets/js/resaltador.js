/* ==========================================================================
   RESALTADOR — marcar y subrayar un apunte en pantalla

   Se usa en las páginas de estudio, junto con assets/css/estudio.css:

       <script src="../../assets/js/resaltador.js" defer></script>

   Qué hace:
     · el alumno selecciona texto y elige un color (o subrayado);
     · la marca se guarda en el navegador y vuelve al recargar la página;
     · con la goma, un clic sobre una marca la saca;
     · imprimir sale con las marcas puestas (ver @media print de estudio.css).

   Dónde se guarda: localStorage, bajo una clave que sale del nombre del
   archivo. Cada apunte tiene sus marcas y no viajan a ningún lado: son del
   navegador de ese alumno. Si alguien limpia los datos del navegador, se van.

   Cómo se referencia una marca: por la posición del párrafo dentro del
   apunte, los dos offsets de texto y una copia del texto marcado. Si el
   apunte se corrige y el párrafo cambió, la marca se busca por su texto; si
   tampoco aparece, se descarta en silencio. Nunca se restaura sobre un texto
   distinto del que se marcó.
   ========================================================================== */

(function () {
  'use strict';

  var CUERPO = document.querySelector('.apunte');
  if (!CUERPO) return;

  // «pre» está en la lista porque resaltar media cláusula de una consulta es
  // de las primeras cosas que alguien quiere marcar, y estudio.css ya tiene
  // el estilo de la marca dentro del código.
  var MARCABLES = 'p, li, h2, h3, h4, td, th, dd, dt, figcaption, .sintaxis, pre';
  var CLAVE = 'marcas:' + (location.pathname.split('/').pop() || 'apunte');

  var TINTAS = [
    { id: 'amarilla', clase: 'marca-amarilla', rotulo: 'Resaltar en amarillo', tecla: '1' },
    { id: 'verde', clase: 'marca-verde', rotulo: 'Resaltar en verde', tecla: '2' },
    { id: 'rosa', clase: 'marca-rosa', rotulo: 'Resaltar en rosa', tecla: '3' },
    { id: 'linea', clase: 'marca-linea', rotulo: 'Subrayar', tecla: '4' }
  ];

  var tintaActiva = TINTAS[0];
  var goma = false;
  var bloques = [];
  var marcas = [];

  // -----------------------------------------------------------------------
  // Guardado
  // -----------------------------------------------------------------------

  function leerGuardadas() {
    try {
      var crudo = localStorage.getItem(CLAVE);
      return crudo ? JSON.parse(crudo) : [];
    } catch (e) {
      return [];
    }
  }

  function guardar() {
    try {
      localStorage.setItem(CLAVE, JSON.stringify(marcas));
    } catch (e) {
      avisar('No se pudieron guardar las marcas en este navegador.');
    }
  }

  // -----------------------------------------------------------------------
  // Offsets de texto dentro de un bloque
  // -----------------------------------------------------------------------

  function nodosDeTexto(elemento) {
    var recorrido = document.createTreeWalker(elemento, NodeFilter.SHOW_TEXT, null);
    var salida = [];
    var nodo;
    while ((nodo = recorrido.nextNode())) salida.push(nodo);
    return salida;
  }

  /* Cuántos caracteres hay en el bloque antes del punto (contenedor, offset). */
  function offsetDePunto(bloque, contenedor, offset) {
    if (contenedor === bloque) {
      var previos = 0;
      for (var i = 0; i < offset && i < bloque.childNodes.length; i++) {
        previos += (bloque.childNodes[i].textContent || '').length;
      }
      return previos;
    }
    var acumulado = 0;
    var nodos = nodosDeTexto(bloque);
    for (var j = 0; j < nodos.length; j++) {
      if (nodos[j] === contenedor) return acumulado + offset;
      acumulado += nodos[j].data.length;
    }
    return null;
  }

  function envolver(bloque, desde, hasta, clase) {
    var pedazos = [];
    var pos = 0;
    var nodos = nodosDeTexto(bloque);
    for (var i = 0; i < nodos.length; i++) {
      var largo = nodos[i].data.length;
      var a = Math.max(desde, pos);
      var b = Math.min(hasta, pos + largo);
      if (a < b) pedazos.push([nodos[i], a - pos, b - pos]);
      pos += largo;
    }
    for (var j = 0; j < pedazos.length; j++) {
      var nodo = pedazos[j][0];
      var ini = pedazos[j][1];
      var fin = pedazos[j][2];
      if (nodo.parentNode && nodo.parentNode.classList &&
          nodo.parentNode.classList.contains('marca')) continue;
      var medio = ini > 0 ? nodo.splitText(ini) : nodo;
      if (fin - ini < medio.data.length) medio.splitText(fin - ini);
      var span = document.createElement('span');
      span.className = 'marca ' + clase;
      medio.parentNode.insertBefore(span, medio);
      span.appendChild(medio);
    }
    return pedazos.length > 0;
  }

  function desenvolver(span) {
    var padre = span.parentNode;
    while (span.firstChild) padre.insertBefore(span.firstChild, span);
    padre.removeChild(span);
    padre.normalize();
  }

  // -----------------------------------------------------------------------
  // Pintar lo guardado
  // -----------------------------------------------------------------------

  function texto(bloque) {
    return bloque.textContent || '';
  }

  /* Dónde está ahora el texto de una marca guardada.

     El apunte se corrige y se le agregan secciones, y eso corre los índices de
     los párrafos: una marca del final se guardó con el índice 491 y después de
     sumar una sección ese 491 es otro párrafo. Por eso la búsqueda va de lo
     más probable a lo más caro: el mismo párrafo, los de alrededor, y al final
     todo el apunte, quedándose con el más cercano al índice viejo. Si aparece
     en otro lugar, la marca se reubica y se guarda el índice nuevo. */
  function ubicar(m) {
    var bloque = bloques[m.b];
    if (bloque && texto(bloque).slice(m.d, m.h) === m.t) {
      return { b: m.b, d: m.d, h: m.h };
    }
    if (!m.t) return null;

    if (bloque) {
      var aca = texto(bloque).indexOf(m.t);
      if (aca !== -1) return { b: m.b, d: aca, h: aca + m.t.length };
    }

    var candidatos = [];
    for (var i = 0; i < bloques.length; i++) {
      var donde = texto(bloques[i]).indexOf(m.t);
      if (donde !== -1) candidatos.push({ b: i, d: donde, h: donde + m.t.length });
    }
    if (!candidatos.length) return null;

    var mejor = candidatos[0];
    for (var j = 1; j < candidatos.length; j++) {
      if (Math.abs(candidatos[j].b - m.b) < Math.abs(mejor.b - m.b)) mejor = candidatos[j];
    }
    return mejor;
  }

  function restaurar() {
    var guardadas = leerGuardadas();
    var quedan = [];
    var perdidas = 0;
    for (var i = 0; i < guardadas.length; i++) {
      var m = guardadas[i];
      var lugar = ubicar(m);
      if (!lugar) {
        // el texto no está en esta versión del apunte. La marca NO se borra:
        // puede ser un párrafo que se reescribió hoy y vuelve mañana, y lo que
        // el alumno marcó no se tira por una edición nuestra.
        quedan.push(m);
        perdidas++;
        continue;
      }
      if (envolver(bloques[lugar.b], lugar.d, lugar.h, m.c)) {
        quedan.push({ b: lugar.b, d: lugar.d, h: lugar.h, t: m.t, c: m.c });
      } else {
        quedan.push(m);
        perdidas++;
      }
    }
    marcas = quedan;
    guardar();
    contar();
    if (perdidas) {
      avisar(perdidas === 1
        ? 'Una marca quedó sobre un texto que cambió; se guarda por si vuelve.'
        : perdidas + ' marcas quedaron sobre textos que cambiaron; se guardan por si vuelven.');
    }
  }

  // -----------------------------------------------------------------------
  // Marcar lo seleccionado
  // -----------------------------------------------------------------------

  function marcarSeleccion() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || sel.rangeCount === 0) {
      avisar('Seleccioná un texto y después elegí el color.');
      return;
    }
    var rango = sel.getRangeAt(0);
    if (!CUERPO.contains(rango.commonAncestorContainer)) {
      avisar('Se puede marcar dentro del apunte, no en los márgenes.');
      return;
    }

    var nuevas = 0;
    for (var i = 0; i < bloques.length; i++) {
      var bloque = bloques[i];
      // intersectsNode y no containsNode: una frase suelta adentro de un
      // párrafo no «contiene» a ese párrafo ni siquiera parcialmente, y con
      // containsNode ese caso —el más común— no se marcaba
      if (!rango.intersectsNode(bloque)) continue;

      var largo = texto(bloque).length;
      var desde = 0;
      var hasta = largo;
      if (bloque.contains(rango.startContainer) || bloque === rango.startContainer) {
        var d = offsetDePunto(bloque, rango.startContainer, rango.startOffset);
        if (d !== null) desde = d;
      }
      if (bloque.contains(rango.endContainer) || bloque === rango.endContainer) {
        var h = offsetDePunto(bloque, rango.endContainer, rango.endOffset);
        if (h !== null) hasta = h;
      }
      if (hasta <= desde) continue;

      var marcado = texto(bloque).slice(desde, hasta);
      if (!marcado.trim()) continue;

      if (envolver(bloque, desde, hasta, tintaActiva.clase)) {
        marcas.push({ b: i, d: desde, h: hasta, t: marcado, c: tintaActiva.clase });
        nuevas++;
      }
    }

    sel.removeAllRanges();
    if (nuevas) {
      guardar();
      contar();
    } else {
      avisar('No quedó nada para marcar en esa selección.');
    }
  }

  function borrarMarca(span) {
    var bloque = span.closest(MARCABLES);
    var indice = bloques.indexOf(bloque);
    var contenido = span.textContent;
    desenvolver(span);
    marcas = marcas.filter(function (m) {
      return !(m.b === indice && m.t === contenido);
    });
    guardar();
    contar();
  }

  function borrarTodo() {
    var puestas = CUERPO.querySelectorAll('.marca');
    for (var i = puestas.length - 1; i >= 0; i--) desenvolver(puestas[i]);
    marcas = [];
    guardar();
    contar();
    avisar('Se borraron todas las marcas de esta página.');
  }

  // -----------------------------------------------------------------------
  // Llevarse las marcas a otro navegador
  //
  // Lo marcado vive en el navegador de cada alumno, así que pasar de la
  // máquina del aula al celular necesita una puerta. Hay dos, y las dos
  // mueven exactamente el mismo contenido:
  //
  //   · un archivo .json, para guardarlo o repartirlo;
  //   · un código de texto, para copiar y pegar, que es lo cómodo cuando
  //     manejar archivos molesta.
  //
  // El archivo lleva las marcas de TODAS las páginas de estudio que tenga
  // ese navegador, no solo la abierta: se importa una vez y quedan todas.
  // -----------------------------------------------------------------------

  var FORMATO = 'marcas-bdd/1';
  var PREFIJO_Z = 'BDD1Z:';   // comprimido
  var PREFIJO_P = 'BDD1P:';   // sin comprimir, si el navegador no comprime

  function paginasGuardadas() {
    var paginas = {};
    try {
      for (var i = 0; i < localStorage.length; i++) {
        var clave = localStorage.key(i);
        if (clave && clave.indexOf('marcas:') === 0) {
          paginas[clave.slice(7)] = JSON.parse(localStorage.getItem(clave) || '[]');
        }
      }
    } catch (e) { /* sin localStorage no hay nada que exportar */ }
    return paginas;
  }

  function paquete() {
    return {
      formato: FORMATO,
      generado: new Date().toISOString().slice(0, 10),
      paginas: paginasGuardadas()
    };
  }

  function cuantas(paginas) {
    var total = 0;
    for (var p in paginas) total += (paginas[p] || []).length;
    return total;
  }

  /* Fusiona sin repetir. Una marca ya está si coincide el color y el texto
     marcado, o si coincide color y posición exacta: lo primero la reconoce
     aunque el apunte se haya corregido y los párrafos se hayan corrido. */
  function fusionar(paginas) {
    var nuevas = 0, repetidas = 0, otras = 0;
    for (var pagina in paginas) {
      var entrantes = paginas[pagina] || [];
      var clave = 'marcas:' + pagina;
      var propias;
      try {
        propias = JSON.parse(localStorage.getItem(clave) || '[]');
      } catch (e) {
        propias = [];
      }
      var vistas = {};
      propias.forEach(function (m) {
        vistas[m.c + '|' + m.t] = true;
        vistas[m.c + '|' + m.b + '|' + m.d + '|' + m.h] = true;
      });
      entrantes.forEach(function (m) {
        if (!m || !m.c) return;
        if (vistas[m.c + '|' + m.t] || vistas[m.c + '|' + m.b + '|' + m.d + '|' + m.h]) {
          repetidas++;
          return;
        }
        vistas[m.c + '|' + m.t] = true;
        propias.push({ b: m.b, d: m.d, h: m.h, t: m.t, c: m.c });
        if (pagina === CLAVE.slice(7)) nuevas++; else otras++;
      });
      try {
        localStorage.setItem(clave, JSON.stringify(propias));
      } catch (e) {
        avisar('No hay lugar en este navegador para guardar las marcas.');
      }
    }
    return { nuevas: nuevas, repetidas: repetidas, otras: otras };
  }

  // --- texto <-> bytes <-> base64, sin dependencias ---

  function aBase64(bytes) {
    var trozos = [];
    for (var i = 0; i < bytes.length; i += 8192) {
      trozos.push(String.fromCharCode.apply(null, bytes.subarray(i, i + 8192)));
    }
    return btoa(trozos.join(''));
  }

  function deBase64(texto) {
    var binario = atob(texto);
    var bytes = new Uint8Array(binario.length);
    for (var i = 0; i < binario.length; i++) bytes[i] = binario.charCodeAt(i);
    return bytes;
  }

  function comprimir(texto) {
    var bytes = new TextEncoder().encode(texto);
    if (typeof CompressionStream === 'undefined') {
      return Promise.resolve(PREFIJO_P + aBase64(bytes));
    }
    var cs = new CompressionStream('gzip');
    var escritor = cs.writable.getWriter();
    escritor.write(bytes);
    escritor.close();
    return new Response(cs.readable).arrayBuffer().then(function (buf) {
      return PREFIJO_Z + aBase64(new Uint8Array(buf));
    });
  }

  function descomprimir(codigo) {
    if (codigo.indexOf(PREFIJO_P) === 0) {
      return Promise.resolve(new TextDecoder().decode(deBase64(codigo.slice(PREFIJO_P.length))));
    }
    var bytes = deBase64(codigo.slice(PREFIJO_Z.length));
    if (typeof DecompressionStream === 'undefined') {
      return Promise.reject(new Error('este navegador no puede descomprimir el código'));
    }
    var ds = new DecompressionStream('gzip');
    var escritor = ds.writable.getWriter();
    escritor.write(bytes);
    escritor.close();
    return new Response(ds.readable).text();
  }

  // --- las cuatro acciones ---

  function exportarArchivo() {
    var datos = paquete();
    if (!cuantas(datos.paginas)) {
      avisar('Todavía no hay ninguna marca para exportar.');
      return;
    }
    var blob = new Blob([JSON.stringify(datos, null, 1)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'marcas-' + (CLAVE.slice(7).replace(/\.html$/, '') || 'apunte') + '.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    avisar('Archivo descargado con ' + cuantas(datos.paginas) + ' marcas.');
  }

  function copiarCodigo() {
    var datos = paquete();
    if (!cuantas(datos.paginas)) {
      avisar('Todavía no hay ninguna marca para copiar.');
      return;
    }
    comprimir(JSON.stringify(datos)).then(function (codigo) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        return navigator.clipboard.writeText(codigo).then(function () {
          avisar('Código copiado: ' + cuantas(datos.paginas) + ' marcas, ' +
                 Math.max(1, Math.round(codigo.length / 1024)) + ' KB. Pegalo en el otro navegador.');
        });
      }
      mostrarParaCopiar(codigo);
    }).catch(function () {
      avisar('No se pudo generar el código en este navegador.');
    });
  }

  function importarTexto(texto) {
    texto = (texto || '').trim();
    if (!texto) {
      avisar('Pegá el código o elegí un archivo.');
      return;
    }
    var leer = (texto.indexOf(PREFIJO_Z) === 0 || texto.indexOf(PREFIJO_P) === 0)
      ? descomprimir(texto)
      : Promise.resolve(texto);

    leer.then(function (json) {
      var datos = JSON.parse(json);
      var paginas = datos && datos.paginas ? datos.paginas : null;
      // un archivo viejo podría ser la lista pelada de una sola página
      if (!paginas && Array.isArray(datos)) {
        paginas = {};
        paginas[CLAVE.slice(7)] = datos;
      }
      if (!paginas) throw new Error('formato desconocido');

      var r = fusionar(paginas);
      var puestas = CUERPO.querySelectorAll('.marca');
      for (var i = puestas.length - 1; i >= 0; i--) desenvolver(puestas[i]);
      restaurar();

      var partes = [];
      partes.push(r.nuevas + (r.nuevas === 1 ? ' marca nueva' : ' marcas nuevas') + ' en esta página');
      if (r.otras) partes.push(r.otras + ' en otras páginas');
      if (r.repetidas) partes.push(r.repetidas + ' ya estaban');
      avisar(partes.join(', ') + '.');
      cerrarMenu();
    }).catch(function () {
      avisar('Ese texto no es un juego de marcas válido.');
    });
  }

  function importarArchivo() {
    var entrada = document.createElement('input');
    entrada.type = 'file';
    entrada.accept = '.json,application/json,text/plain';
    entrada.addEventListener('change', function () {
      var archivo = entrada.files && entrada.files[0];
      if (!archivo) return;
      var lector = new FileReader();
      lector.onload = function () { importarTexto(String(lector.result)); };
      lector.onerror = function () { avisar('No se pudo leer el archivo.'); };
      lector.readAsText(archivo);
    });
    entrada.click();
  }

  // -----------------------------------------------------------------------
  // Barra
  // -----------------------------------------------------------------------

  var cuenta, aviso, relojAviso, menu;

  function avisar(mensaje) {
    if (!aviso) return;
    aviso.textContent = mensaje;
    aviso.classList.add('visible');
    clearTimeout(relojAviso);
    relojAviso = setTimeout(function () {
      aviso.classList.remove('visible');
    }, 2600);
  }

  function contar() {
    if (cuenta) cuenta.textContent = marcas.length ? String(marcas.length) : '—';
  }

  function cerrarMenu() {
    if (menu) {
      menu.hidden = true;
      var b = document.querySelector('.barra-estudio [data-menu]');
      if (b) b.setAttribute('aria-expanded', 'false');
    }
  }

  function mostrarParaCopiar(codigo) {
    abrirMenu();
    var area = menu.querySelector('textarea');
    area.value = codigo;
    area.focus();
    area.select();
    avisar('Copiá este código y pegalo en el otro navegador.');
  }

  function abrirMenu() {
    menu.hidden = false;
    var b = document.querySelector('.barra-estudio [data-menu]');
    if (b) b.setAttribute('aria-expanded', 'true');
  }

  function armarMenu() {
    menu = document.createElement('div');
    menu.className = 'menu-estudio';
    menu.hidden = true;
    menu.innerHTML =
      '<h4>Llevar las marcas a otro navegador</h4>' +
      '<p>Lo que marcás se guarda en este navegador. Para tenerlo en otra ' +
      'computadora o en el celular, bajá el archivo o copiá el código y traelo del otro lado.</p>' +
      '<div class="acciones-estudio">' +
      '<button type="button" data-accion="archivo">Bajar archivo</button>' +
      '<button type="button" data-accion="codigo">Copiar código</button>' +
      '</div>' +
      '<h4>Traer marcas</h4>' +
      '<div class="acciones-estudio">' +
      '<button type="button" data-accion="abrir">Elegir archivo…</button>' +
      '</div>' +
      '<textarea rows="3" placeholder="…o pegá acá el código y tocá Traer"></textarea>' +
      '<div class="acciones-estudio">' +
      '<button type="button" data-accion="pegar">Traer del código</button>' +
      '<button type="button" data-accion="cerrar">Cerrar</button>' +
      '</div>';

    menu.addEventListener('click', function (e) {
      var accion = e.target.getAttribute && e.target.getAttribute('data-accion');
      if (accion === 'archivo') exportarArchivo();
      else if (accion === 'codigo') copiarCodigo();
      else if (accion === 'abrir') importarArchivo();
      else if (accion === 'pegar') importarTexto(menu.querySelector('textarea').value);
      else if (accion === 'cerrar') cerrarMenu();
    });

    document.body.appendChild(menu);
  }

  function boton(clase, rotulo, alHacerClic) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = clase;
    b.title = rotulo;
    b.setAttribute('aria-label', rotulo);
    b.addEventListener('click', alHacerClic);
    return b;
  }

  function armarBarra() {
    var barra = document.createElement('div');
    barra.className = 'barra-estudio';
    barra.setAttribute('role', 'toolbar');
    barra.setAttribute('aria-label', 'Resaltador');

    TINTAS.forEach(function (tinta) {
      var b = boton(
        tinta.id === 'linea' ? '' : 'tinta-' + tinta.id,
        tinta.rotulo + ' (tecla ' + tinta.tecla + ')',
        function () {
          tintaActiva = tinta;
          goma = false;
          refrescarBotones(barra);
          marcarSeleccion();
        }
      );
      if (tinta.id === 'linea') b.innerHTML = '<u>A</u>';
      b.dataset.tinta = tinta.id;
      barra.appendChild(b);
    });

    var sep = document.createElement('span');
    sep.className = 'separador';
    barra.appendChild(sep);

    var bGoma = boton('', 'Goma: tocá una marca para sacarla', function () {
      goma = !goma;
      refrescarBotones(barra);
      avisar(goma ? 'Goma activada: tocá una marca para sacarla.' : 'Goma desactivada.');
    });
    bGoma.textContent = '⌫';
    bGoma.dataset.goma = '1';
    barra.appendChild(bGoma);

    var dobleToque = false;
    var bTodo = boton('', 'Borrar todas las marcas de esta página', function () {
      if (!dobleToque) {
        dobleToque = true;
        avisar('Tocá de nuevo para borrar todas las marcas.');
        setTimeout(function () { dobleToque = false; }, 3000);
        return;
      }
      dobleToque = false;
      borrarTodo();
    });
    bTodo.textContent = '✕';
    barra.appendChild(bTodo);

    cuenta = document.createElement('span');
    cuenta.className = 'cuenta';
    barra.appendChild(cuenta);

    var sep2 = document.createElement('span');
    sep2.className = 'separador';
    barra.appendChild(sep2);

    var bImprimir = boton('', 'Imprimir el apunte', function () { window.print(); });
    bImprimir.textContent = '⎙';
    barra.appendChild(bImprimir);

    var bMenu = boton('', 'Llevar las marcas a otro navegador', function () {
      if (menu.hidden) abrirMenu(); else cerrarMenu();
    });
    bMenu.textContent = '⋯';
    bMenu.dataset.menu = '1';
    bMenu.setAttribute('aria-expanded', 'false');
    barra.appendChild(bMenu);

    aviso = document.createElement('div');
    aviso.className = 'aviso-estudio';
    aviso.setAttribute('role', 'status');

    document.body.appendChild(aviso);
    document.body.appendChild(barra);
    refrescarBotones(barra);
  }

  function refrescarBotones(barra) {
    barra.querySelectorAll('button').forEach(function (b) {
      if (b.dataset.tinta) {
        b.setAttribute('aria-pressed', String(!goma && b.dataset.tinta === tintaActiva.id));
      } else if (b.dataset.goma) {
        b.setAttribute('aria-pressed', String(goma));
      }
    });
  }

  // -----------------------------------------------------------------------
  // Índice lateral y progreso
  // -----------------------------------------------------------------------

  function seguirLectura() {
    var enlaces = document.querySelectorAll('.mapa-lateral a[href^="#"]');
    var progreso = document.querySelector('.progreso-lectura');
    var mapa = document.querySelector('.mapa-lateral');
    var encabezado = document.querySelector('header');
    if (!enlaces.length && !progreso) return;

    var destinos = [];
    enlaces.forEach(function (a) {
      var seccion = document.getElementById(a.getAttribute('href').slice(1));
      if (seccion) destinos.push({ enlace: a, seccion: seccion });
    });

    var pendiente = false;
    function alScrollear() {
      if (pendiente) return;
      pendiente = true;
      requestAnimationFrame(function () {
        pendiente = false;
        if (progreso) {
          var alto = document.documentElement.scrollHeight - window.innerHeight;
          var avance = alto > 0 ? (window.scrollY / alto) * 100 : 0;
          progreso.style.width = Math.min(100, Math.max(0, avance)) + '%';
        }
        // el índice espera a que el encabezado salga de la pantalla
        if (mapa && encabezado) {
          var tope = parseFloat(getComputedStyle(mapa).top) || 0;
          mapa.classList.toggle('esperando',
            encabezado.getBoundingClientRect().bottom > tope);
        }
        var actual = null;
        for (var i = 0; i < destinos.length; i++) {
          if (destinos[i].seccion.getBoundingClientRect().top <= 120) actual = destinos[i];
        }
        destinos.forEach(function (d) { d.enlace.classList.remove('aqui'); });
        if (actual) actual.enlace.classList.add('aqui');
      });
    }

    window.addEventListener('scroll', alScrollear, { passive: true });
    alScrollear();
  }

  // -----------------------------------------------------------------------
  // Arranque
  // -----------------------------------------------------------------------

  bloques = Array.prototype.slice.call(CUERPO.querySelectorAll(MARCABLES));

  armarMenu();
  armarBarra();
  restaurar();
  seguirLectura();

  CUERPO.addEventListener('click', function (e) {
    var span = e.target.closest ? e.target.closest('.marca') : null;
    if (span && goma) {
      e.preventDefault();
      borrarMarca(span);
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { cerrarMenu(); return; }
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    var foco = document.activeElement;
    if (foco && (foco.tagName === 'INPUT' || foco.tagName === 'TEXTAREA' || foco.isContentEditable)) return;
    for (var i = 0; i < TINTAS.length; i++) {
      if (e.key === TINTAS[i].tecla) {
        tintaActiva = TINTAS[i];
        goma = false;
        var barra = document.querySelector('.barra-estudio');
        if (barra) refrescarBotones(barra);
        marcarSeleccion();
        return;
      }
    }
  });
})();
