#!/usr/bin/env python3
"""Lyceum — локальная проверяющая система курса.

Отдаёт конспект и позволяет решать домашки прямо на странице:
код сохраняется в pycourse/lessonXX/tasks.py и проверяется теми же тестами,
что и python3 pycourse/check.py.

    python3 pycourse/lyceum.py
    → http://localhost:4002
"""
import argparse
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))
import runner  # noqa: E402

PAGES = {"/": "py1.html", "/part2": "py2.html", "/part3": "py3.html"}
CHECK_LOCK = threading.Lock()  # одна проверка за раз


class Handler(BaseHTTPRequestHandler):
    server_version = "lyceum"

    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body, ctype="text/plain; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _local(self):
        # Защита от DNS rebinding: чужой сайт не сможет писать файлы через этот сервер.
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        if host not in ("localhost", "127.0.0.1"):
            self._send(403, "только localhost")
            return False
        return True

    def _lesson(self):
        parts = self.path.split("?", 1)[0].strip("/").split("/")
        # api/lessons/{n}/{action}
        if len(parts) != 4 or parts[:2] != ["api", "lessons"] or not runner.LESSON_RE.match(parts[2]) \
                or not os.path.isdir(runner.lesson_dir(parts[2])):
            self._send(404, "нет такого урока")
            return None, None
        return parts[2], parts[3]

    def do_GET(self):
        if not self._local():
            return
        path = self.path.split("?", 1)[0]
        if path in PAGES:
            try:
                with open(os.path.join(runner.ROOT, PAGES[path]), encoding="utf-8") as f:
                    body = f.read()
            except OSError:
                self._send(404, "страница ещё не собрана: python3 pycourse/tools/build.py")
                return
            page = ('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
                    '<meta name="viewport" content="width=device-width, initial-scale=1"></head><body>'
                    + body + "</body></html>")
            self._send(200, page, "text/html; charset=utf-8")
            return
        if path == "/api/ping":
            self._send(200, "ok")
            return
        n, action = self._lesson()
        if n and action == "code":
            with open(runner.editable(n), encoding="utf-8") as f:
                self._send(200, f.read())
        elif n:
            self._send(404, "нет такого действия")

    def do_PUT(self):
        if not self._local():
            return
        n, action = self._lesson()
        if not n:
            return
        if action != "code":
            self._send(404, "нет такого действия")
            return
        size = int(self.headers.get("Content-Length") or 0)
        if size > 256 << 10:
            self._send(413, "слишком большой файл")
            return
        code = self.rfile.read(size).decode("utf-8").replace("\r\n", "\n").replace("\t", "    ")
        if not code.endswith("\n"):
            code += "\n"
        with open(runner.editable(n), "w", encoding="utf-8") as f:
            f.write(code)
        self._send(200, code)

    def do_POST(self):
        if not self._local():
            return
        n, action = self._lesson()
        if not n:
            return
        if action != "check":
            self._send(404, "нет такого действия")
            return
        with CHECK_LOCK:
            res = runner.run(n)
        self._send(200, json.dumps(res, ensure_ascii=False), "application/json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=4002)
    a = ap.parse_args()
    if not os.path.exists(os.path.join(runner.ROOT, "py1.html")):
        print("конспект не собран: python3 pycourse/tools/build.py", file=sys.stderr)
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print(f"конспект с редактором: http://localhost:{a.port}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
