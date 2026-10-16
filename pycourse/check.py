#!/usr/bin/env python3
"""Проверяющая система курса: прогоняет тесты и показывает, сколько задач засчитано.

    python3 pycourse/check.py          — все уроки
    python3 pycourse/check.py 31       — только урок 3.1 (с ошибками)
    python3 pycourse/check.py 31 -v    — то же, подробнее
    python3 pycourse/check.py -v       — все уроки с ошибками
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))
import runner  # noqa: E402


def main(argv):
    only = next((a for a in argv if a.isdigit()), None)
    verbose = "-v" in argv or only is not None
    nums = runner.lesson_numbers()
    if only:
        if only not in nums:
            print(f"Нет урока {only}. Есть: {', '.join(nums)}")
            return 2
        nums = [only]
    total_ok = total_all = 0
    for n in nums:
        res = runner.run(n)
        name = runner.title(n)
        if res["build_error"]:
            print(f"💥 {name}: тесты не запустились")
            if verbose:
                print("\n".join("     " + l for l in res["build_error"].splitlines()))
            continue
        ok = sum(t["pass"] for t in res["tests"])
        all_ = len(res["tests"])
        total_ok += ok
        total_all += all_
        print(f"{'✅' if ok == all_ else '❌'} {name}: {ok}/{all_}")
        if verbose:
            for t in res["tests"]:
                if not t["pass"]:
                    print(f"   ✗ {t['name']}")
                    for l in t["output"][:8]:
                        print(f"       {l}")
    if not only:
        print(f"Итого: {total_ok}/{total_all} задач")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
