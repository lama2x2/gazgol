// Редактор домашек: работает, когда конспект открыт через локальный сервер
// (python3 pycourse/lyceum.py → http://localhost:4002). Иначе показывает, как его включить.
(function () {
  var local = /^https?:$/.test(location.protocol) && (location.hostname === "localhost" || location.hostname === "127.0.0.1");
  var serverReady = local ? fetch("/api/ping").then(function (r) { return r.ok; }, function () { return false; }) : Promise.resolve(false);
  var dirty = {};

  window.addEventListener("beforeunload", function (e) {
    for (var k in dirty) if (dirty[k]) { e.preventDefault(); e.returnValue = ""; return; }
  });

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function insert(ta, text) {
    ta.focus();
    if (!document.execCommand || !document.execCommand("insertText", false, text)) {
      ta.setRangeText(text, ta.selectionStart, ta.selectionEnd, "end");
      ta.dispatchEvent(new Event("input"));
    }
  }

  function keys(ta, onCheck, onSave) {
    ta.addEventListener("keydown", function (e) {
      var mod = e.metaKey || e.ctrlKey;
      if (mod && e.key === "Enter") { e.preventDefault(); onCheck(); return; }
      if (mod && (e.key === "s" || e.key === "ы")) { e.preventDefault(); onSave(); return; }
      if (e.key === "Tab" && !e.shiftKey && !mod) { e.preventDefault(); insert(ta, "    "); return; }
      if (e.key === "Tab" && e.shiftKey && !mod) {
        // убрать до 4 пробелов в начале текущей строки
        e.preventDefault();
        var v = ta.value, start = v.lastIndexOf("\n", ta.selectionStart - 1) + 1;
        var n = (v.slice(start).match(/^ {1,4}/) || [""])[0].length;
        if (n) {
          var pos = ta.selectionStart;
          ta.setSelectionRange(start, start + n);
          insert(ta, "");
          ta.selectionStart = ta.selectionEnd = Math.max(start, pos - n);
        }
        return;
      }
      if (e.key === "Enter" && !mod && !e.shiftKey) {
        // сохраняем отступ текущей строки, после двоеточия добавляем ещё 4 пробела
        var before = ta.value.slice(0, ta.selectionStart);
        var line = before.slice(before.lastIndexOf("\n") + 1);
        var indent = (line.match(/^[\t ]*/) || [""])[0];
        if (/:\s*(#.*)?$/.test(line)) indent += "    ";
        e.preventDefault();
        insert(ta, "\n" + indent);
      }
    });
  }

  function hint(panel) {
    var h = el("div", "hint");
    var p1 = el("p", null, "Писать и проверять код прямо здесь можно, когда конспект открыт через локальную проверяющую систему. В корне репозитория запусти:");
    var c = el("pre"); c.appendChild(el("code", null, "python3 pycourse/lyceum.py"));
    var p2 = el("p", null, "и открой http://localhost:4002 — там у каждой домашки будет редактор и кнопка «Проверить». Код сохраняется в тот же tasks.py, так что можно переключаться между браузером и IDE.");
    h.append(p1, c, p2);
    panel.appendChild(h);
  }

  function render(hw, panel, res) {
    var old = panel.querySelector(".build"); if (old) old.remove();
    var status = panel.querySelector(".status");
    hw.querySelectorAll(".task").forEach(function (t) {
      t.classList.remove("ok", "bad");
      var f = t.querySelector(".fails"); if (f) f.remove();
      var v = t.querySelector(".verdict"); if (v) v.remove();
    });
    if (res.build_error) {
      status.textContent = "💥 Тесты не запустились";
      var b = el("pre", "build", res.build_error);
      panel.appendChild(b);
      return;
    }
    var byName = {}; res.tests.forEach(function (r) { byName[r.name] = r; });
    var ok = 0, all = 0;
    hw.querySelectorAll(".task").forEach(function (t) {
      var r = byName[t.dataset.test];
      if (!r) return;
      all++;
      var label = t.querySelector("label span");
      var v = el("span", "verdict", r.pass ? "засчитано" : "не прошло");
      label.appendChild(v);
      if (r.pass) {
        ok++;
        t.classList.add("ok");
        var box = t.querySelector("input");
        if (!box.checked) { box.checked = true; box.dispatchEvent(new Event("change")); }
      } else {
        t.classList.add("bad");
        if (r.output && r.output.length) {
          var f = el("pre", "fails", r.output.join("\n"));
          t.querySelector("label").after(f);
        }
      }
    });
    status.textContent = (ok === all ? "✅ " : "❌ ") + ok + "/" + all + " засчитано";
  }

  function editor(hw, panel) {
    var lesson = hw.dataset.lesson;
    var ta = el("textarea");
    ta.id = "code-" + lesson;
    ta.spellcheck = false;
    ta.setAttribute("autocapitalize", "off");
    ta.setAttribute("autocomplete", "off");
    ta.setAttribute("aria-label", "Код урока " + lesson.slice(0, -1) + "." + lesson.slice(-1));
    var bar = el("div", "bar");
    var check = el("button", "primary", "Проверить");
    check.type = "button";
    var reload = el("button", null, "Загрузить с диска");
    reload.type = "button";
    var status = el("span", "status", "");
    var keysHint = el("span", null, ""); keysHint.innerHTML = "<kbd>⌘/Ctrl+Enter</kbd> проверить · <kbd>⌘/Ctrl+S</kbd> сохранить";
    keysHint.style.fontSize = "12px";
    bar.append(check, reload, status);
    panel.append(ta, bar, keysHint);

    function load() {
      status.textContent = "Загружаю…";
      return fetch("/api/lessons/" + lesson + "/code").then(function (r) { return r.text(); }).then(function (code) {
        ta.value = code; dirty[lesson] = false; status.textContent = "";
      }, function () { status.textContent = "Не удалось загрузить файл"; });
    }
    function save() {
      var pos = ta.selectionStart;
      return fetch("/api/lessons/" + lesson + "/code", { method: "PUT", body: ta.value })
        .then(function (r) { if (!r.ok) throw new Error(); return r.text(); })
        .then(function (code) {
          if (code !== ta.value) { ta.value = code; ta.selectionStart = ta.selectionEnd = Math.min(pos, code.length); }
          dirty[lesson] = false;
          status.textContent = "Сохранено";
        });
    }
    function run() {
      check.disabled = true;
      status.textContent = "Проверяю…";
      save().then(function () {
        return fetch("/api/lessons/" + lesson + "/check", { method: "POST" }).then(function (r) { return r.json(); });
      }).then(function (res) { render(hw, panel, res); }, function () {
        status.textContent = "Сервер не ответил — он запущен?";
      }).then(function () { check.disabled = false; });
    }
    ta.addEventListener("input", function () { dirty[lesson] = true; if (status.textContent === "Сохранено") status.textContent = ""; });
    check.addEventListener("click", run);
    reload.addEventListener("click", function () {
      if (dirty[lesson] && !panel.querySelector(".confirm")) {
        var c = el("button", "confirm", "Точно? Несохранённые правки пропадут");
        c.type = "button";
        c.addEventListener("click", function () { c.remove(); load(); });
        bar.appendChild(c);
        setTimeout(function () { c.remove(); }, 4000);
        return;
      }
      load();
    });
    keys(ta, run, function () { save().catch(function () { status.textContent = "Не удалось сохранить"; }); });
    load().then(function () { ta.focus(); });
  }

  document.querySelectorAll(".hw").forEach(function (hw) {
    var run = hw.querySelector(".run");
    var btn = el("button", "primary", "Решать здесь");
    btn.type = "button";
    run.prepend(btn);
    var panel = null;
    btn.addEventListener("click", function () {
      if (panel) { panel.hidden = !panel.hidden; btn.textContent = panel.hidden ? "Решать здесь" : "Скрыть редактор"; return; }
      panel = el("div", "ed");
      hw.appendChild(panel);
      btn.textContent = "Скрыть редактор";
      serverReady.then(function (ok) { ok ? editor(hw, panel) : hint(panel); });
    });
  });
})();
