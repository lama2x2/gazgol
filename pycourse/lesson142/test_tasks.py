# Проверяющая система урока 14.2 — не меняй этот файл.
import random
import threading

import pytest

from tasks import ClockMovedBackwards, Snowflake, UrlShortener, base62_decode, base62_encode

rnd = random.Random(142)


def test_base62():
    assert base62_encode(0) == "0" and base62_encode(61) == "Z" and base62_encode(62) == "10"
    assert base62_encode(3843) == "ZZ" and base62_decode("ZZ") == 3843
    for _ in range(2000):
        n = rnd.randrange(2**64)
        assert base62_decode(base62_encode(n)) == n
    for bad in ("", "a-b", "абв", "a b"):
        with pytest.raises(ValueError):
            base62_decode(bad)
    with pytest.raises(ValueError):
        base62_encode(-1)


class Clock:
    def __init__(self, t):
        self.t = t
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self.t


def test_snowflake():
    clk = Clock(Snowflake.EPOCH_MS + 5000)
    sf = Snowflake(node=3, clock=clk)
    a, b = sf.next_id(), sf.next_id()
    assert a >> 22 == 5000 and (a >> 12) & 1023 == 3 and a & 4095 == 0
    assert b == a + 1, "в той же миллисекунде растёт счётчик"
    clk.t += 1
    c = sf.next_id()
    assert c >> 22 == 5001 and c & 4095 == 0, "новая миллисекунда — счётчик с нуля"
    clk.t -= 2
    with pytest.raises(ClockMovedBackwards):
        sf.next_id()
    with pytest.raises(ValueError):
        Snowflake(node=1024)

    class Ticking:
        def __init__(self):
            self.t = Snowflake.EPOCH_MS
            self.n = 0

        def __call__(self):
            self.n += 1
            if self.n % 5000 == 0:
                self.t += 1
            return self.t

    sf2 = Snowflake(node=1, clock=Ticking())
    ids = [sf2.next_id() for _ in range(10_000)]
    assert len(set(ids)) == 10_000 and ids == sorted(ids), "больше 4096 в миллисекунду — ждать следующую"
    assert all(i & 4095 < 4096 for i in ids)

    real = Snowflake(node=7)
    out, lock = [], threading.Lock()

    def work():
        got = [real.next_id() for _ in range(2000)]
        with lock:
            out.extend(got)
    ts = [threading.Thread(target=work) for _ in range(8)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert len(set(out)) == 16_000, "id из разных потоков должны быть уникальны — нужна блокировка"


class T:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_url_shortener():
    clk = T()
    s = UrlShortener(clock=clk)
    c1 = s.shorten("https://example.com/promo?utm=sms")
    c2 = s.shorten("https://example.com/promo?utm=sms")
    assert c1 != c2 and len(c1) <= 7
    assert s.resolve(c1) == "https://example.com/promo?utm=sms" and s.resolve(c1) and s.stats(c1) == 2
    assert s.stats(c2) == 0
    assert s.shorten("http://a.ru/x", alias="sale2026") == "sale2026"
    with pytest.raises(ValueError):
        s.shorten("http://a.ru/y", alias="sale2026")
    for bad_alias in ("ab", "x" * 33, "with-dash", "пробел"):
        with pytest.raises(ValueError):
            s.shorten("http://a.ru", alias=bad_alias)
    for bad_url in ("ftp://a.ru/f", "javascript:alert(1)", "example.com", "https://"):
        with pytest.raises(ValueError):
            s.shorten(bad_url)
    with pytest.raises(KeyError):
        s.resolve("nope")
    t = s.shorten("https://b.ru", ttl=10)
    clk.t = 9.9
    assert s.resolve(t) == "https://b.ru"
    clk.t = 10.0
    with pytest.raises(KeyError):
        s.resolve(t)
    promo = s.shorten("https://c.ru", alias="promo10", ttl=5)
    clk.t = 15.0
    assert s.shorten("https://d.ru", alias=promo) == "promo10", "истёкший код можно занять снова"
    assert s.resolve("promo10") == "https://d.ru"

    first = UrlShortener(clock=clk)
    first.shorten("https://z.ru", alias="100")          # = base62(3844): генератор дойдёт до него
    gen = [first.shorten(f"https://z.ru/{i}") for i in range(5000)]
    assert "100" not in gen and len(set(gen)) == 5000, "сгенерированный код не должен совпасть с чужим алиасом"
    assert first.resolve("100") == "https://z.ru"
