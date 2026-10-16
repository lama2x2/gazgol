#!/usr/bin/env python3
"""Сборка конспектов Python-курса из markdown-файлов в pycourse/content/partN/.

    python3 pycourse/tools/build.py            # собрать все части
    python3 pycourse/tools/build.py --verify   # + запустить код из «Что выведет?» и сверить ответы

Формат урока (content/partN/31.md):

    %% 7 | Название модуля            — разделитель модуля (перед первым уроком модуля)
    # 7.1 Название урока              — тема (рамка вверху каждого листа)
    @@                                — новый лист
    ## Заголовок блока                — новый блок
    обычный текст, `код`, **жирный**, [ссылка](url), - списки, 1. списки, | таблицы |, > цитаты
    ```python … ```                   — код с подсветкой (python, sql, bash, text)
    ::: py Заголовок / solve / warn / project / checklist … :::   — особые блоки
    ::: quiz output|choice|bug|open|design|review <id> [собес] [verify=exception|runs]
        (verify=exception: программа падает; последняя строка ответа — имя исключения)
        Вопрос (первая строка)
        … код, текст, варианты «- [ ]» / «- [x]» …
        --- answer   (для output — точный вывод; для open — эталонный ответ)
        --- why      (пояснение)
        --- points   (ключевые пункты для самопроверки)
    :::
    ::: hw 31
        * `имя` — описание {test_имя}
        + как решать
        ! подвох
    :::
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # pycourse/
ASSETS = os.path.join(ROOT, "tools", "assets")

PARTS = {
    1: {
        "file": "py1.html",
        "title": "Python собес: язык",
        "cover": "Python собес",
        "level": "Часть 1 · платформенная секция",
        "lead": "Как устроены собеседования в бигтехе и банках, и всё, что спрашивают про сам Python: объекты и коллекции изнутри, "
                "замыкания и декораторы, генераторы, ООП и дескрипторы, память и GIL, потоки и asyncio, типизация и тесты.",
        "description": "Часть 1 курса подготовки к Python-собеседованиям: платформенная секция — язык изнутри, с тренажёрами и автотестами.",
    },
    2: {
        "file": "py2.html",
        "title": "Python собес: алгоритмы",
        "cover": "Лайвкод",
        "level": "Часть 2 · алгоритмическая секция",
        "lead": "Паттерны алгоритмических задач в формате Яндекса и бигтеха: хеши, два указателя, окно, бинарный поиск, "
                "стек, списки, деревья, графы, кучи, перебор и динамика. Каждая задача — с автотестами и разбором.",
        "description": "Часть 2 курса подготовки к Python-собеседованиям: алгоритмическая секция и лайвкодинг по паттернам.",
    },
    3: {
        "file": "py3.html",
        "title": "Python собес: бэкенд",
        "cover": "Бэкенд",
        "level": "Часть 3 · практика, БД, веб, system design",
        "lead": "Практический лайвкод «как в продакшене», бизнес-логика и код-ревью, SQL и устройство баз данных, HTTP и фреймворки, "
                "очереди и кэши, system design и поведенческое интервью.",
        "description": "Часть 3 курса подготовки к Python-собеседованиям: практический лайвкод, SQL, веб-бэкенд, архитектура и system design.",
    },
}

# Ссылки на опубликованные страницы (заполняются после первой публикации).
REMOTE = {
    1: "https://claude.ai/artifact/QMUd6PvLPGnbQJnutDPWvS",
    2: "https://claude.ai/artifact/Q9kqNNUqhgNUCob6uyiyuY",
    3: "https://claude.ai/artifact/SpUd2BLD8FQLgZkmanYafU",
}
LOCAL = {1: "/", 2: "/part2", 3: "/part3"}

KIND_LABEL = {
    "output": "Что выведет?",
    "choice": "Выбери",
    "bug": "Найди баг",
    "open": "Подумай",
    "design": "Спроектируй",
    "review": "Код-ревью",
}

# ---------------------------------------------------------------- подсветка

PY_KW = set("""False None True and as assert async await break class continue def del elif else except
finally for from global if import in is lambda nonlocal not or pass raise return try while with yield
match case type self cls""".split())
SQL_KW = set("""select from where and or not in is null as join left right inner outer full on group by order
having limit offset insert into values update set delete create table index unique primary key references
foreign default begin commit rollback transaction isolation level read committed repeatable serializable
uncommitted distinct count sum avg min max case when then else end exists returning with explain analyze
for share nowait skip locked asc desc integer int text varchar boolean timestamp serial bigserial bigint
check constraint cascade alter add column drop if like between union all over partition row_number using
coalesce lateral true false now interval""".split())

PY_TOKEN = re.compile(r"""(?P<c>#[^\n]*)|(?P<s>(?:\b[rbfRBF]{1,2})?(?:\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\'|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'))|(?P<n>\b\d[\d_]*(?:\.\d+)?(?:e[+-]?\d+)?j?\b)|(?P<d>@[A-Za-z_][\w.]*)|(?P<w>[A-Za-z_]\w*)""")
SQL_TOKEN = re.compile(r"""(?P<c>--[^\n]*)|(?P<s>'(?:''|[^'])*')|(?P<n>\b\d+(?:\.\d+)?\b)|(?P<w>[A-Za-z_]\w*)""")
SH_TOKEN = re.compile(r"""(?P<c>(?:^|(?<=\s))#[^\n]*)|(?P<s>"[^"\n]*"|'[^'\n]*')""", re.M)


def highlight(code, lang):
    lang = (lang or "").lower()
    if lang in ("python", "py", ""):
        rx, kw = PY_TOKEN, PY_KW
    elif lang == "sql":
        rx, kw = SQL_TOKEN, SQL_KW
    elif lang in ("bash", "sh", "shell", "dockerfile", "yaml", "yml"):
        rx, kw = SH_TOKEN, set()
    else:
        return html.escape(code)
    out, pos = [], 0
    for m in rx.finditer(code):
        out.append(html.escape(code[pos:m.start()]))
        t = m.group(0)
        g = m.lastgroup
        if g == "w":
            low = t.lower() if lang == "sql" else t
            out.append(f'<span class="k">{html.escape(t)}</span>' if low in kw else html.escape(t))
        else:
            out.append(f'<span class="{"k" if g == "d" else g}">{html.escape(t)}</span>')
        pos = m.end()
    out.append(html.escape(code[pos:]))
    return "".join(out)


# ---------------------------------------------------------------- инлайн-разметка

def inline(text):
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for p in parts:
        if len(p) > 1 and p.startswith("`") and p.endswith("`"):
            out.append(f"<code>{html.escape(p[1:-1])}</code>")
            continue
        p = html.escape(p, quote=False)
        p = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", p)
        p = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", p)
        p = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', p)
        out.append(p)
    return "".join(out)


# ---------------------------------------------------------------- блоки

def render_blocks(lines):
    """Обычный markdown внутри блока: абзацы, списки, код, таблицы, цитаты."""
    out, i, para = [], 0, []

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            flush()
            lang = s[3:].strip()
            j = i + 1
            code = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                code.append(lines[j])
                j += 1
            out.append(f'<pre><code>{highlight(chr(10).join(code), lang)}</code></pre>')
            i = j + 1
            continue
        if line.startswith("\x00"):
            flush(); out.append(line[1:]); i += 1; continue
        if not s:
            flush(); i += 1; continue
        if s.startswith("- "):
            flush()
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:]); i += 1
                while i < len(lines) and lines[i].startswith("  ") and lines[i].strip() and not lines[i].strip().startswith("- "):
                    items[-1] += " " + lines[i].strip(); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(t)}</li>" for t in items) + "</ul>")
            continue
        if re.match(r"\d+\. ", s):
            flush()
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i].strip()):
                items.append(re.sub(r"^\d+\. ", "", lines[i].strip())); i += 1
                while i < len(lines) and lines[i].startswith("   ") and lines[i].strip():
                    items[-1] += " " + lines[i].strip(); i += 1
            out.append("<ol>" + "".join(f"<li>{inline(t)}</li>" for t in items) + "</ol>")
            continue
        if s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip()); i += 1
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows if not re.match(r"^\|[\s:|-]+\|$", r)]
            head, body = cells[0], cells[1:]
            t = "<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            t += "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody>"
            out.append(f'<div class="tbl"><table>{t}</table></div>')
            continue
        if s.startswith("> "):
            flush()
            q = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q.append(lines[i].strip()[1:].strip()); i += 1
            out.append("<blockquote>" + inline(" ".join(q)) + "</blockquote>")
            continue
        para.append(s)
        i += 1
    flush()
    return "\n".join(out)


def split_sections(lines):
    """Делит тело тренажёра на секции по строкам «--- имя»."""
    sec, cur = {"body": []}, "body"
    for l in lines:
        m = re.match(r"^---\s+(\w+)\s*$", l.strip())
        if m:
            cur = m.group(1); sec[cur] = []; continue
        sec[cur].append(l)
    return sec


QUIZZES = []  # для проверки и карточек повторения


def render_quiz(args, lines, lesson):
    kind, qid = args[0], args[1]
    tags = [a for a in args[2:] if "=" not in a]
    opts = dict(a.split("=", 1) for a in args[2:] if "=" in a)
    sec = split_sections(lines)
    body = sec["body"]
    while body and not body[0].strip():
        body.pop(0)
    title = body[0].strip() if body else ""
    rest = body[1:]
    QUIZZES.append({"id": qid, "kind": kind, "title": title, "lesson": lesson, "tags": tags,
                    "verify": opts.get("verify"), "body": rest, "answer": "\n".join(sec.get("answer", [])).strip()})

    label = KIND_LABEL[kind]
    if "собес" in tags and kind == "open":
        label = "Вопрос с собеса"
    tag = '<span class="tag">· частый вопрос на собесе</span>' if "собес" in tags and kind != "open" else ""
    h = [f'<div class="box quiz" id="{qid}" data-id="{qid}" data-kind="{kind}"'
         + (f' data-answer="{html.escape(sec.get("answer") and chr(10).join(sec["answer"]).strip() or "", quote=True)}"' if kind == "output" else "")
         + ">",
         f'<h3><span class="qkind">{label}</span><span>{inline(title)}{tag}</span></h3>']

    if kind in ("choice", "bug"):
        text = [l for l in rest if not re.match(r"^\s*- \[[ xX]\] ", l)]
        options = [l for l in rest if re.match(r"^\s*- \[[ xX]\] ", l)]
        h.append(render_blocks(text))
        multi = sum(1 for o in options if re.match(r"^\s*- \[[xX]\]", o)) > 1
        itype = "checkbox" if multi else "radio"
        h.append('<div class="qopts" role="group">')
        for n, o in enumerate(options):
            correct = "1" if re.match(r"^\s*- \[[xX]\]", o) else "0"
            t = re.sub(r"^\s*- \[[ xX]\] ", "", o)
            h.append(f'<label data-correct="{correct}"><input type="{itype}" name="{qid}" id="{qid}-o{n}"><span>{inline(t)}</span></label>')
        h.append("</div>")
        if multi:
            h.append('<p class="sm">Здесь несколько правильных вариантов.</p>')
        h.append('<div class="qbar"><button type="button" class="qcheck primary">Проверить</button>'
                 '<button type="button" class="qshow">Показать ответ</button><span class="qres"></span></div>')
        if sec.get("why"):
            h.append('<div class="qans" hidden><b>Почему</b>' + render_blocks(sec["why"]) + "</div>")
    elif kind == "output":
        h.append(render_blocks(rest))
        h.append(f'<textarea id="in-{qid}" rows="3" spellcheck="false" placeholder="Напиши, что напечатает программа, строка в строку. Если упадёт — последней строкой имя исключения" aria-label="Твой ответ"></textarea>')
        h.append('<div class="qbar"><button type="button" class="qcheck primary">Проверить</button>'
                 '<button type="button" class="qshow">Показать ответ</button><span class="qres"></span></div>')
        ans = "\n".join(sec.get("answer", [])).strip()
        h.append('<div class="qans" hidden><b>Вывод</b><pre><code>' + html.escape(ans) + "</code></pre>"
                 + (render_blocks(sec["why"]) if sec.get("why") else "") + "</div>")
    else:  # open / design / review
        h.append(render_blocks(rest))
        h.append(f'<textarea id="in-{qid}" class="prose" rows="5" placeholder="Ответь своими словами, как на собеседовании. Черновик сохраняется" aria-label="Твой ответ"></textarea>')
        h.append('<div class="qbar"><button type="button" class="qcheck primary">Сравнить с эталоном</button>'
                 '<button type="button" class="qshow">Показать ответ</button><span class="qres"></span></div>')
        a = ['<div class="qans" hidden><b>Эталонный ответ</b>', render_blocks(sec.get("answer", []))]
        pts = [l.strip()[2:] for l in sec.get("points", []) if l.strip().startswith("- ")]
        if pts:
            a.append("<b>Отметь, что было в твоём ответе</b><div class=\"qpoints\">")
            for n, p in enumerate(pts):
                a.append(f'<label><input type="checkbox" id="{qid}-p{n}"><span>{inline(p)}</span></label>')
            a.append("</div>")
        a.append('<div class="qbar"><button type="button" class="qcredit primary">Засчитать</button></div></div>')
        h.append("".join(a))
    h.append("</div>")
    return "\n".join(h)


def render_hw(num, lines):
    tasks, cur = [], None
    for l in lines:
        s = l.strip()
        if s.startswith("* "):
            m = re.match(r"^\* (.*?)\s*\{(\w+)\}\s*$", s)
            if not m:
                raise SystemExit(f"hw {num}: не разобрал строку задачи: {s}")
            cur = {"text": m.group(1), "test": m.group(2), "plan": "", "trap": ""}
            tasks.append(cur)
        elif s.startswith("+ ") and cur:
            cur["plan"] += (" " if cur["plan"] else "") + s[2:]
        elif s.startswith("! ") and cur:
            cur["trap"] += (" " if cur["trap"] else "") + s[2:]
    dotted = f"{num[:-1]}.{num[-1]}"
    h = [f'<div class="box hw" data-lesson="{num}"><h3>Домашка {dotted} <span class="count"></span></h3>']
    for n, t in enumerate(tasks, 1):
        tid = f"t{num}-{n}"
        h.append(f'<div class="task" data-test="{t["test"]}"><label><input type="checkbox" id="{tid}"><span>{inline(t["text"])}</span></label>'
                 f'<details><summary>Как решать</summary><p><b>Как решать.</b> {inline(t["plan"])}</p>'
                 + (f'<p><b>Подвох.</b> {inline(t["trap"])}</p>' if t["trap"] else "")
                 + "</details></div>")
    h.append(f'<div class="run"><code>python3 pycourse/check.py {num}</code><button type="button" class="copy">Копировать</button></div></div>')
    return "\n".join(h)


def render_special(kind, args, lines, lesson):
    title = " ".join(args)
    if kind == "quiz":
        return render_quiz(args, lines, lesson)
    if kind == "hw":
        return render_hw(args[0], lines)
    if kind == "src":
        return f'<div class="box src"><h3>{inline(title or "Источники")}</h3>{render_blocks(lines)}</div>'
    if kind == "stat":
        cells = []
        for l in lines:
            if l.strip().startswith("- "):
                big, _, small = l.strip()[2:].partition(" | ")
                cells.append(f"<div><b>{inline(big)}</b><small>{inline(small)}</small></div>")
        return f'<div class="stat">{"".join(cells)}</div>'
    if kind == "checklist":
        return f'<div class="box review-list"><h3>{inline(title or "Чек-лист ревьюера")}</h3>{render_blocks(lines)}</div>'
    cls = {"py": "py", "solve": "solve", "warn": "warn", "project": "project"}[kind]
    head = f"<h3>{inline(title)}</h3>" if title else ""
    return f'<div class="box {cls}">{head}{render_blocks(lines)}</div>'


# ---------------------------------------------------------------- урок → листы

def render_lesson(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    out, module, topic, lesson = [], None, "", ""
    sheet_open = False
    box = None  # (title, lines)
    first_sheet = True

    def close_box():
        nonlocal box
        if box is not None:
            title, bl = box
            out.append(f'<div class="box"><h3>{inline(title)}</h3>{render_blocks(bl)}</div>')
            box = None

    def open_sheet():
        nonlocal sheet_open, first_sheet
        close_box()
        if sheet_open:
            out.append("</div></section>")
        anchor = f' id="l{lesson.replace(".", "")}"' if first_sheet else ""
        first_sheet = False
        out.append(f'<section class="sheet"{anchor}><div class="sheet-cap"></div><div class="sheet-body">')
        out.append(f'<div class="topic">{inline(topic)}</div>')
        sheet_open = True

    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("%% "):
            num, _, name = s[3:].partition("|")
            module = (num.strip(), name.strip())
            out.append(f'<div class="part" id="m{num.strip()}"><b>Модуль {html.escape(num.strip())}</b><h2>{inline(name.strip())}</h2></div>')
            i += 1; continue
        if s.startswith("# "):
            topic = s[2:].strip()
            lesson = topic.split()[0]
            open_sheet(); i += 1; continue
        if s == "@@":
            open_sheet(); i += 1; continue
        if s.startswith("## "):
            close_box()
            box = (s[3:].strip(), [])
            i += 1; continue
        if s.startswith(":::") and len(s) > 3:
            head = s[3:].split()
            kind, args = head[0], head[1:]
            if not (kind == "stat" and box is not None):
                close_box()
            j, inner, fence = i + 1, [], False
            while j < len(lines):
                t = lines[j].strip()
                if t.startswith("```"):
                    fence = not fence
                if t == ":::" and not fence:
                    break
                inner.append(lines[j]); j += 1
            if kind == "stat" and box is not None:
                box[1].append("\x00" + render_special(kind, args, inner, lesson))  # цифры — внутри текущего блока
            else:
                out.append(render_special(kind, args, inner, lesson))
            i = j + 1; continue
        if box is not None:
            box[1].append(line)
        elif s:
            box = ("", [line])
        i += 1
    close_box()
    if sheet_open:
        out.append("</div></section>")
    return "\n".join(out)


def lesson_files(part):
    d = os.path.join(ROOT, "content", f"part{part}")
    files = [f for f in os.listdir(d) if re.match(r"^\d+\.md$", f)]
    return [os.path.join(d, f) for f in sorted(files, key=lambda f: int(f[:-3]))]


def build(part):
    meta = PARTS[part]
    QUIZZES.clear()
    body = [render_lesson(f) for f in lesson_files(part)]

    # оглавление
    toc = []
    for f in lesson_files(part):
        first = open(f, encoding="utf-8").read()
        m = re.search(r"^# (\d+)\.(\d+)", first, re.M)
        if m:
            toc.append(f'<a href="#l{m.group(1)}{m.group(2)}">{m.group(1)}.{m.group(2)}</a>')

    # карточки повторения
    cards = [q for q in QUIZZES if "собес" in q["tags"]]
    if cards:
        c = ['<div class="part" id="review"><b>Повторение</b><h2>Вопросы с собеседований</h2></div>',
             '<section class="sheet"><div class="sheet-cap"></div><div class="sheet-body">',
             '<div class="topic">Перед собеседованием пройдись по всем карточкам</div>',
             '<div class="box"><h3>Как пользоваться:</h3><p>Открой вопрос и ответь вслух, не подглядывая, будто ты на собеседовании. '
             'Зелёная рамка — вопрос уже засчитан в тренажёре.</p><div class="cards">']
        for q in cards:
            c.append(f'<a href="#{q["id"]}" data-id="{q["id"]}"><small>{q["lesson"]} · {KIND_LABEL[q["kind"]] if q["kind"] != "open" else "вопрос"}</small>{inline(q["title"])}</a>')
        c.append("</div></div></div></section>")
        body.append("\n".join(c))
        toc.append('<a href="#review" class="mod">Собес</a>')

    parts_nav = []
    names = {1: "Часть 1 · Язык", 2: "Часть 2 · Алгоритмы", 3: "Часть 3 · Бэкенд"}
    for p in (1, 2, 3):
        cur = ' aria-current="page"' if p == part else ""
        if not lesson_files(p):
            continue
        parts_nav.append(f'<a{cur} data-local="{LOCAL[p]}" data-remote="{REMOTE[p]}"' + (' href="#"' if p == part else "") + f">{names[p]}</a>")

    css = open(os.path.join(ASSETS, "base.css"), encoding="utf-8").read() + open(os.path.join(ASSETS, "course.css"), encoding="utf-8").read()
    js = open(os.path.join(ASSETS, "course.js"), encoding="utf-8").read()
    ed = open(os.path.join(ASSETS, "editor.js"), encoding="utf-8").read()

    page = f"""<title>{meta['title']}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
{css}
</style>

<div class="wrap" data-part="{part}">
<nav class="parts" aria-label="Части курса">{''.join(parts_nav)}</nav>
<header class="cover">
  <div>
    <div class="cover-frame"><div class="cover-inner"><h1>{meta['cover']}</h1></div></div>
    <span class="level">{meta['level']}</span>
    <p>{meta['lead']}</p>
  </div>
</header>
<nav class="toc" aria-label="Уроки">{''.join(toc)}<span class="prog" id="prog"></span></nav>

{chr(10).join(body)}

<footer>Отметки и ответы в тренажёрах хранятся только в этом браузере. Настоящий счёт по коду показывает <code>python3 pycourse/check.py</code>.</footer>
</div>

<script>
{js}
</script>
<script>
{ed}
</script>
"""
    out = os.path.join(ROOT, meta["file"])
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    return out


# ---------------------------------------------------------------- проверка ответов

def norm(s):
    return "\n".join(re.sub(r"\s+", " ", l.strip()) for l in s.replace("\r", "").split("\n")).strip("\n")


def first_code(lines):
    code, inside = [], False
    for l in lines:
        if l.strip().startswith("```"):
            if inside:
                return "\n".join(code)
            inside = True
            continue
        if inside:
            code.append(l)
    return None


def verify(part):
    bad = 0
    checked = 0
    with tempfile.TemporaryDirectory() as tmp:
        for q in QUIZZES:
            if q["kind"] != "output" and not q["verify"]:
                continue
            code = first_code(q["body"])
            if not code:
                print(f"  ? {q['id']}: нет кода — пропущен")
                continue
            f = os.path.join(tmp, q["id"] + ".py")
            with open(f, "w") as fh:
                fh.write(code)
            try:
                r = subprocess.run([sys.executable, "-I", f], cwd=tmp, capture_output=True, text=True, timeout=60)
            except subprocess.TimeoutExpired:
                bad += 1
                print(f"  ✗ {q['id']}: завис")
                continue
            checked += 1
            exp = q["verify"]
            exc = ""
            if r.returncode != 0 and "Traceback" in r.stderr:
                last = [l for l in r.stderr.strip().splitlines() if l.strip()][-1]
                exc = last.split(":", 1)[0].strip().rsplit(".", 1)[-1]
            if exp == "runs":
                ok = r.returncode == 0
            elif exp == "exception":
                got = (r.stdout.rstrip("\n") + "\n" + exc).strip("\n")
                ok = bool(exc) and (q["kind"] != "output" or norm(got) == norm(q["answer"]))
            else:
                ok = r.returncode == 0 and norm(r.stdout) == norm(q["answer"])
            if not ok:
                bad += 1
                print(f"  ✗ {q['id']} ({exp or 'output'}): ожидалось:\n{q['answer']}\n  --- stdout:\n{r.stdout}\n  --- stderr:\n{r.stderr[-600:]}")
    print(f"  часть {part}: проверено {checked}, ошибок {bad}")
    return bad


if __name__ == "__main__":
    want = [int(a) for a in sys.argv[1:] if a.isdigit()] or [p for p in PARTS if lesson_files(p)]
    errors = 0
    for p in want:
        out = build(p)
        n_q = len(QUIZZES)
        print(f"часть {p}: {os.path.relpath(out)} — тренажёров {n_q}")
        if "--verify" in sys.argv:
            errors += verify(p)
    sys.exit(1 if errors else 0)
