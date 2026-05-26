"""Проверка адаптивной вёрстки лендинга на ключевых брейкпоинтах.

Снимает full-page скриншоты и проверяет отсутствие горизонтального скролла
(переполнения по ширине) на 320/375/768/1024/1440 px.

Запуск:
    python tests/check_layout.py
Скриншоты появятся в tests/shots/.
"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
INDEX = (ROOT / "index.html").as_uri()
SHOTS = ROOT / "tests" / "shots"
SHOTS.mkdir(parents=True, exist_ok=True)

BREAKPOINTS = [320, 375, 768, 1024, 1440]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        results = []
        for w in BREAKPOINTS:
            page = browser.new_page(viewport={"width": w, "height": 900})
            page.goto(INDEX)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(400)
            scroll_w = page.evaluate("document.documentElement.scrollWidth")
            client_w = page.evaluate("document.documentElement.clientWidth")
            overflow = scroll_w - client_w
            page.screenshot(path=str(SHOTS / f"bp_{w}.png"), full_page=True)
            results.append((w, scroll_w, client_w, overflow))
            page.close()
        browser.close()

    print(f"{'width':>6} {'scrollW':>9} {'clientW':>9} {'overflow':>9}  status")
    ok = True
    for w, sw, cw, ov in results:
        status = "OK" if ov <= 1 else "OVERFLOW!"
        if ov > 1:
            ok = False
        print(f"{w:>6} {sw:>9} {cw:>9} {ov:>9}  {status}")
    print("\nИтог:", "горизонтального скролла нет" if ok else "ЕСТЬ переполнение — смотри скриншоты")


if __name__ == "__main__":
    main()
