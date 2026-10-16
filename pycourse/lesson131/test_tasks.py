# Проверяющая система урока 13.1 — не меняй этот файл.
import base64
import hashlib
import hmac
import inspect
import json

import pytest

import tasks
from tasks import (IdempotencyConflict, IdempotencyStore, InvalidToken, MethodNotAllowed, NotFound, Router, TokenExpired,
                   jwt_decode, jwt_encode, parse_request)


def test_parse_request():
    raw = (b"POST /api/orders?expand=items&tag=a&tag=b HTTP/1.1\r\n"
           b"Host: shop.example.com:8080\r\nContent-Type: application/json\r\n"
           b"X-Request-ID:  abc  \r\nContent-Length: 13\r\n\r\n{\"qty\": 2}...extra")
    r = parse_request(raw)
    assert r.method == "POST" and r.path == "/api/orders"
    assert r.query == {"expand": ["items"], "tag": ["a", "b"]}
    assert r.headers["host"] == "shop.example.com:8080", "значение может содержать двоеточие"
    assert r.headers["x-request-id"] == "abc" and r.headers["content-type"] == "application/json"
    assert r.body == b'{"qty": 2}...', "тело — ровно Content-Length байт"
    g = parse_request(b"GET / HTTP/1.1\r\nHost: x\r\n\r\n")
    assert g.path == "/" and g.query == {} and g.body == b""
    for bad in (b"GET / HTTP/1.1\r\nHost: x\r\n", b"GARBAGE\r\n\r\n", b""):
        with pytest.raises(ValueError):
            parse_request(bad)


def test_router():
    r = Router()
    r.add("GET", "/users/{id:int}", "get_user")
    r.add("DELETE", "/users/{id:int}", "del_user")
    r.add("GET", "/users/{id:int}/orders/{name}", "user_order")
    r.add("GET", "/health", "health")
    assert r.resolve("GET", "/users/42") == ("get_user", {"id": 42})
    assert r.resolve("GET", "/users/7/orders/abc-1") == ("user_order", {"id": 7, "name": "abc-1"})
    assert r.resolve("GET", "/health") == ("health", {})
    with pytest.raises(MethodNotAllowed) as ei:
        r.resolve("POST", "/users/42")
    assert ei.value.allowed == {"GET", "DELETE"}
    for path in ("/users/abc", "/users/42/extra", "/nope", "/users/"):
        with pytest.raises(NotFound):
            r.resolve("GET", path)


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_idempotency():
    clk = Clock()
    store = IdempotencyStore(ttl=100, clock=clk)
    calls = []

    def create():
        calls.append(1)
        return {"id": len(calls), "status": 201}

    first = store.run("k1", b'{"sum": 10}', create)
    again = store.run("k1", b'{"sum": 10}', create)
    assert first == again == {"id": 1, "status": 201} and len(calls) == 1, "повтор не выполняет операцию"
    with pytest.raises(IdempotencyConflict):
        store.run("k1", b'{"sum": 99}', create)
    assert store.run("k2", b'{"sum": 10}', create)["id"] == 2

    def boom():
        raise RuntimeError("упало")

    with pytest.raises(RuntimeError):
        store.run("k3", b"x", boom)
    assert store.run("k3", b"x", create)["id"] == 3, "неудачный вызов не запоминается"
    clk.t += 101
    assert store.run("k1", b'{"sum": 10}', create)["id"] == 4, "ключ живёт ttl секунд"


def _b64(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def test_jwt():
    secret = b"s3cr3t"
    tok = jwt_encode({"sub": "42", "role": "admin"}, secret)
    parts = tok.split(".")
    assert len(parts) == 3 and "=" not in tok
    head = json.loads(base64.urlsafe_b64decode(parts[0] + "=" * (-len(parts[0]) % 4)))
    assert head == {"alg": "HS256", "typ": "JWT"}
    want_sig = _b64(hmac.new(secret, f"{parts[0]}.{parts[1]}".encode(), hashlib.sha256).digest())
    assert parts[2] == want_sig, "подпись — HMAC-SHA256 от header.payload"
    assert jwt_decode(tok, secret) == {"sub": "42", "role": "admin"}
    with pytest.raises(InvalidToken):
        jwt_decode(tok, b"wrong")
    forged = parts[0] + "." + _b64(json.dumps({"sub": "1", "role": "admin"}).encode()) + "." + parts[2]
    with pytest.raises(InvalidToken):
        jwt_decode(forged, secret)
    none_head = _b64(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    with pytest.raises(InvalidToken):
        jwt_decode(none_head + "." + parts[1] + ".", secret)
    with pytest.raises(InvalidToken):
        jwt_decode("abc", secret)
    exp = jwt_encode({"sub": "1", "exp": 1000}, secret)
    assert jwt_decode(exp, secret, now=999)["sub"] == "1"
    with pytest.raises(TokenExpired):
        jwt_decode(exp, secret, now=1000)
    assert "compare_digest" in inspect.getsource(tasks.jwt_decode), "сравнивай подписи через hmac.compare_digest"
    # совместимость: токен, подписанный «как в PyJWT», тоже должен читаться
    h = _b64(b'{"alg":"HS256","typ":"JWT"}')
    p = _b64(b'{"user":"ann"}')
    s = _b64(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest())
    assert jwt_decode(f"{h}.{p}.{s}", secret) == {"user": "ann"}
