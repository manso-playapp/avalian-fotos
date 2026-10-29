# Reencuadre de fotos a 1344x840 (pantalla de escenario Avalian)
# - Apaisadas: recorte "cover" con punto de foco manual (fx, fy en 0..1)
# - Verticales / impresas: foto entera tipo copia impresa sobre fondo desenfocado de la misma foto
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageOps
import glob, os
W, H = 1344, 840

def cover(im, fx=.5, fy=.5):
    """Recorta al ratio 16:10 centrando en el foco y escala a WxH."""
    r = W / H; w, h = im.size
    if w / h > r:   # más ancha: recorto ancho
        nw = round(h * r); x = round((w - nw) * fx); box = (x, 0, x + nw, h)
    else:           # más alta: recorto alto
        nh = round(w / r); y = round((h - nh) * fy); box = (0, y, w, y + nh)
    return im.crop(box).resize((W, H), Image.LANCZOS)

def framed(im, scale=.86):
    """Foto completa como copia impresa (borde blanco + sombra) sobre su versión desenfocada y teñida de verde."""
    bg = cover(im).filter(ImageFilter.GaussianBlur(38))
    bg = ImageEnhance.Brightness(bg).enhance(.55)
    tint = Image.new('RGB', (W, H), (1, 41, 31))          # verde profundo de marca
    bg = Image.blend(bg, tint, .45)
    # Foto contenida
    # Escala proporcional (agranda o achica) para ocupar siempre la misma caja:
    # siempre dentro de la caja de seguridad → nunca sale del encuadre
    # Caja de seguridad (incluye el borde blanco ≈ 2/45 del alto): 70% ancho × 78% alto.
    # Deja ~90 px arriba/abajo para el acercamiento lento, recortes de pantalla y el logo de esquina.
    k = min(W * .70 / im.size[0], H * .78 / im.size[1]) / (1 + 2/45)
    im2 = im.resize((round(im.size[0] * k), round(im.size[1] * k)), Image.LANCZOS)
    b = max(8, im2.size[1] // 45)                          # borde blanco proporcional
    card = ImageOps.expand(im2, border=b, fill=(250, 250, 246))
    # Sombra suave
    sh = Image.new('L', (card.size[0] + 80, card.size[1] + 80), 0)
    ImageDraw.Draw(sh).rectangle((40, 50, 40 + card.size[0], 50 + card.size[1]), fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    x = (W - card.size[0]) // 2; y = (H - card.size[1]) // 2
    bg.paste((0, 0, 0), (x - 40, y - 40), sh)
    bg.paste(card, (x, y))
    return bg

# (archivo, modo, parámetros) en orden de pasada: primero 2001, luego actuales
PLAN = [
    ('06.jpg', 'framed', dict(crop=(22, 0, 1223, 1232))),   # 1 InterAca San Bernardo 2001 (sin marco del portarretrato)
    ('01.jpg', 'framed', dict(crop=(0, 278, 590, 992))),    # 1° InterAca (solo la copia impresa)
    ('02.jpg', 'framed', dict()),
    ('03.jpg', 'framed',  dict()),
    ('04.jpg', 'framed',  dict()),
    ('05.jpg', 'framed',  dict()),
    ('07.jpg', 'framed',  dict()),
    ('08.jpg', 'framed',  dict()),
    ('09.jpg', 'framed',  dict()),
    ('10.jpg', 'framed',  dict()),
]
MOZZI = ['m24_3','m23_4','m23_2','m24_2','m28_','m27_1','m28_1','m25_2','m27_2','m27_3','m26_1',
         'm24_','m26_4','m29_3','m28_3','m25_1','m26_3','m29_','m29_2','m24_1','m23_3',
         'm26_','m28_2','m29_1','m25_3','m25_','m26_2','m27_','m23_1','m23_']
PLAN = [('../mozzi/'+m+'.jpg','framed',dict()) for m in MOZZI] + PLAN
for f in glob.glob('out/*.jpg'): os.remove(f)
for n, (f, mode, p) in enumerate(PLAN, 1):
    im = ImageOps.exif_transpose(Image.open('raw/' + f)).convert('RGB')
    if 'crop' in p: im = im.crop(p['crop'])
    out = framed(im) if mode == 'framed' else cover(im, p['fx'], p['fy'])
    out.save(f'out/avalian_25_{n:02d}.jpg', quality=90)
    print(n, f, mode)
