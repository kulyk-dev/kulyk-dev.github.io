import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, black, white

BOT = "BuffaloUngvarVideoBot"
# 11.10.2026: QR ведут на свою переадресацию (GitHub Pages) — при блокировке бота меняем
# адрес в kulyk-dev.github.io/tN, а QR на столах остаются прежними.
SITE = "https://kulyk-dev.github.io"
TABLES = [2, 3, 5, 6, 7, 8, 9]
F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("D", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DB", F + "DejaVuSans-Bold.ttf"))
GREEN = HexColor("#0E5C3A"); GREY = HexColor("#555555"); LIGHT = HexColor("#BBBBBB")

def url_for(t): return f"{SITE}/t{t}"

def matrix(url):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=0)
    q.add_data(url); q.make(fit=True)
    return q.get_matrix()

def draw_qr(c, m, x, y, size):
    n = len(m); cell = size / n
    c.setFillColor(black)
    for r, row in enumerate(m):
        for col, v in enumerate(row):
            if v:
                c.rect(x + col * cell, y + size - (r + 1) * cell, cell + 0.05, cell + 0.05, stroke=0, fill=1)

def card(c, table, x0, y0, w, h):
    c.setStrokeColor(GREEN); c.setLineWidth(2.5)
    c.roundRect(x0 + 8*mm, y0 + 8*mm, w - 16*mm, h - 16*mm, 6*mm, stroke=1, fill=0)
    qs = 92*mm
    qx, qy = x0 + 18*mm, y0 + (h - qs) / 2
    draw_qr(c, matrix(url_for(table)), qx, qy, qs)
    tx = qx + qs + 12*mm
    c.setFillColor(GREEN); c.setFont("DB", 17)
    c.drawString(tx, y0 + h - 27*mm, "Відео вашої гри")
    c.setFont("DB", 24); c.setFillColor(black)
    c.drawString(tx, y0 + h - 64*mm, "СТІЛ")
    c.setFont("DB", 96)
    c.drawString(tx + 30*mm, y0 + h - 64*mm, str(table))
    c.setFont("D", 12); c.setFillColor(black)
    steps = ["1. Наведіть камеру телефону", "    на QR-код",
             "2. Оберіть, яку частину гри", "    надіслати",
             "3. Відео прийде в Telegram"]
    yy = y0 + h - 80*mm
    for s in steps:
        c.drawString(tx, yy, s); yy -= 6.5*mm
    c.setFont("D", 9); c.setFillColor(GREY)
    c.drawString(tx, y0 + 24*mm, "Камера над столом, без звуку.")
    c.drawString(tx, y0 + 19*mm, f"Telegram: @{BOT}")

W, H = A4
c = canvas.Canvas("QR_stoly.pdf", pagesize=A4)
c.setTitle("QR-коди для столів"); c.setAuthor("Buffalo")
half = H / 2
for i, tb in enumerate(TABLES):
    top = (i % 2 == 0)
    y0 = half if top else 0
    card(c, tb, 0, y0, W, half)
    if top:
        c.setStrokeColor(LIGHT); c.setDash(4, 4); c.setLineWidth(0.6)
        c.line(5*mm, half, W - 5*mm, half); c.setDash()
        c.setFont("D", 7); c.setFillColor(LIGHT); c.drawString(6*mm, half + 1.5*mm, "лінія відрізу")
    if not top or i == len(TABLES) - 1:
        c.showPage()
c.save()

for tb in TABLES:
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=4)
    q.add_data(url_for(tb)); q.make(fit=True)
    q.make_image(fill_color="black", back_color="white").save(f"QR_stil_{tb}.png")
print("ok")
