"""QR-наклейки для бронювання (20.10.2026). Стиль — як у наклейок відео (qr/make_qr.py).
QR ведуть на kulyk-dev.github.io/b/... (переадресація) — якщо бот колись зміниться, міняємо сторінку, а наклейки лишаються."""
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, black

BOT = "BuffaloUngvarZakazBot"
SITE = "https://kulyk-dev.github.io/b"
F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("D", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DB", F + "DejaVuSans-Bold.ttf"))
GREEN = HexColor("#0E5C3A"); GREY = HexColor("#555555"); LIGHT = HexColor("#BBBBBB")

# (шлях, заголовок, підпис столу, велика цифра)
CARDS = ([("pyr1", "Піраміда", "СТІЛ", "1"), ("vip10", "VIP-кімната", "СТІЛ", "10")]
         + [(f"pool{n}", "Пул", "СТІЛ", str(n)) for n in range(1, 8)]
         + [(f"darts{n}", "Дартс", "МІШЕНЬ", str(n)) for n in (1, 2)]
         + [("", "Бар · вихід", "", "")])

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

def card(c, path, hall, word, num, x0, y0, w, h):
    url = f"{SITE}/{path}" if path else SITE
    c.setStrokeColor(GREEN); c.setLineWidth(2.5)
    c.roundRect(x0 + 8*mm, y0 + 8*mm, w - 16*mm, h - 16*mm, 6*mm, stroke=1, fill=0)
    qs = 92*mm
    qx, qy = x0 + 18*mm, y0 + (h - qs) / 2
    draw_qr(c, matrix(url), qx, qy, qs)
    tx = qx + qs + 12*mm
    c.setFillColor(GREEN); c.setFont("DB", 17)
    if num:
        c.drawString(tx, y0 + h - 27*mm, "Забронюйте цей стіл")
        c.setFont("DB", 13); c.setFillColor(GREY); c.drawString(tx, y0 + h - 35*mm, hall)
        c.setFont("DB", 22); c.setFillColor(black); c.drawString(tx, y0 + h - 64*mm, word)
        c.setFont("DB", 90 if len(num) == 1 else 70)
        c.drawString(tx + (42 if word == "МІШЕНЬ" else 30)*mm, y0 + h - 64*mm, num)
        steps = ["1. Наведіть камеру телефону", "    на QR-код", "2. Оберіть дату й час",
                 "3. Мішень чекатиме на вас" if word == "МІШЕНЬ" else "3. Стіл чекатиме на вас"]
    else:
        c.drawString(tx, y0 + h - 27*mm, "Сподобалось?")
        c.setFont("DB", 26); c.setFillColor(black)
        c.drawString(tx, y0 + h - 50*mm, "Забронюйте")
        c.drawString(tx, y0 + h - 62*mm, "наступну гру")
        steps = ["1. Наведіть камеру телефону", "    на QR-код", "2. Оберіть зал, дату й час",
                 "3. Без дзвінків — за хвилину"]
    c.setFont("D", 12); c.setFillColor(black)
    yy = y0 + h - 80*mm
    for s in steps:
        c.drawString(tx, yy, s); yy -= 6.5*mm
    c.setFont("D", 9); c.setFillColor(GREY)
    c.drawString(tx, y0 + 24*mm, "Піраміда · VIP · пул · дартс")
    c.drawString(tx, y0 + 19*mm, f"Telegram: @{BOT}")

W, H = A4
c = canvas.Canvas("QR_bron.pdf", pagesize=A4)
c.setTitle("QR-коди для бронювання"); c.setAuthor("Buffalo")
half = H / 2
for i, (path, hall, word, num) in enumerate(CARDS):
    top = (i % 2 == 0)
    y0 = half if top else 0
    card(c, path, hall, word, num, 0, y0, W, half)
    if top:
        c.setStrokeColor(LIGHT); c.setDash(4, 4); c.setLineWidth(0.6)
        c.line(5*mm, half, W - 5*mm, half); c.setDash()
        c.setFont("D", 7); c.setFillColor(LIGHT); c.drawString(6*mm, half + 1.5*mm, "лінія відрізу")
    if not top or i == len(CARDS) - 1:
        c.showPage()
c.save()

for path, hall, word, num in CARDS:
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=4)
    q.add_data(f"{SITE}/{path}" if path else SITE); q.make(fit=True)
    q.make_image(fill_color="black", back_color="white").save(f"QR_bron_{path or 'bar'}.png")
print("ok")
