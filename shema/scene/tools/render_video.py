#!/usr/bin/env python3
"""Покадровый рендер сцены цеха в PNG-кадры (дальше их склеивает ffmpeg).

Страница рисует кадр по команде: window.__step(t, true) — точное время такта,
без сглаживания камеры, поэтому кадры ложатся ровно в тайминг.

    pip install playwright
    cd shema/scene && python3 -m http.server 8731 &
    python3 tools/render_video.py            # -> frames/f00000.png ...
    ffmpeg -framerate 25 -i frames/f%05d.png -c:v libx264 -pix_fmt yuv420p \
           -crf 20 -movflags +faststart tsekh.mp4

Переменные окружения: URL, OUT, FPS, DUR, W, H, CHROME.
"""
import asyncio, os, time
from playwright.async_api import async_playwright

URL = os.environ.get('URL', 'http://127.0.0.1:8731/index.html')
OUT = os.environ.get('OUT', 'frames')
FPS = float(os.environ.get('FPS', '25'))
DUR = float(os.environ.get('DUR', '48'))
W, H = int(os.environ.get('W', '1280')), int(os.environ.get('H', '720'))
CHROME = os.environ.get('CHROME', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
        '--no-sandbox', '--disable-gpu', '--hide-scrollbars']

async def main():
    os.makedirs(OUT, exist_ok=True)
    n = int(FPS * DUR)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(executable_path=CHROME, args=ARGS)
        page = await browser.new_page(viewport={'width': W, 'height': H})
        await page.goto(URL, wait_until='load')
        await page.evaluate("() => { window.__paused = true; }")
        await page.wait_for_timeout(3000)              # текстуры и шрифты
        start = time.time()
        for i in range(n):
            await page.evaluate("t => window.__step(t, true)", (i / FPS) % DUR)
            await page.screenshot(path=f'{OUT}/f{i:05d}.png')
            if i % 50 == 0:
                print(f'{i}/{n}  {time.time() - start:.0f}s', flush=True)
        print(f'готово: {n} кадров за {time.time() - start:.0f}s')
        await browser.close()

asyncio.run(main())
