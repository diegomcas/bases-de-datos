<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bases de Datos · Índice de la materia</title>
<link rel="stylesheet" href="assets/css/fuentes.css">
<link rel="stylesheet" href="assets/css/base.css">
<link rel="stylesheet" href="assets/css/indice.css">
</head>
<body data-tema="indice">

<header>
  <div class="header-container">
    <span class="badge">{{ciclo_titulo}}</span>
    <h1>Bases de Datos</h1>
    <p>Todo el material de la materia, en el orden en que lo vamos construyendo:
       de por qué los datos importan, hasta una base que responde preguntas.</p>
    <div class="ciclo">
      <div class="ciclo-txt">
        <span>Semana <strong id="sem">—</strong> de {{ciclo_semanas}}</span>
        <span id="etapa">—</span>
      </div>
      <div class="barra"><div id="prog"></div></div>
    </div>
  </div>
</header>

<div class="sticky">
  <div class="sticky-in">
    <div class="buscador">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
      <input type="search" id="q" placeholder="Buscar un tema, una clase o un taller…" autocomplete="off" aria-label="Buscar material">
    </div>
    <nav class="saltos">
      <a href="#partida">Inicio</a>
      <a href="#casos">Casos</a>
      <a href="#t1">1.º trim.</a>
      <a href="#t2">2.º trim.</a>
      <a href="#t3">3.º trim.</a>
      <a href="#proyecto">Proyecto</a>
    </nav>
  </div>
</div>

<p id="sin-resultados">No hay material que coincida con esa búsqueda.</p>

<main>
{{contenido}}
</main>

<footer>
  <p><strong>Bases de Datos</strong> · Ciclo lectivo {{ciclo_anio}}</p>
  <p style="margin-top:6px;font-size:.85rem">
    Los talleres se resuelven con la base de El Chip cargada. Si un resultado no te da,
    lo primero a revisar es la carga de datos, no la consulta.</p>
  <p style="margin-top:12px;font-size:.82rem">
    Material bajo licencia
    <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es" rel="license">CC BY-NC-SA 4.0</a>
    · se puede usar y adaptar citando la fuente, sin fines comerciales.</p>
</footer>

<script>
/* ---------- progreso del ciclo ---------- */
(function () {
    var INICIO = {{ciclo_inicio}};
  var TOTAL = {{ciclo_semanas}};
  var sem = Math.floor((new Date() - INICIO) / 604800000) + 1;
  sem = Math.max(1, Math.min(TOTAL, sem));

  var etapa;
{{ciclo_etapas}}

  document.getElementById('sem').textContent = sem;
  document.getElementById('etapa').textContent = etapa;
  setTimeout(function () {
    document.getElementById('prog').style.width = (sem / TOTAL * 100) + '%';
  }, 150);
})();

/* ---------- buscador ---------- */
(function () {
  var campo = document.getElementById('q');
  var vacio = document.getElementById('sin-resultados');
  var unidades = Array.prototype.slice.call(document.querySelectorAll('.unidad'));
  var bandas = Array.prototype.slice.call(document.querySelectorAll('.trimestre'));

  // busca sin distinguir mayúsculas ni acentos: "agrupacion" encuentra "Agrupación"
  function normalizar(s) {
    return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  campo.addEventListener('input', function () {
    var t = normalizar(campo.value.trim());
    var hay = false;

    unidades.forEach(function (u) {
      var clases = u.querySelectorAll('.clase');
      var cab = u.querySelector('.u-cab');
      var intro = u.querySelector('.u-intro');
      var texto = normalizar((cab ? cab.textContent : '') +
                             (intro ? intro.textContent : ''));
      var porCabecera = !!t && texto.indexOf(t) !== -1;

      var visibles = 0;
      Array.prototype.forEach.call(clases, function (c) {
        var coincide = !t || porCabecera || normalizar(c.textContent).indexOf(t) !== -1;
        c.style.display = coincide ? '' : 'none';
        if (coincide) visibles++;
      });

      if (!clases.length) {
        visibles = (!t || normalizar(u.textContent).indexOf(t) !== -1) ? 1 : 0;
      }
      u.style.display = visibles ? '' : 'none';
      if (visibles) hay = true;
    });

    // una banda de trimestre sólo se muestra si le quedó alguna unidad visible
    bandas.forEach(function (b) {
      var visible = false;
      var n = b.nextElementSibling;
      while (n && !n.classList.contains('trimestre')) {
        if (n.classList.contains('unidad') && n.style.display !== 'none') visible = true;
        n = n.nextElementSibling;
      }
      b.style.display = (!t || visible) ? '' : 'none';
    });

    vacio.style.display = hay ? 'none' : 'block';
  });

  campo.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { campo.value = ''; campo.dispatchEvent(new Event('input')); }
  });
})();
</script>
</body>
</html>
