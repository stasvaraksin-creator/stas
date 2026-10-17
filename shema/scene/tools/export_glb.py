#!/usr/bin/env python3
"""Выгрузка сцены цеха в один файл .glb — чтобы крутить и приближать в любом
просмотрщике 3D. Берётся поза на 12-й секунде такта: фура под воротами,
рохля везёт блок.

Страница грузится с подключённым GLTFExporter, стены возвращаются в
непрозрачные, инстансы листов разворачиваются в обычные меши (glTF их не
знает), карточки с подписями выключаются — в файле остаётся геометрия цеха.

    pip install playwright
    # рядом с index.html нужны three.min.js и GLTFExporter.js из three@0.128
    python3 tools/export_glb.py      # -> tsekh-tekspolimer.glb
"""
import asyncio, base64, os, time
from playwright.async_api import async_playwright

URL = os.environ.get('URL', 'http://127.0.0.1:8731/export.html')
OUT = os.environ.get('OUT', 'tsekh-tekspolimer.glb')
POSE = float(os.environ.get('POSE', '12'))
CHROME = os.environ.get('CHROME', '/opt/pw-browsers/chromium-1194/chrome-linux/chrome')

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(executable_path=CHROME, args=[
            '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
            '--no-sandbox', '--disable-gpu'])
        page = await browser.new_page(viewport={'width': 900, 'height': 600})
        await page.goto(URL, wait_until='load')
        await page.wait_for_timeout(3500)
        await page.evaluate("t => window.__step(t, true)", POSE)
        await page.evaluate("() => window.__prep()")
        data = await page.evaluate("() => window.__exportGLB()")
        raw = base64.b64decode(data)
        open(OUT, 'wb').write(raw)
        print(f'{OUT}: {len(raw) / 1e6:.2f} MB')
        await browser.close()

asyncio.run(main())
