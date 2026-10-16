# Проверяющая система урока 6.1 — не меняй этот файл.
# Запускает твои тесты (student_tests.py) на настоящем cart.py и на мутантах из mutants/.
import ast
import functools
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

MUTANTS = {
    "m1_qty_zero": "line_total принимает qty = 0",
    "m2_negative_price": "line_total принимает отрицательную цену",
    "m3_sale20": "SALE10 даёт скидку 20%",
    "m4_minus500_boundary": "MINUS500 срабатывает только при сумме > 3000 (граница!)",
    "m5_unknown_ignored": "неизвестный промокод молча игнорируется",
    "m10_sale_round_up": "SALE10 округляет скидку вверх",
    "m6_delivery_boundary": "бесплатная доставка только при сумме > 5000 (граница!)",
    "m7_no_notify": "Checkout не отправляет уведомление",
    "m8_delivery_before_promo": "доставка считается от суммы до скидки",
    "m9_notify_before_charge": "уведомление уходит до списания — и при отказе платежа тоже",
}


@functools.lru_cache(maxsize=None)
def run_with(mutant):
    """→ (код возврата pytest, хвост вывода) для student_tests.py на cart.py или мутанте."""
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(os.path.join(HERE, "student_tests.py"), tmp)
        src = os.path.join(HERE, "cart.py") if mutant is None else os.path.join(HERE, "mutants", mutant + ".py")
        shutil.copy(src, os.path.join(tmp, "cart.py"))
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        try:
            p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "-p", "no:asyncio",
                                "--tb=line", "student_tests.py"], cwd=tmp, capture_output=True, text=True, timeout=40, env=env)
        except subprocess.TimeoutExpired:
            return 99, "тесты зависли"
        return p.returncode, "\n".join((p.stdout + p.stderr).strip().splitlines()[-6:])


def _test_count():
    tree = ast.parse(open(os.path.join(HERE, "student_tests.py"), encoding="utf-8").read())
    return sum(1 for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))


def _assert_original_ok():
    code, out = run_with(None)
    assert code == 0, f"твои тесты должны проходить на настоящем cart.py:\n{out}"


def _assert_killed(*names):
    _assert_original_ok()
    alive = [MUTANTS[n] for n in names if run_with(n)[0] != 1]
    assert not alive, "выжили мутанты (твои тесты их не заметили): " + "; ".join(alive)


def test_original():
    _assert_original_ok()
    assert _test_count() >= 6, f"тестов {_test_count()}, нужно хотя бы 6 функций test_…"


def test_kills_line_total():
    _assert_killed("m1_qty_zero", "m2_negative_price")


def test_kills_promo():
    _assert_killed("m3_sale20", "m4_minus500_boundary", "m5_unknown_ignored", "m10_sale_round_up")


def test_kills_delivery():
    _assert_killed("m6_delivery_boundary")


def test_kills_checkout():
    _assert_killed("m7_no_notify", "m8_delivery_before_promo", "m9_notify_before_charge")
