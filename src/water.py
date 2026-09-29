"""Физрендер воды на ткани и мягкой тени под товаром.

Вода не рисуется плоскими заливками, а считается как прозрачная плёнка:
по карте высот строятся нормали, по ним смещается выборка из настоящей
фотографии ткани (преломление), сверху кладутся блик по Блинну-Фонгу
и френелевская подсветка кромки. Поэтому в луже виден реальный материал.
"""
import json, numpy as np
from PIL import Image
from scipy import ndimage

S = 3                                    # апсемплинг рендера
L = (6, 75); B = (533, 6); R = (668, 71)  # углы силуэта в координатах вырезки
U = (B[0] - L[0], B[1] - L[1])            # длинная сторона, 200 см
V = (R[0] - B[0], R[1] - B[1])            # короткая сторона, 90 см
PAD = (70, 40, 70, 96)                    # поля под тень: л, в, п, н


def st_coords(h, w, pad, s):
    """Параметрические координаты верхней грани для каждого пикселя."""
    ox, oy = pad[0] * s, pad[1] * s
    ux, uy = U[0] * s, U[1] * s
    vx, vy = V[0] * s, V[1] * s
    det = ux * vy - uy * vx
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    px = xx - (L[0] * s + ox); py = yy - (L[1] * s + oy)
    return (px * vy - py * vx) / det, (ux * py - uy * px) / det


def blob(ss, tt, cs, ct, rs, rt, wob=(0.13, 3, 0.7), wob2=(0.07, 5, 2.1), wob3=(0.035, 9, 4.4)):
    """Органическое пятно в (s,t): эллипс с волнистым радиусом."""
    ds = (ss - cs) / rs; dt = (tt - ct) / rt
    th = np.arctan2(dt, ds)
    r = (1 + wob[0] * np.sin(wob[1] * th + wob[2]) + wob2[0] * np.sin(wob2[1] * th + wob2[2])
         + wob3[0] * np.sin(wob3[1] * th + wob3[2]))
    return np.sqrt(ds ** 2 + dt ** 2) / r


def soft_shadow(alpha, s):
    """Контактная тень по силуэту: смещение по свету и два радиуса размытия."""
    a = alpha.astype(np.float32) / 255.
    near = ndimage.gaussian_filter(np.roll(np.roll(a, int(5 * s), 0), int(3 * s), 1), 5 * s)
    far = ndimage.gaussian_filter(np.roll(np.roll(a, int(13 * s), 0), int(7 * s), 1), 20 * s)
    return np.clip(near * 0.55 + far * 0.42, 0, 1)


def build(src='product.png', wet=True, out='product_wet.png'):
    im = Image.open(src).convert('RGBA')
    w0, h0 = im.size
    W = (w0 + PAD[0] + PAD[2]) * S
    H = (h0 + PAD[1] + PAD[3]) * S
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    canvas.paste(im.resize((w0 * S, h0 * S), Image.LANCZOS), (PAD[0] * S, PAD[1] * S))
    arr = np.asarray(canvas).astype(np.float32) / 255.
    rgb, alpha = arr[..., :3].copy(), arr[..., 3].copy()

    if wet:
        ss, tt = st_coords(H, W, PAD, S)
        onface = alpha > .5

        # лужа и брызги: расстояния в единицах грани (s — 200 см, t — 90 см)
        d_pool = blob(ss, tt, .585, .495, .196, .415)
        pool = (d_pool < 1) & onface

        beads = np.zeros((H, W), bool)
        bead_h = np.zeros((H, W), np.float32)
        spec_r = [(.352, .128, 2.6), (.836, .208, 2.0), (.318, .800, 2.9),
                  (.872, .786, 1.7), (.262, .420, 1.5), (.742, .930, 2.2),
                  (.918, .500, 1.4), (.500, .950, 1.6), (.228, .660, 1.3),
                  (.952, .620, 1.1), (.196, .250, 1.0), (.640, .048, 1.3),
                  (.410, .930, 1.2), (.882, .350, 1.15), (.152, .500, .9),
                  (.690, .955, .95), (.268, .900, 1.05), (.966, .430, .85)]
        for cs, ct, r_cm in spec_r:                 # r_cm — радиус капли, см
            ds = (ss - cs) / (r_cm / 200.); dt = (tt - ct) / (r_cm / 90.)
            q = ds ** 2 + dt ** 2
            m = (q < 1) & onface
            beads |= m
            bead_h = np.maximum(bead_h, np.sqrt(np.clip(1 - q, 0, 1)) * (r_cm * 2.4 * S))

        # высота: у лужи плоский центр и скруглённая кромка (мениск)
        dist = ndimage.distance_transform_edt(pool).astype(np.float32)
        rim = 7.0 * S
        pool_h = (np.clip(dist / rim, 0, 1) ** .55) * (3.4 * S)
        h = np.maximum(pool_h, bead_h)
        rng = np.random.default_rng(7)
        ripple = ndimage.gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), 2.6 * S)
        ripple /= np.abs(ripple).max() + 1e-8
        h = h + ripple * (0.42 * S) * (h > 0)
        h = ndimage.gaussian_filter(h, .8 * S)
        water = pool | beads

        # нормали
        gy, gx = np.gradient(h)
        nz = np.full_like(h, 1.32 * S)
        n = np.stack([-gx, -gy, nz], -1)
        n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-8

        # преломление: выборка настоящей ткани со смещением по нормали
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        k = 34.0
        sx = np.clip(xx + n[..., 0] * k * (h > 0), 0, W - 1)
        sy = np.clip(yy + n[..., 1] * k * (h > 0), 0, H - 1)
        ref = np.stack([ndimage.map_coordinates(rgb[..., c], [sy, sx], order=1, mode='nearest')
                        for c in range(3)], -1)
        rgb = np.where(water[..., None], ref, rgb)

        # мокрая ткань темнее и насыщеннее
        wet_m = water[..., None].astype(np.float32)
        lum = rgb @ np.array([.299, .587, .114], np.float32)
        rgb = rgb * (1 - wet_m) + wet_m * np.clip((rgb - lum[..., None]) * 1.24 + lum[..., None] * .835, 0, 1)

        # блик по Блинну-Фонгу, свет сверху-слева как на исходном фото
        Lv = np.array([-.42, -.78, .47], np.float32); Lv /= np.linalg.norm(Lv)
        Hv = Lv + np.array([0, 0, 1], np.float32); Hv /= np.linalg.norm(Hv)
        ndh = np.clip(n @ Hv, 0, 1)
        grain = ndimage.gaussian_filter(np.random.default_rng(13).standard_normal((H, W)).astype(np.float32), 1.6 * S)
        grain = .62 + .38 * np.clip(grain / (np.abs(grain).max() + 1e-8) * 2.4 + .5, 0, 1)
        spec = ((ndh ** 110) * 1.70 + (ndh ** 20) * .16) * grain
        # широкий блик неба на глянце
        sheen = np.clip(-n[..., 1] * 2 * n[..., 2], 0, 1) ** 3.0 * .10
        # френель: кромка воды светлее
        fres = np.clip(1 - n[..., 2], 0, 1) ** 2.6 * .46
        # рассеянная составляющая: склон от света темнее
        shade = .84 + .16 * np.clip(n @ Lv, 0, 1)
        rgb = np.where(water[..., None], rgb * shade[..., None], rgb)
        glow = np.clip((spec + fres + sheen) * water, 0, 1.7)[..., None]
        rgb = np.clip(rgb + glow * np.array([.96, 1.0, .99], np.float32), 0, 1)

        # тень от кромки воды на ткани
        edge = ndimage.gaussian_filter(water.astype(np.float32), 2.2 * S)
        halo = np.clip(edge - water.astype(np.float32), 0, 1)[..., None]
        rgb = np.clip(rgb * (1 - halo * .22), 0, 1)

    # мягкая тень под товаром
    sh = soft_shadow(np.asarray(canvas)[..., 3], S)
    sh = np.clip(sh - alpha, 0, 1)
    shadow_rgb = np.array([.29, .13, .04], np.float32)
    out_rgb = rgb * alpha[..., None] + shadow_rgb * (1 - alpha[..., None])
    out_a = np.clip(alpha + sh * .52, 0, 1)

    res = np.concatenate([out_rgb, out_a[..., None]], -1)
    Image.fromarray((np.clip(res, 0, 1) * 255).astype(np.uint8)).save(out)
    print(out, (W, H))
    return W, H


if __name__ == '__main__':
    W, H = build(wet=False, out='product_sh.png')
    build(wet=True, out='product_wet.png')
    json.dump({'S': S, 'PAD': PAD, 'W': W, 'H': H,
               'L': L, 'B': B, 'R': R, 'U': U, 'V': V}, open('geom.json', 'w'))
    print('geom.json')
