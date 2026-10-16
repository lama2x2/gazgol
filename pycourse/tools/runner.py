"""Прогон тестов урока: общая часть для check.py и lyceum.py.

Каждая задача домашки — тестовая функция test_<имя> (и, если нужно, test_<имя>__<что-то>). Параметризованные
случаи (test_x[a], test_x[b]) сворачиваются в одну задачу: она засчитана,
только если прошли все случаи.
"""
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # pycourse/
LESSON_RE = re.compile(r"^(1[0-4]|[1-9])[1-9]$")
TIMEOUT = 60
TODO = "ещё не решено: в коде остался raise NotImplementedError"


def lesson_numbers():
    nums = [d[6:] for d in os.listdir(ROOT) if d.startswith("lesson") and LESSON_RE.match(d[6:])]
    return sorted(nums, key=int)


def lesson_dir(num):
    return os.path.join(ROOT, "lesson" + num)


def dotted(num):
    return f"{num[:-1]}.{num[-1]}"


def title(num):
    """Первая строка файла ученика: «# Урок 3.1. Замыкания и декораторы»."""
    try:
        with open(editable(num), encoding="utf-8") as f:
            first = f.readline().strip()
    except OSError:
        return dotted(num)
    return re.sub(r"^#\s*Урок\s*", "", first).rstrip(".") or dotted(num)


def editable(num):
    """Файл, который правит ученик: student_tests.py в уроках, где тесты пишешь ты, иначе tasks.py."""
    d = lesson_dir(num)
    student = os.path.join(d, "student_tests.py")
    return student if os.path.exists(student) else os.path.join(d, "tasks.py")


def _fail_lines(node):
    msg = node.get("message", "")
    text = node.text or ""
    lines = [l[1:].strip() for l in text.splitlines() if l.startswith("E ")]
    if any(l.startswith("AssertionError: ") for l in lines):
        # своё сообщение в assert уже всё объясняет — убираем интроспекцию pytest
        lines = [l for l in lines if not l.startswith(("assert ", "+", "where "))]
    if not lines and msg:
        lines = [msg]
    return lines[:14]


def run(num):
    """→ {"build_error": str | None, "tests": [{"name", "pass", "output"}]}"""
    d = lesson_dir(num)
    with tempfile.TemporaryDirectory() as tmp:
        xml = os.path.join(tmp, "r.xml")
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "no:asyncio", "--tb=short",
               f"--junitxml={xml}", "-o", "junit_family=xunit2"]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        try:
            p = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=TIMEOUT, env=env)
        except subprocess.TimeoutExpired:
            return {"build_error": f"Проверка не уложилась в {TIMEOUT} секунд — возможно, в коде бесконечный цикл "
                                   "или потоки/корутины ждут друг друга.", "tests": []}
        out = (p.stdout + p.stderr).strip()
        if "No module named pytest" in out:
            return {"build_error": "Не установлен pytest: python3 -m pip install pytest", "tests": []}
        if not os.path.exists(xml):
            return {"build_error": out[-3000:] or "pytest не запустился", "tests": []}
        tree = ET.parse(xml)

    tests, by = [], {}
    collect_err = []
    for tc in tree.iter("testcase"):
        name = tc.get("name", "")
        bad = [c for c in tc if c.tag in ("failure", "error")]
        if any("collection failure" in (c.get("message") or "") or "ERROR collecting" in (c.text or "") for c in bad) \
                or not name.startswith("test_"):
            collect_err += [(c.text or c.get("message") or "").strip() for c in bad]
            continue
        base = name.split("[", 1)[0].split("__", 1)[0]  # test_x__random — тоже задача test_x
        if base not in by:
            by[base] = {"name": base, "pass": True, "output": []}
            tests.append(by[base])
        skipped = any(c.tag == "skipped" for c in tc)
        if bad or skipped:
            r = by[base]
            r["pass"] = False
            case = name[len(base):]
            for c in bad:
                lines = _fail_lines(c)
                if any(l.startswith("NotImplementedError") for l in lines):
                    if TODO not in r["output"]:
                        r["output"].append(TODO)
                    continue
                if case and lines:
                    lines = [f"случай {case}:"] + lines
                if len(r["output"]) < 30:
                    r["output"] += lines
    if collect_err and not tests:
        # из трейсбека оставляем только строки про код урока — там SyntaxError / ImportError
        keep = []
        for l in "\n".join(collect_err).splitlines():
            t = l.strip()
            if "site-packages" in t or "/lib/python3" in t or "<frozen" in t or t == "???" or t.startswith(("mod = ", "importlib.", "return _bootstrap", "exec(co")):
                continue
            keep.append(l[2:] if l.startswith("E ") else l)
        return {"build_error": "\n".join(keep[-25:]), "tests": []}
    if not tests:
        return {"build_error": out[-3000:] or "тесты не найдены", "tests": []}
    return {"build_error": None, "tests": tests}
