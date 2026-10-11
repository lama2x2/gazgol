// Прогресс, отметки домашек, тренажёры. Состояние хранится только в этом браузере.
(function () {
  var wrap = document.querySelector(".wrap");
  var KEY = "go-course-p" + (wrap.dataset.part || "1");
  var state = { tasks: {}, quiz: {}, drafts: {} };
  try {
    var saved = JSON.parse(localStorage.getItem(KEY) || "null");
    if (saved) { state.tasks = saved.tasks || {}; state.quiz = saved.quiz || {}; state.drafts = saved.drafts || {}; }
  } catch (e) {}
  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }

  // ---------- ссылки на другие части: локально — через сервер, иначе — опубликованные страницы ----------
  var local = /^https?:$/.test(location.protocol) && (location.hostname === "localhost" || location.hostname === "127.0.0.1");
  document.querySelectorAll(".parts a").forEach(function (a) {
    var href = local ? a.dataset.local : a.dataset.remote;
    if (href) a.href = href; else if (!a.getAttribute("aria-current")) a.removeAttribute("href");
  });

  // ---------- прогресс ----------
  var boxes = document.querySelectorAll(".hw input[type=checkbox]");
  var quizzes = document.querySelectorAll(".quiz");
  function render() {
    var done = 0;
    document.querySelectorAll(".hw").forEach(function (hw) {
      var inputs = hw.querySelectorAll("input[type=checkbox]");
      var n = 0;
      inputs.forEach(function (i) { if (i.checked) n++; });
      done += n;
      var c = hw.querySelector(".count"); if (c) c.textContent = n + "/" + inputs.length;
    });
    var q = 0;
    quizzes.forEach(function (z) { if (state.quiz[z.dataset.id] === "solved") q++; });
    var prog = document.getElementById("prog");
    if (prog) prog.textContent = "код " + done + "/" + boxes.length + " · тренажёры " + q + "/" + quizzes.length;
    document.querySelectorAll(".cards a").forEach(function (a) {
      a.classList.toggle("done", state.quiz[a.dataset.id] === "solved");
    });
  }
  boxes.forEach(function (b) {
    b.checked = !!state.tasks[b.id];
    b.addEventListener("change", function () { state.tasks[b.id] = b.checked; save(); render(); });
  });

  // ---------- копирование команд ----------
  document.querySelectorAll(".hw .run button.copy").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var code = btn.parentElement.querySelector("code");
      function selectIt() {
        var r = document.createRange(); r.selectNodeContents(code);
        var s = getSelection(); s.removeAllRanges(); s.addRange(r);
        btn.textContent = "Выделено";
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code.textContent).then(function () { btn.textContent = "Скопировано"; }, selectIt);
      } else { selectIt(); }
      setTimeout(function () { btn.textContent = "Копировать"; }, 1600);
    });
  });

  // ---------- тренажёры ----------
  function norm(s) {
    return s.replace(/\r/g, "").split("\n").map(function (l) { return l.trim().replace(/\s+/g, " "); })
      .join("\n").replace(/^\n+|\n+$/g, "");
  }
  function setRes(z, cls, text) {
    var r = z.querySelector(".qres");
    r.className = "qres " + cls; r.textContent = text;
  }
  function reveal(z) { var a = z.querySelector(".qans"); if (a) a.hidden = false; }
  function solved(z, silent) {
    z.classList.add("solved");
    if (!silent) { state.quiz[z.dataset.id] = "solved"; save(); render(); }
    setRes(z, "ok", "✓ Верно");
    reveal(z);
  }

  quizzes.forEach(function (z) {
    var id = z.dataset.id, kind = z.dataset.kind;
    var check = z.querySelector(".qcheck"), show = z.querySelector(".qshow");

    if (kind === "output") {
      var inp = z.querySelector("textarea");
      var expected = z.dataset.answer;
      if (state.drafts[id]) inp.value = state.drafts[id];
      inp.addEventListener("input", function () { state.drafts[id] = inp.value; save(); });
      check.addEventListener("click", function () {
        if (!inp.value.trim()) { setRes(z, "no", "Сначала напиши свой ответ"); return; }
        if (norm(inp.value) === norm(expected)) solved(z);
        else setRes(z, "no", "Не совпало. Пройди по коду ещё раз строка за строкой");
      });
      inp.addEventListener("keydown", function (e) { if ((e.metaKey || e.ctrlKey) && e.key === "Enter") { e.preventDefault(); check.click(); } });
    }

    if (kind === "choice" || kind === "bug") {
      check.addEventListener("click", function () {
        var labels = z.querySelectorAll(".qopts label");
        var any = false, ok = true;
        labels.forEach(function (l) {
          var i = l.querySelector("input"), right = l.dataset.correct === "1";
          l.classList.remove("right", "wrong");
          if (i.checked) any = true;
          if (i.checked !== right) ok = false;
        });
        if (!any) { setRes(z, "no", "Выбери вариант"); return; }
        labels.forEach(function (l) {
          var i = l.querySelector("input");
          if (i.checked) l.classList.add(l.dataset.correct === "1" ? "right" : "wrong");
        });
        if (ok) solved(z); else setRes(z, "no", "Не совсем. Подумай ещё");
      });
    }

    if (kind === "open" || kind === "design" || kind === "review") {
      var ta = z.querySelector("textarea");
      var credit = z.querySelector(".qcredit");
      if (state.drafts[id]) ta.value = state.drafts[id];
      ta.addEventListener("input", function () { state.drafts[id] = ta.value; save(); });
      check.addEventListener("click", function () {
        if (ta.value.trim().length < 20) { setRes(z, "no", "Сначала ответь своими словами — хотя бы пару предложений"); return; }
        reveal(z); setRes(z, "peek", "Сравни свой ответ с эталоном и отметь, что упомянул");
      });
      if (credit) credit.addEventListener("click", function () {
        var pts = z.querySelectorAll(".qpoints input"), n = 0;
        pts.forEach(function (p) { if (p.checked) n++; });
        if (pts.length && n < Math.ceil(pts.length * 0.7)) {
          setRes(z, "no", "Отмечено " + n + " из " + pts.length + ". Дополни ответ и попробуй снова");
          return;
        }
        solved(z);
      });
    }

    if (show) show.addEventListener("click", function () {
      reveal(z);
      if (state.quiz[id] !== "solved") { state.quiz[id] = "shown"; save(); setRes(z, "peek", "Ответ подсмотрен — тренажёр не засчитан"); }
    });

    if (state.quiz[id] === "solved") solved(z, true);
    else if (state.quiz[id] === "shown") { reveal(z); setRes(z, "peek", "Ответ подсмотрен — тренажёр не засчитан"); }
  });

  render();
})();
