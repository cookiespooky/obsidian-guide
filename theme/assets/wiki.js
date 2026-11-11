/* Ящик с содержанием на узком экране: открыть кнопкой, закрыть крестиком, затемнением или Esc. Без скрипта
   ящика нет, но содержание остаётся на главной странице. */
(function () {
  var drawer = document.querySelector('[data-drawer]');
  var overlay = document.querySelector('[data-drawer-overlay]');
  var openBtn = document.querySelector('[data-drawer-open]');
  if (!drawer || !overlay || !openBtn) return;
  function set(open) {
    if (open) { drawer.hidden = false; overlay.hidden = false; drawer.offsetWidth; }
    drawer.classList.toggle('is-open', open);
    overlay.classList.toggle('is-open', open);
    drawer.setAttribute('aria-hidden', String(!open));
    openBtn.setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('is-locked', open);
    if (!open) setTimeout(function () { if (!drawer.classList.contains('is-open')) { drawer.hidden = true; overlay.hidden = true; } }, 280);
  }
  openBtn.addEventListener('click', function () { set(true); });
  overlay.addEventListener('click', function () { set(false); });
  drawer.querySelector('[data-drawer-close]').addEventListener('click', function () { set(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') set(false); });
})();

/* Кнопка «Копировать» в правом верхнем углу каждого блока кода: тексты запросов в курсе берут целиком. */
(function () {
  if (!navigator.clipboard) return;
  Array.prototype.forEach.call(document.querySelectorAll('.prose pre'), function (pre) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'code-copy';
    btn.textContent = 'Копировать';
    btn.addEventListener('click', function () {
      var code = pre.querySelector('code') || pre;
      navigator.clipboard.writeText(code.innerText.replace(/\n$/, '')).then(function () {
        btn.textContent = 'Скопировано';
        btn.classList.add('is-done');
        setTimeout(function () { btn.textContent = 'Копировать'; btn.classList.remove('is-done'); }, 1600);
      });
    });
    pre.appendChild(btn);
  });
})();

/* Меню помнит, докуда его прокрутили: после перехода оно стоит там же, а не с начала. Если открытый материал
   при этом не виден (пришли по ссылке из текста или с другого сайта) — меню прокручивается к нему. */
(function () {
  var KEY = 'wiki-menu-scroll';
  var saved = {};
  try { saved = JSON.parse(sessionStorage.getItem(KEY) || '{}'); } catch (e) {}
  Array.prototype.forEach.call(document.querySelectorAll('.side, [data-drawer]'), function (box, i) {
    function show() {
      var cur = box.querySelector('[aria-current="page"]');
      if (!cur || !box.clientHeight) return;
      var a = cur.getBoundingClientRect(), b = box.getBoundingClientRect();
      if (a.top < b.top + 8 || a.bottom > b.bottom - 8) box.scrollTop += a.top - b.top - (box.clientHeight - a.height) / 2;
    }
    if (saved[i]) box.scrollTop = saved[i];
    show();
    if (box.hasAttribute('data-drawer')) {      // ящик скрыт до открытия: место в нём выставляется, когда он открыт
      var btn = document.querySelector('[data-drawer-open]');
      if (btn) btn.addEventListener('click', function () { if (saved[i]) box.scrollTop = saved[i]; show(); });
    }
    box.addEventListener('scroll', function () {
      saved[i] = box.scrollTop;
      try { sessionStorage.setItem(KEY, JSON.stringify(saved)); } catch (e) {}
    }, { passive: true });
  });
})();
