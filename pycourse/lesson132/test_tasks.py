# Проверяющая система урока 13.2 — не меняй этот файл.
import asyncio
import io
import json
from wsgiref.util import setup_testing_defaults

import pytest

from tasks import Depends, app, asgi_app, solve, timing_middleware


def call(application, method="GET", path="/", query="", body=b"", headers=None):
    env = {}
    setup_testing_defaults(env)
    env.update({"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query,
                "CONTENT_LENGTH": str(len(body)), "wsgi.input": io.BytesIO(body)})
    for k, v in (headers or {}).items():
        env["HTTP_" + k.upper().replace("-", "_")] = v
    got = {}

    def start_response(status, hdrs, exc_info=None):
        got["status"], got["headers"] = status, dict(hdrs)
    chunks = application(env, start_response)
    data = b"".join(chunks)
    return got["status"], got["headers"], data, env


def test_wsgi_app():
    st, h, b, _ = call(app, "GET", "/health")
    assert st.startswith("200") and json.loads(b) == {"status": "ok"}
    assert h["Content-Type"] == "application/json" and h["Content-Length"] == str(len(b))
    assert json.loads(call(app, "GET", "/hello", "name=Ann")[2]) == {"hello": "Ann"}
    assert json.loads(call(app, "GET", "/hello")[2]) == {"hello": "world"}
    st, _, b, _ = call(app, "POST", "/echo", body=b'{"a": [1, 2]}')
    assert st.startswith("200") and json.loads(b) == {"a": [1, 2]}
    st, _, b, _ = call(app, "POST", "/echo", body=b"{oops")
    assert st.startswith("400") and json.loads(b) == {"error": "bad json"}
    st, h, b, _ = call(app, "DELETE", "/health")
    assert st.startswith("405") and "GET" in h.get("Allow", ""), "405 с заголовком Allow"
    st, _, b, _ = call(app, "GET", "/nope")
    assert st.startswith("404") and json.loads(b) == {"error": "not found"}


def test_timing_middleware():
    ticks = iter([10.0, 10.25])
    seen = {}

    def inner(environ, start_response):
        seen["rid"] = environ.get("request_id")
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"ok"]

    wrapped = timing_middleware(inner, clock=lambda: next(ticks))
    st, h, b, _ = call(wrapped, headers={"X-Request-ID": "abc123"})
    assert b == b"ok" and st.startswith("200")
    assert h["X-Request-ID"] == "abc123" and seen["rid"] == "abc123"
    assert h["X-Response-Time-ms"] == "250" and h["Content-Type"] == "text/plain"
    st, h, b, _ = call(timing_middleware(inner))
    assert len(h["X-Request-ID"]) == 32 and seen["rid"] == h["X-Request-ID"], "новый id, если не пришёл"
    assert int(h["X-Response-Time-ms"]) >= 0


def test_depends():
    log = []

    def get_settings():
        log.append("settings")
        return {"dsn": "sqlite://"}

    def get_db(settings=Depends(get_settings)):
        log.append("db open")
        yield f"db({settings['dsn']})"
        log.append("db close")

    def get_repo(db=Depends(get_db), settings=Depends(get_settings)):
        log.append("repo")
        return f"repo[{db}]"

    def handler(repo=Depends(get_repo), db=Depends(get_db)):
        log.append("handler")
        return repo, db

    assert solve(handler) == ("repo[db(sqlite://)]", "db(sqlite://)")
    assert log == ["settings", "db open", "repo", "handler", "db close"], f"каждая зависимость — один раз: {log}"

    log.clear()

    def failing(db=Depends(get_db)):
        raise RuntimeError("упало")

    with pytest.raises(RuntimeError):
        solve(failing)
    assert log == ["settings", "db open", "db close"], "генератор закрывается и при исключении"

    log.clear()
    assert solve(handler, overrides={get_db: lambda: "fake-db"}) == ("repo[fake-db]", "fake-db")
    assert "db open" not in log

    def a():
        yield "A"
        log.append("close A")

    def b(x=Depends(a)):
        yield x + "B"
        log.append("close B")

    def h2(y=Depends(b)):
        return y

    log.clear()
    assert solve(h2) == "AB" and log == ["close B", "close A"], "закрывать в обратном порядке"


def run_asgi(scope, messages):
    sent = []
    queue = list(messages)

    async def receive():
        return queue.pop(0) if queue else {"type": "http.disconnect"}

    async def send(msg):
        sent.append(msg)

    asyncio.run(asyncio.wait_for(asgi_app(scope, receive, send), 5))
    return sent


def http(method, path):
    return {"type": "http", "method": method, "path": path, "headers": [], "query_string": b""}


def test_asgi_app():
    sent = run_asgi(http("GET", "/health"), [{"type": "http.request", "body": b"", "more_body": False}])
    assert sent[0]["type"] == "http.response.start" and sent[0]["status"] == 200
    assert (b"content-type", b"application/json") in [tuple(h) for h in sent[0]["headers"]]
    assert json.loads(sent[1]["body"]) == {"status": "ok"}
    chunks = [{"type": "http.request", "body": b'{"a": ', "more_body": True},
              {"type": "http.request", "body": b'1}', "more_body": False}]
    sent = run_asgi(http("POST", "/echo"), chunks)
    assert sent[0]["status"] == 200 and json.loads(sent[1]["body"]) == {"a": 1}, "тело собирается из кусков"
    assert run_asgi(http("GET", "/x"), [{"type": "http.request", "body": b""}])[0]["status"] == 404
    life = run_asgi({"type": "lifespan"}, [{"type": "lifespan.startup"}, {"type": "lifespan.shutdown"}])
    assert [m["type"] for m in life] == ["lifespan.startup.complete", "lifespan.shutdown.complete"]
