from PIL import Image, ImageDraw, ImageFont, ImageFilter

# configuration
width = 154
height = 176
back_ground_color = (255, 255, 255)
font_size = 48


def move(fc, aft):
    r, g, b = fc
    inc = 15
    dr = (r + inc) % 225 if r < round(inc + (225 * ord(aft[0]) / 800)) else (r + 225 - inc) % 225
    dg = (g + inc) % 225 if g < round(inc + (225 * ord(aft[1]) / 800)) else (r + 225 - inc) % 225
    db = (b + inc) % 225 if b < round(inc + (225 * ord(aft[2]) / 800)) else (r + 225 - inc) % 225
    return dr, dg, db


def avatar(uuid, f="/tmp/text.jpg"):
    n = uuid.n
    tt = " " + uuid.id

    res, rem = divmod(n, 21780986680939)
    r = 15 + round(225 * rem / 21780986680939)
    res, rem = divmod(res, 21780986680939)
    g = 15 + round(225 * rem / 21780986680939)
    res, rem = divmod(res, 21780986680939)
    b = 15 + round(225 * rem / 21780986680939)

    im = Image.new("RGB", (width, height), back_ground_color)
    draw = ImageDraw.Draw(im)
    unicode_font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)
    font_color = r, g, b

    c = 0
    i = 0
    for l in tt[0:5]:
        draw.text((3 + i, 3), l, font=unicode_font, fill=font_color)
        i += 31
        c += 1
        font_color = move(font_color, tt[c:c + 3])

    i = 0
    for l in tt[5:10]:
        draw.text((3 + i, 61), l, font=unicode_font, fill=font_color)
        i += 31
        c += 1
        font_color = move(font_color, tt[c:c + 3])

    i = 0
    for l in tt[10:15]:
        draw.text((3 + i, 117), l, font=unicode_font, fill=font_color)
        i += 31
        c += 1
        if c == 13:
            font_color = move(font_color, tt[13:15] + tt[1])
        else:
            font_color = move(font_color, tt[14] + tt[1:3])

    im.save(f)
