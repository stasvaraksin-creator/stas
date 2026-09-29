from playwright.sync_api import sync_playwright
import pathlib, sys
d = pathlib.Path(__file__).parent
ids = ['c1','c2','c3','c4','c5','c6']
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg = b.new_page(viewport={'width':900,'height':1100}, device_scale_factor=2)
    pg.goto((d/'cards.html').as_uri())
    pg.wait_for_timeout(1400)
    for i in ids:
        pg.locator('#'+i).screenshot(path=str(d/f'out_{i}.png'))
    print('shot', len(ids))
    b.close()
