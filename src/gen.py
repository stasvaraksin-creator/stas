import os, re

# ── шрифты ───────────────────────────────────────────────────────────────────
LAT = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212"
CYR = "U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116"
def faces():
    out = []
    for fam, alias, weights in [("Montserrat", "M", [700, 800, 900]),
                                ("GolosText", "G", [400, 500, 600, 700, 800, 900])]:
        for w in weights:
            for sub, rng in (("latin", LAT), ("cyrillic", CYR)):
                out.append(
                    "@font-face{font-family:%s;src:url(fonts/%s-%d-%s.woff2)format('woff2');"
                    "font-weight:%d;font-style:normal;font-display:block;unicode-range:%s}"
                    % (alias, fam, w, sub, w, rng))
    return "\n".join(out)

HEX = ("url(\"data:image/svg+xml,%3Csvg width='28' height='49' viewBox='0 0 28 49' "
       "xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.5' fill-rule='evenodd'%3E"
       "%3Cpath d='M13.99 9.25l13 7.5v15l-13 7.5L1 31.75v-15l12.99-7.5zM3 17.9v12.7l10.99 6.34 11-6.35V17.9l-11-6.34L3 17.9z"
       "M0 15l12.98-7.5V0h-2v6.35L0 12.69v2.3zm0 18.5L12.98 41v8h-2v-6.85L0 35.81V33.5zM15 0v7.5L27.99 15H28v-2.31h-.01L17 6.35V0h-2z"
       "m0 49v-8l12.99-7.5H28v2.31h-.01L17 42.15V49h-2z'/%3E%3C/g%3E%3C/svg%3E\")")

# ── иконки (24×24, обводка currentColor) ─────────────────────────────────────
ICONS = {
 "drop":   '<path d="M12 3.2c0 0 6.2 6.6 6.2 10.3A6.2 6.2 0 0 1 12 19.7a6.2 6.2 0 0 1-6.2-6.2C5.8 9.8 12 3.2 12 3.2z"/>',
 "zip":    '<path d="M9.2 3v6.6M14.8 3v6.6M9.2 4.6H6.9M9.2 7.1H6.9M14.8 4.6h2.3M14.8 7.1h2.3"/>'
           '<rect x="8.4" y="9.6" width="7.2" height="5.2" rx="1.8"/><path d="M12 14.8v3.4"/>'
           '<circle cx="12" cy="19.7" r="1.5"/>',
 "cross":  '<rect x="3.2" y="3.2" width="17.6" height="17.6" rx="5"/><path d="M12 7.6v8.8M7.6 12h8.8"/>',
 "home":   '<path d="M4 11.2l8-6.4 8 6.4v7.6a1.2 1.2 0 0 1-1.2 1.2H5.2A1.2 1.2 0 0 1 4 18.8z"/>'
           '<path d="M9.6 20.4v-5.6h4.8v5.6"/>',
 "shield": '<path d="M12 3.2l7.2 2.9v5.3c0 4.9-3 7.9-7.2 9.6-4.2-1.7-7.2-4.7-7.2-9.6V6.1z"/>'
           '<path d="M8.9 12.2l2.2 2.2 4-4.2"/>',
 "vapor":  '<path d="M7.6 21c0-3.6-2-3.6-2-6.4s2-2.8 2-5.6M12 21c0-3.6-2-3.6-2-6.4s2-2.8 2-5.6M16.4 21c0-3.6-2-3.6-2-6.4s2-2.8 2-5.6"/>'
           '<path d="M4 5.2h16"/>',
 "leaf":   '<path d="M5 19.4c0-8.4 6.2-13.6 14.4-13.6 0 8.4-5.2 13.6-14.4 13.6z"/><path d="M5 19.4c3.2-4.4 6.4-6.6 9.6-7.8"/>',
 "clock":  '<circle cx="12" cy="12" r="8.4"/><path d="M12 6.8V12l3.4 2.2"/>',
 "bolt":   '<path d="M13.2 3l-7 9.4h5.2L10.2 21l7-9.4h-5z"/>',
 "spray":  '<rect x="7.6" y="9.4" width="7.6" height="11.4" rx="2"/><path d="M9.6 9.4V6.6h3.6v2.8"/>'
           '<path d="M16.6 5.2h2.6M16.6 8.4h2.6M16.6 11.6h2.6"/>',
 "steam":  '<path d="M5.4 14.6c2.2-2.2 4.4 2.2 6.6 0s4.4-2.2 6.6 0M5.4 19c2.2-2.2 4.4 2.2 6.6 0s4.4-2.2 6.6 0"/>'
           '<path d="M9.2 9.6V6.2M12 9.6V4.8M14.8 9.6V6.2"/>',
 "auto":   '<rect x="3.2" y="6.6" width="17.6" height="11.6" rx="2.4"/><path d="M7 11.2h5.6M7 14.4h3.2"/>'
           '<circle cx="17" cy="12.6" r="1.6"/>',
 "iron":   '<path d="M3.6 16.4h16.8l-2-6.2a4.2 4.2 0 0 0-4-3H8.8"/><path d="M3.6 16.4v3.2h16.8v-3.2"/>',
 "check":  '<path d="M4.4 12.4l5 5L19.6 6.6"/>',
 "ruler":  '<rect x="2.6" y="8" width="18.8" height="8" rx="1.8"/>'
           '<path d="M7 8v3.2M11 8v4.4M15 8v3.2M19 8v4.4"/>',
}
def ic(name, cls="ic", extra=""):
    return ('<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" '
            'stroke-linecap="round" stroke-linejoin="round"%s>%s</svg>' % (cls, extra, ICONS[name]))
def ic_no(name, cls="ic"):
    """иконка с перечёркиванием"""
    return ('<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" '
            'stroke-linecap="round" stroke-linejoin="round">%s'
            '<path d="M4.2 19.8L19.8 4.2" stroke-width="2.4"/></svg>' % (cls, ICONS[name]))

# ── геометрия товара (координаты внутри product_sh.png с полями под тень) ──
import json as _json
_G = _json.load(open(os.path.join(os.path.dirname(__file__), "geom.json")))
PADL, PADT = _G["PAD"][0], _G["PAD"][1]
PW, PH = _G["W"] // _G["S"], _G["H"] // _G["S"]          # полный холст с полями
BODYW = 675                                              # ширина самого изделия
SCALE = PW / BODYW                                       # во сколько шире холст
L = (_G["L"][0] + PADL, _G["L"][1] + PADT)
B = (_G["B"][0] + PADL, _G["B"][1] + PADT)
R = (_G["R"][0] + PADL, _G["R"][1] + PADT)
U = tuple(_G["U"]); V = tuple(_G["V"])
FACE = "matrix(%d,%d,%d,%d,%d,%d)" % (U[0], U[1], V[0], V[1], L[0], L[1])
THICK = 21

def prod_svg(inner, padx=0.12, padtop=0.55, padbot=0.30):
    """SVG поверх фото в координатах вырезки"""
    vb = (-padx * PW, -padtop * PH, PW * (1 + 2 * padx), PH * (1 + padtop + padbot))
    style = ("left:%.2f%%;top:%.2f%%;width:%.2f%%;height:%.2f%%"
             % (-padx * 100, -padtop * 100, (1 + 2 * padx) * 100, (1 + padtop + padbot) * 100))
    return ('<svg class="pov" style="%s" viewBox="%.1f %.1f %.1f %.1f">%s</svg>'
            % (style, vb[0], vb[1], vb[2], vb[3], inner))

def product(cls="", inner="", w=660, src="product_sh.png", extra=""):
    """w — ширина самого изделия; холст с полями под тень шире в SCALE раз."""
    full = round(w * SCALE)
    return ('<div class="prod %s" style="width:%dpx%s"><img src="%s" alt="">%s</div>'
            % (cls, full, extra, src, inner))

# ── размерные стрелки (карточка 6) ───────────────────────────────────────────
def dims():
    def off(p, d, k):  return (p[0] + d[0] * k, p[1] + d[1] * k)
    n_long = (-U[1], U[0]); m = (n_long[0] ** 2 + n_long[1] ** 2) ** .5
    n_long = (n_long[0] / m, n_long[1] / m)
    n_short = (V[1], -V[0]); m = (n_short[0] ** 2 + n_short[1] ** 2) ** .5
    n_short = (n_short[0] / m, n_short[1] / m)
    a1, b1 = off(L, n_long, -32), off(B, n_long, -32)
    a2, b2 = off(B, n_short, 34), off(R, n_short, 34)
    a3, b3 = (L[0] - 26, L[1] + 1), (L[0] - 26, L[1] + THICK)
    def line(a, b, w=3.2):
        return ('<path d="M%.1f %.1f L%.1f %.1f" stroke="#fff" stroke-width="%.1f" '
                'stroke-dasharray="11 9" stroke-linecap="round" fill="none" '
                'marker-start="url(#ah)" marker-end="url(#ah)"/>' % (a[0], a[1], b[0], b[1], w))
    def lab(p, t, dx=0, dy=0, fs=27, rot=None):
        tr = ' transform="rotate(%d %.1f %.1f)"' % (rot, p[0] + dx, p[1] + dy) if rot else ''
        return ('<text x="%.1f" y="%.1f" fill="#fff" font-family="G" font-weight="800" '
                'font-size="%d" text-anchor="middle" dominant-baseline="central"%s>%s</text>'
                % (p[0] + dx, p[1] + dy, fs, tr, t))
    mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    inner = (
      '<defs><marker id="ah" viewBox="0 0 10 10" refX="8.6" refY="5" markerWidth="5.2" '
      'markerHeight="5.2" orient="auto-start-reverse">'
      '<path d="M0 1.2 L9.4 5 L0 8.8 Z" fill="#fff"/></marker></defs>'
      + line(a1, b1) + line(a2, b2) + line(a3, b3, 2.8)
      + lab(mid(a1, b1), "200 см", 0, -25)
      + lab(mid(a2, b2), "90 см", 8, -24)
      + lab(mid(a3, b3), "10 см", -20, 0, 24, rot=-90))
    return prod_svg(inner, padx=0.03, padtop=0.06, padbot=0.02)

# ── шапка карточки ───────────────────────────────────────────────────────────
def head(big, small=None, size=88, ssize=40, center=False, top=52):
    s = '<span class="hs" style="font-size:%dpx">%s</span>' % (ssize, small) if small else ''
    return ('<div class="head%s" style="top:%dpx"><span class="hb" style="font-size:%dpx">%s</span>%s</div>'
            % (" ctr" if center else "", top, size, big, s))

def bubble(icon, html, style, w=None, tail="left"):
    i = '<span class="bic">%s</span>' % ic(icon) if icon else ''
    ws = ";width:%dpx" % w if w else ''
    return '<div class="bub t-%s" style="%s%s">%s<span>%s</span></div>' % (tail, style, ws, i, html)

def chip(icon, text, no=False):
    g = ic_no(icon) if no else ic(icon)
    return '<div class="chip"><span class="cic">%s</span><b>%s</b></div>' % (g, text)

# ── карточки ─────────────────────────────────────────────────────────────────
C1 = f'''
<div class="card" id="c1">
  <div class="hex tr"></div><div class="hex bl"></div><div class="halo"></div>
  <div class="brand">
    <img class="logo" src="logo_texpolimer.png" alt="ТЕКСПОЛИМЕР">
    <span class="ru"><img src="made_in_russia.png" alt="Сделано в России"></span>
  </div>
  <div class="head" style="top:150px">
    <span class="hs" style="font-size:36px;margin-bottom:6px">200 × 90 × 10 см</span>
    <span class="hb" style="font-size:78px">НАМАТРАСНИК</span>
  </div>
  <div class="grid2" style="top:322px">
    {chip("drop","непромокаемый")}{chip("zip","на молнии")}
    {chip("cross","для медицинского матраса")}{chip("home","для домашнего использования")}
  </div>
  {product("p1", "", 700)}
  <div class="specs">
    <div class="spec"><em>ECO</em><b>Клеёнка ПВХ</b><s>материал</s></div>
    <div class="spec teal"><b>265 г/м²</b><s>плотность</s></div>
  </div>
</div>'''

C2 = f'''
<div class="card" id="c2">
  <div class="hex bl"></div><div class="halo"></div>
  {head("НЕПРОМОКАЕМЫЙ","наматрасник",66,38)}
  {bubble("home","Подходит для <b>медицинских учреждений</b> и для домашнего использования","left:52px;top:268px",w=412)}
  {product("p2", "", 764, src="product_wet.png")}
  <div class="corner">
    <span class="cic big">{ic("shield")}</span>
    <b>БЕЗОПАСЕН<s>для детей и взрослых</s></b>
  </div>
</div>'''

C3 = f'''
<div class="card" id="c3">
  <div class="photo"><img src="zip_wide.jpg" alt=""><div class="fade"></div></div>
  <div class="head" style="top:44px">
    <span class="hb" style="font-size:74px">ТКАНЬ</span>
    <span class="hs" style="font-size:44px">«Клеёнка ПВХ»</span>
  </div>
  {bubble(None,"Ткань обеспечивает <b>гигиеничное</b> и <b>противомикробное</b> состояние, позволяет легко удалять любые загрязнения","left:52px;top:300px",w=430)}
  <div class="panel">
    <div class="prow">{ic("check","chk")}<span><b>Водонепроницаемый</b> 100 %</span></div>
    <div class="prow">{ic("check","chk")}<span>Паропроницаемый</span></div>
    <div class="prow">{ic("check","chk")}<span>Гипоаллергенный материал</span></div>
    <div class="prow">{ic("check","chk")}<span>Долгий срок службы</span></div>
    <div class="prow">{ic("check","chk")}<span>Не накапливает электростатический заряд</span></div>
    <div class="prow">{ic("check","chk")}<span>Стойкий к санитарно-гигиенической обработке</span></div>
  </div>
</div>'''

C4 = f'''
<div class="card" id="c4">
  <div class="hex bl"></div><div class="halo"></div>
  {head("УДОБСТВО","использования",84,42)}
  <div class="lbl" style="left:52px;top:236px"><span class="cic">{ic("zip")}</span>МОЛНИЯ</div>
  <div class="zoom" style="right:44px;top:214px;width:286px;height:286px">
    <img src="zip_slider.jpg" alt="">
  </div>
  {bubble(None,"Чехол на молнии <b>легко надевается</b> на матрас и снимается для обработки, закрывая его со всех сторон","left:52px;top:372px",w=384)}
  {product("p4","", 700)}
</div>'''

C5 = f'''
<div class="card" id="c5">
  <div class="hex tr"></div><div class="hex bl"></div><div class="halo"></div>
  {head("МАТЕРИАЛ СТОЙКИЙ", None, 62, 0, center=True, top=52)}
  <div class="deck">к санитарно-гигиенической обработке,<br>в том числе альдегид- и хлорсодержащими средствами</div>
  <div class="notlbl">НЕ ПОДЛЕЖИТ:</div>
  <div class="list">
    {chip("auto","Автоклавированию",no=True)}
    {chip("steam","Обработке паром",no=True)}
    {chip("iron","Глажке",no=True)}
  </div>
  {product("p5","", 690)}
</div>'''

C6 = f'''
<div class="card" id="c6">
  <div class="hex bl"></div><div class="halo"></div>
  {head("РАЗМЕР","200 × 90 × 10 см",84,46)}
  {bubble("ruler","На матрас <b>200 × 90 см</b> высотой <b>10 см</b> — для медицинской кровати и для дома","left:52px;top:300px",w=430)}
  {product("p6", dims(), 640)}
</div>'''

CSS = '''
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#F0F0F0}
body{display:flex;flex-direction:column;gap:26px;align-items:center;padding:26px}
.card{position:relative;width:750px;height:1000px;overflow:hidden;
  background:linear-gradient(178deg,#CE7938 0%,#D8873F 42%,#DF9353 100%);
  font-family:G,sans-serif;color:#fff;-webkit-font-smoothing:antialiased}

.hex{position:absolute;width:330px;height:340px;opacity:.14;background-size:30px auto;background-image:HEXURL}
.hex.bl{left:0;bottom:0}
.hex.tr{right:0;top:0}
.halo{position:absolute;left:50%;top:74%;transform:translate(-50%,-50%);width:840px;height:390px;
  border-radius:50%;background:radial-gradient(closest-side,rgba(255,255,255,.34),rgba(255,255,255,0))}

/* шапка */
.head{position:absolute;left:52px;right:52px;display:flex;flex-direction:column;z-index:4}
.head.ctr{text-align:center;align-items:center}
.hb{font-family:M,sans-serif;font-weight:900;text-transform:uppercase;line-height:.92;
  letter-spacing:-.012em;color:#fff;text-shadow:0 4px 18px rgba(120,58,14,.26)}
.hs{font-family:G,sans-serif;font-weight:600;color:rgba(255,255,255,.93);line-height:1.15;margin-top:8px;
  letter-spacing:.005em}

/* товар */
.prod{position:absolute;left:50%;transform:translateX(-50%)}
.prod img{display:block;width:100%;height:auto}
.pov{position:absolute;overflow:visible;pointer-events:none}
.p1{bottom:70px}.p2{bottom:106px}.p4{bottom:8px}.p5{bottom:-20px}.p6{bottom:62px;margin-left:20px}

/* чипы 2×2 */
.grid2{position:absolute;left:52px;right:52px;display:grid;grid-template-columns:1fr 1fr;gap:14px;z-index:4}
.chip{display:flex;align-items:center;gap:14px;background:#fff;border-radius:18px;padding:15px 18px;
  box-shadow:0 10px 24px rgba(112,52,10,.20)}
.chip b{font-weight:600;font-size:23px;line-height:1.2;color:#2B4A45}
.cic{display:flex;align-items:center;justify-content:center;width:50px;height:50px;flex:none;
  border-radius:14px;background:#E2F4F0;color:#2A9A88}
.cic .ic{width:28px;height:28px}
.cic.big{width:72px;height:72px;border-radius:20px}
.cic.big .ic{width:40px;height:40px}

/* выноска */
.bub{position:absolute;display:flex;gap:16px;align-items:flex-start;background:#fff;border-radius:22px;
  padding:22px 24px;box-shadow:0 16px 34px rgba(108,50,8,.24);color:#2B4A45;font-size:25px;
  font-weight:500;line-height:1.32;z-index:5}
.bub b{font-weight:800}
.bub::after{content:"";position:absolute;bottom:-17px;border:18px solid transparent;
  border-top-color:#fff;border-bottom:0;width:0;height:0}
.bub.t-left::after{left:38px}
.bub.t-right::after{right:38px}
.bic{display:flex;align-items:center;justify-content:center;width:52px;height:52px;flex:none;
  border-radius:15px;background:#E2F4F0;color:#2A9A88}
.bic .ic{width:30px;height:30px}

/* угловой знак */
.corner{position:absolute;left:52px;bottom:44px;display:flex;align-items:center;gap:18px;z-index:5}
.corner b{font-family:M,sans-serif;font-weight:800;font-size:30px;letter-spacing:.02em;line-height:1.1}
.corner s{display:block;font-family:G,sans-serif;text-decoration:none;font-weight:500;font-size:23px;
  letter-spacing:0;color:rgba(255,255,255,.92);margin-top:3px}

/* спецификации */
.specs{position:absolute;left:52px;right:52px;bottom:52px;display:flex;gap:16px;z-index:5}
.spec{flex:1;background:#fff;border-radius:20px;padding:16px 20px;color:#2B4A45;position:relative;
  box-shadow:0 12px 26px rgba(112,52,10,.20)}
.spec b{display:block;font-family:M,sans-serif;font-weight:800;font-size:30px;line-height:1.1}
.spec s{display:block;text-decoration:none;font-size:21px;font-weight:500;color:#6F8A85;margin-top:3px}
.spec em{position:absolute;right:18px;top:16px;font-style:normal;font-family:M,sans-serif;font-weight:800;
  font-size:17px;letter-spacing:.06em;color:#2A9A88;background:#E2F4F0;border-radius:8px;padding:4px 9px}
.spec.teal{background:#2A9A88;color:#fff;flex:0 0 268px}
.spec.teal s{color:rgba(255,255,255,.88)}

/* бренд-строка */
.brand{position:absolute;left:52px;right:52px;top:48px;display:flex;justify-content:space-between;
  align-items:center;z-index:5}
.logo{display:block;height:42px;width:auto}
.ru{display:flex;align-items:center;background:#fff;border-radius:14px;padding:11px 16px;
  box-shadow:0 8px 20px rgba(112,52,10,.18)}
.ru img{display:block;height:34px;width:auto}

/* фото-полоса */
.photo{position:absolute;left:0;right:0;top:0;height:470px;overflow:hidden}
.photo img{width:100%;height:100%;object-fit:cover;object-position:50% 58%}
.photo .fade{position:absolute;left:0;right:0;bottom:0;height:190px;
  background:linear-gradient(180deg,rgba(206,121,56,0),#D2803B 88%)}
#c3 .photo::after{content:"";position:absolute;left:0;right:0;top:0;height:280px;background:linear-gradient(180deg,rgba(54,25,5,.46),rgba(54,25,5,0))}
#c3 .head{text-shadow:0 4px 20px rgba(48,22,4,.55)}
#c3 .hs{color:#fff}

/* панель со свойствами */
.panel{position:absolute;left:52px;right:52px;bottom:52px;background:#fff;border-radius:26px;
  padding:26px 28px;display:flex;flex-direction:column;gap:17px;
  box-shadow:0 18px 38px rgba(108,50,8,.24)}
.prow{display:flex;align-items:center;gap:16px;color:#2B4A45;font-size:25px;font-weight:500;line-height:1.25}
.prow b{font-weight:800}
.chk{width:30px;height:30px;flex:none;color:#2A9A88;stroke-width:2.6}

/* лейбл */
.lbl{position:absolute;display:flex;align-items:center;gap:15px;font-family:M,sans-serif;font-weight:800;
  font-size:30px;letter-spacing:.07em;z-index:5}

/* круглая врезка */
.zoom{position:absolute;border-radius:50%;overflow:hidden;border:9px solid #fff;z-index:5;
  box-shadow:0 16px 32px rgba(108,50,8,.26)}
.zoom img{width:100%;height:100%;object-fit:cover}
.zoom .rib{position:absolute;left:-46px;top:26px;transform:rotate(-38deg);background:#2A9A88;color:#fff;
  font-family:G,sans-serif;font-weight:800;font-size:19px;letter-spacing:.04em;padding:6px 52px}

/* список запретов */
.deck{position:absolute;left:66px;right:66px;top:158px;text-align:center;font-size:27px;font-weight:600;
  line-height:1.34;color:rgba(255,255,255,.95);z-index:4}
.notlbl{position:absolute;left:52px;top:300px;font-family:M,sans-serif;font-weight:800;font-size:32px;
  letter-spacing:.05em;z-index:4}
.list{position:absolute;left:52px;right:52px;top:364px;display:flex;flex-direction:column;gap:13px;z-index:4}
.list .chip{padding:13px 18px}
.list .cic{color:#C9503C;background:#FBE6E1}
'''.replace("HEXURL", HEX)

HTML = ("<!doctype html><html lang='ru'><head><meta charset='utf-8'><title>Карточки</title>"
        "<style>%s\n%s</style></head><body>%s</body></html>"
        % (faces(), CSS, C1 + C2 + C3 + C4 + C5 + C6))

open(os.path.join(os.path.dirname(__file__), "cards.html"), "w").write(HTML)
print("cards.html", len(HTML), "bytes")
