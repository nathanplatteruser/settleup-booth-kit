#!/usr/bin/env python3
"""Build Denver leave-behind PDF packs: DEMO ONLY + CONVERT."""
from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path

import qrcode
from PIL import Image as PILImage
from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parent
SHOTS = ROOT / "shots"
QRS = ROOT / "qrs"
QRS.mkdir(exist_ok=True)

PAGE_W, PAGE_H = letter  # 612 x 792

# Brand colors
BG = HexColor("#0f1419")
PANEL = HexColor("#1a2332")
BORDER = HexColor("#2a3544")
TEXT = HexColor("#e7ecf3")
MUTED = HexColor("#8b9bb4")
ACCENT = HexColor("#5b9fd4")
ON = HexColor("#2d6cdf")
YES = HexColor("#3ecf8e")
WARN = HexColor("#fbbf24")
BAD = HexColor("#f87171")
HERO = HexColor("#f0a020")
DEMO_TAG = HexColor("#3ecf8e")
CONV_TAG = HexColor("#f0a020")

BASE_PAGES = "https://nathanplatteruser.github.io/settleup-booth-kit/denver-leavebehinds"

DEMO_LINKS = [
    (
        "Open the letter demo",
        "DEMO-OUTPUT.html · LTR-300-REFUSED",
        "https://nathanplatteruser.github.io/dispute-agent-demo/DEMO-OUTPUT.html",
        "demo-letter",
    ),
    (
        "GitHub dispute-agent-demo",
        "Source repo · README · sandbox",
        "https://github.com/nathanplatteruser/dispute-agent-demo",
        "demo-repo",
    ),
    (
        "Demo Pages home",
        "Public GitHub Pages for the demo",
        "https://nathanplatteruser.github.io/dispute-agent-demo/",
        "demo-pages",
    ),
    (
        "Session walkthrough",
        "Nathan · Olga · Ralph beats",
        f"{BASE_PAGES}/walkthrough.html",
        "walkthrough",
    ),
    (
        "Demo QR wall (screen)",
        "iPhone-friendly demo assets only",
        f"{BASE_PAGES}/demo-only.html",
        "demo-screen",
    ),
]

CONVERT_LINKS = [
    (
        "Book Nathan (PRIMARY)",
        "20-min walkthrough · Calendly",
        "https://calendly.com/nathanplatter",
        "book-calendly",
        True,
    ),
    (
        "SettleUp home",
        "settleupcollections.com",
        "https://settleupcollections.com/",
        "home",
        False,
    ),
    (
        "Pricing",
        "Pilot · Firm · Audit",
        "https://settleupcollections.com/pricing",
        "pricing",
        False,
    ),
    (
        "Letter Risk Audit",
        "Consulting SKU · $2,500",
        "https://settleupcollections.com/audit",
        "audit",
        False,
    ),
    (
        "Free tools / Everything",
        "Demos + tools hub",
        "https://settleupcollections.com/everything",
        "everything",
        False,
    ),
    (
        "Risk scan lead magnet",
        "Quick letter-risk scan",
        "https://settleupcollections.com/risk-scan",
        "risk-scan",
        False,
    ),
    (
        "Conference QR hub",
        "Staff / booth bookmark",
        "https://settleupcollections.com/qr",
        "qr-hub",
        False,
    ),
    (
        "Brainstorm hub",
        "Event landing",
        "https://settleupcollections.com/brainstorm",
        "brainstorm",
        False,
    ),
    (
        "Demo recall (DEMO-OUTPUT)",
        "Reconnect to what you saw",
        "https://nathanplatteruser.github.io/dispute-agent-demo/DEMO-OUTPUT.html",
        "demo-recall",
        False,
    ),
    (
        "Waitlist",
        "Optional · stay in the loop",
        "https://settleupcollections.com/waitlist",
        "waitlist",
        False,
    ),
]


def make_qr(url: str, path: Path, box_size: int = 12) -> Path:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(path)
    return path


def ensure_qrs():
    for title, why, url, slug in DEMO_LINKS:
        make_qr(url, QRS / f"{slug}.png")
    for title, why, url, slug, _ in CONVERT_LINKS:
        make_qr(url, QRS / f"{slug}.png")


def draw_bg(c: canvas.Canvas):
    c.setFillColor(BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)


def draw_footer(c: canvas.Canvas, label: str, page_no: int | None = None):
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    left = "SettleUp Collections · Brainstorm 2026 Denver · " + label
    c.drawString(0.55 * inch, 0.38 * inch, left)
    if page_no is not None:
        c.drawRightString(PAGE_W - 0.55 * inch, 0.38 * inch, str(page_no))


def rounded_rect(c, x, y, w, h, r=10, fill=None, stroke=None, sw=1):
    c.saveState()
    if fill:
        c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(sw)
    p = c.beginPath()
    p.moveTo(x + r, y)
    p.lineTo(x + w - r, y)
    p.arcTo(x + w - 2 * r, y, x + w, y + 2 * r, -90, 90)
    p.lineTo(x + w, y + h - r)
    p.arcTo(x + w - 2 * r, y + h - 2 * r, x + w, y + h, 0, 90)
    p.lineTo(x + r, y + h)
    p.arcTo(x, y + h - 2 * r, x + 2 * r, y + h, 90, 90)
    p.lineTo(x, y + r)
    p.arcTo(x, y, x + 2 * r, y + 2 * r, 180, 90)
    p.close()
    if fill and stroke:
        c.drawPath(p, fill=1, stroke=1)
    elif fill:
        c.drawPath(p, fill=1, stroke=0)
    else:
        c.drawPath(p, fill=0, stroke=1)
    c.restoreState()


def fit_image(path: Path, max_w: float, max_h: float):
    im = PILImage.open(path)
    iw, ih = im.size
    scale = min(max_w / iw, max_h / ih)
    return iw * scale, ih * scale, ImageReader(str(path))


def wrap_text(c, text, font, size, max_w):
    c.setFont(font, size)
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if c.stringWidth(trial, font, size) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ── DEMO PDF ──────────────────────────────────────────────────────────────


def demo_cover(c: canvas.Canvas):
    draw_bg(c)
    # tag
    rounded_rect(c, 0.55 * inch, PAGE_H - 1.15 * inch, 2.6 * inch, 0.42 * inch, r=8, fill=HexColor("#14532d"), stroke=YES, sw=1.2)
    c.setFillColor(YES)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.7 * inch, PAGE_H - 1.02 * inch, "STACK DEMO  ·  NO SALES CTAs")

    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 28)
    y = PAGE_H - 1.85 * inch
    for line in ["STACK DEMO", "Dispute Queue"]:
        c.drawString(0.55 * inch, y, line)
        y -= 0.42 * inch
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.55 * inch, y, "Nathan  ·  Olga  ·  Ralph")
    y -= 0.45 * inch

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    c.drawString(0.55 * inch, y, "Brainstorm 2026 Denver  ·  SettleUp Collections")
    y -= 0.55 * inch

    # proof strip
    rounded_rect(c, 0.55 * inch, y - 1.55 * inch, PAGE_W - 1.1 * inch, 1.7 * inch, r=12, fill=PANEL, stroke=BORDER)
    c.setFillColor(HERO)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.75 * inch, y - 0.15 * inch, "WHAT YOU SAW")
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(0.75 * inch, y - 0.45 * inch, "Refuse over hallucinate")
    c.setFont("Helvetica", 11)
    c.setFillColor(MUTED)
    lines = [
        "Letter LTR-300-REFUSED  ·  model wrote $1,000  ·  ledger $20,370.53",
        "Run stats: 300 / 20 / 19 / 1   (checked · remediations · fixed · refused)",
        "Console: /app?booth=1  ·  Remediation tab  ·  Thursday 8:30 sandbox",
    ]
    yy = y - 0.75 * inch
    for ln in lines:
        c.drawString(0.75 * inch, yy, ln)
        yy -= 0.28 * inch

    # credits
    cy = 2.4 * inch
    rounded_rect(c, 0.55 * inch, cy - 0.1 * inch, PAGE_W - 1.1 * inch, 1.55 * inch, r=12, fill=PANEL, stroke=BORDER)
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75 * inch, cy + 1.2 * inch, "SESSION CREDITS")
    credits = [
        ("Nathan Platter", "SettleUp / Platter Analytics  ·  drives refuse-letter UI"),
        ("Olga Mironova", "CCMR3  ·  ops / capacity / exam"),
        ("Ralph Hall", "GVH  ·  setup / deterministic automation"),
    ]
    yy = cy + 0.9 * inch
    for name, role in credits:
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(0.75 * inch, yy, name)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9)
        c.drawString(2.85 * inch, yy, role)
        yy -= 0.32 * inch

    c.setFillColor(MUTED)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(PAGE_W / 2, 1.1 * inch, "Demo assets only. No Calendly. No pricing. No marketing CTAs.")
    c.setFont("Helvetica", 9)
    c.drawCentredString(PAGE_W / 2, 0.85 * inch, "Re-open what you saw. Scan the QR cards inside.")
    draw_footer(c, "STACK DEMO", 1)
    c.showPage()


def demo_screens(c: canvas.Canvas):
    draw_bg(c)
    c.setFillColor(YES)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.55 * inch, PAGE_H - 0.55 * inch, "WHAT YOU SAW ON SCREEN")
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.55 * inch, PAGE_H - 0.9 * inch, "Ops board + refused letter remediation")

    # Remediation (primary) large on top
    rem = SHOTS / "app-remediation.png"
    max_w = PAGE_W - 1.1 * inch
    max_h = 3.55 * inch
    dw, dh, ir = fit_image(rem, max_w, max_h)
    x = (PAGE_W - dw) / 2
    y = PAGE_H - 1.15 * inch - dh
    rounded_rect(c, x - 4, y - 4, dw + 8, dh + 8, r=6, fill=PANEL, stroke=BORDER)
    c.drawImage(ir, x, y, width=dw, height=dh, preserveAspectRatio=True, mask="auto")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W / 2, y - 14, "Remediation · LTR-300-REFUSED · primary visual recall")

    # Console below
    cons = SHOTS / "app-console.png"
    max_h2 = 2.7 * inch
    dw2, dh2, ir2 = fit_image(cons, max_w, max_h2)
    x2 = (PAGE_W - dw2) / 2
    y2 = 0.85 * inch
    rounded_rect(c, x2 - 4, y2 - 4, dw2 + 8, dh2 + 8, r=6, fill=PANEL, stroke=BORDER)
    c.drawImage(ir2, x2, y2, width=dw2, height=dh2, preserveAspectRatio=True, mask="auto")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W / 2, y2 - 14, "Operations / dashboard console · /app?booth=1")

    draw_footer(c, "STACK DEMO", 2)
    c.showPage()


def demo_qr_card(c: canvas.Canvas, title, why, url, slug, page_no, index, total):
    draw_bg(c)
    # banner
    rounded_rect(c, 0.55 * inch, PAGE_H - 1.0 * inch, PAGE_W - 1.1 * inch, 0.5 * inch, r=8, fill=HexColor("#14532d"), stroke=YES)
    c.setFillColor(YES)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 0.82 * inch, f"DEMO QR  {index}/{total}  ·  STACK DEMO  ·  no sales CTAs")

    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 22)
    lines = wrap_text(c, title, "Helvetica-Bold", 22, PAGE_W - 1.2 * inch)
    y = PAGE_H - 1.55 * inch
    for ln in lines:
        c.drawCentredString(PAGE_W / 2, y, ln)
        y -= 0.32 * inch

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_W / 2, y - 0.05 * inch, why)

    # QR
    qr_path = QRS / f"{slug}.png"
    qr_size = 3.2 * inch
    qx = (PAGE_W - qr_size) / 2
    qy = y - 0.5 * inch - qr_size
    rounded_rect(c, qx - 12, qy - 12, qr_size + 24, qr_size + 24, r=12, fill=white, stroke=BORDER)
    c.drawImage(str(qr_path), qx, qy, width=qr_size, height=qr_size, mask="auto")

    c.setFillColor(ACCENT)
    c.setFont("Helvetica", 9)
    # wrap URL
    url_lines = wrap_text(c, url, "Helvetica", 9, PAGE_W - 1.4 * inch)
    uy = qy - 0.45 * inch
    for ul in url_lines:
        c.drawCentredString(PAGE_W / 2, uy, ul)
        uy -= 0.18 * inch

    c.setFillColor(MUTED)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(PAGE_W / 2, 0.95 * inch, "Scan to re-open the Dispute Queue demo assets.")
    draw_footer(c, "STACK DEMO", page_no)
    c.showPage()



def demo_ops_fte(c: canvas.Canvas, page_no: int):
    """Olga locked FTE + complaint≠dispute framing (ops callout)."""
    draw_bg(c)
    c.setFillColor(YES)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.55 * inch, PAGE_H - 0.55 * inch, "OPS CALLOUT  ·  OLGA LOCKED")
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.55 * inch, PAGE_H - 0.9 * inch, "FTE minutes per dispute")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(0.55 * inch, PAGE_H - 1.15 * inch, "Cite as Olga Mironova (CCMR3) ranges — not Nathan’s shop, not a universal time-study.")

    stages = [
        ("Intake", "3–5"),
        ("Review", "~4"),
        ("Research", "20–30"),
        ("Draft", "5–7"),
        ("Compliance", "3–6"),
        ("Close", "3–5"),
    ]
    # stage cards in 2 rows of 3
    card_w = (PAGE_W - 1.3 * inch) / 3
    card_h = 0.95 * inch
    y0 = PAGE_H - 1.45 * inch
    for i, (name, mins) in enumerate(stages):
        row, col = divmod(i, 3)
        x = 0.55 * inch + col * (card_w + 0.1 * inch)
        y = y0 - row * (card_h + 0.12 * inch) - card_h
        rounded_rect(c, x, y, card_w, card_h, r=10, fill=PANEL, stroke=BORDER)
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x + card_w / 2, y + card_h - 0.28 * inch, name.upper())
        c.setFillColor(YES)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(x + card_w / 2, y + 0.28 * inch, mins)

    y = y0 - 2 * (card_h + 0.12 * inch) - 0.15 * inch
    rounded_rect(c, 0.55 * inch, y - 0.85 * inch, PAGE_W - 1.1 * inch, 0.85 * inch, r=10, fill=PANEL, stroke=BORDER)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.75 * inch, y - 0.32 * inch, "Working range ~38-57  ·  demo baseline upper (~57)  ·  lunch/meetings vs 100% desk")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(0.75 * inch, y - 0.58 * inch, "Replaces any old “12 min working average” line.")

    # framing quote
    y2 = y - 1.15 * inch
    rounded_rect(c, 0.55 * inch, 1.35 * inch, PAGE_W - 1.1 * inch, y2 - 1.35 * inch, r=10, fill=PANEL, stroke=HERO)
    c.setFillColor(HERO)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75 * inch, y2 - 0.28 * inch, "COMPLAINT ≠ DISPUTE  ·  OLGA FRAMING")
    frame = (
        "Complaints and disputes aren’t the same thing, but architecture doesn’t care — "
        "public complaint language, synthetic ledger; point it at your own dispute queue "
        "and it’s the same metadata, just different buckets and different template letters."
    )
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    yy = y2 - 0.55 * inch
    for ln in wrap_text(c, frame, "Helvetica", 10, PAGE_W - 1.7 * inch):
        c.drawString(0.75 * inch, yy, ln)
        yy -= 0.18 * inch
    c.setFillColor(YES)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75 * inch, 1.55 * inch, "Audit-trail: yes (Olga confirmed).")

    draw_footer(c, "STACK DEMO", page_no)
    c.showPage()


def demo_proof_back(c: canvas.Canvas, page_no: int):
    draw_bg(c)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.55 * inch, PAGE_H - 0.85 * inch, "Proof lines (from the sandbox)")

    cards = [
        ("Refuse over hallucinate", "The gate checked, tried once, then refused out loud."),
        ("$1,000 vs $20,370.53", "Model wrote the wrong dollars. Ledger truth won."),
        ("300 / 20 / 19 / 1", "Checked · remediations · fixed · refused (LTR-300-REFUSED)."),
        ("Nathan · Olga · Ralph", "UI drive · ops/exam · setup/deterministic automation."),
    ]
    y = PAGE_H - 1.2 * inch
    for title, body in cards:
        rounded_rect(c, 0.55 * inch, y - 1.05 * inch, PAGE_W - 1.1 * inch, 1.0 * inch, r=10, fill=PANEL, stroke=BORDER)
        c.setFillColor(YES)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0.75 * inch, y - 0.35 * inch, title)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 10)
        for ln in wrap_text(c, body, "Helvetica", 10, PAGE_W - 1.6 * inch):
            c.drawString(0.75 * inch, y - 0.6 * inch, ln)
            y_line = y - 0.6 * inch
            break
        # draw remaining wrapped
        lines = wrap_text(c, body, "Helvetica", 10, PAGE_W - 1.6 * inch)
        yy = y - 0.6 * inch
        for i, ln in enumerate(lines):
            if i == 0:
                continue
            yy -= 0.18 * inch
            c.drawString(0.75 * inch, yy, ln)
        y -= 1.2 * inch

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawCentredString(PAGE_W / 2, 1.0 * inch, "This pack is DEMO ONLY. For booking / pricing use the CONVERT leave-behind.")
    draw_footer(c, "STACK DEMO", page_no)
    c.showPage()


def build_demo_pdf(path: Path):
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setTitle("SettleUp Dispute Queue Demo ONLY — Brainstorm 2026 Denver")
    c.setAuthor("SettleUp Collections / Platter Analytics")
    demo_cover(c)
    demo_screens(c)
    n = len(DEMO_LINKS)
    for i, (title, why, url, slug) in enumerate(DEMO_LINKS, start=1):
        demo_qr_card(c, title, why, url, slug, page_no=2 + i, index=i, total=n)
    demo_ops_fte(c, page_no=3 + n)
    demo_proof_back(c, page_no=4 + n)
    c.save()
    print("wrote", path)


def build_demo_2up(path: Path):
    """2-up cut sheets: cover note + pairs of QR cards."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setTitle("SettleUp Dispute Queue Demo ONLY 2-up")
    draw_bg(c)
    rounded_rect(c, 0.5 * inch, PAGE_H - 1.1 * inch, PAGE_W - 1.0 * inch, 0.55 * inch, r=8, fill=HexColor("#14532d"), stroke=YES)
    c.setFillColor(YES)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 0.88 * inch, "STACK DEMO 2-UP CUTS  ·  NO SALES CTAs  ·  cut on dashed midline")
    c.setFillColor(TEXT)
    c.setFont("Helvetica", 11)
    y = PAGE_H - 1.6 * inch
    for ln in [
        "Print color, US Letter, 100% scale, single-sided, 80-110 lb cardstock.",
        "This is the DEMO ONLY stack. Do not mix with CONVERT or Stack A/B piles.",
        "Each half-page below is one QR card. Cut on the dashed horizontal line.",
    ]:
        c.drawString(0.6 * inch, y, ln)
        y -= 0.28 * inch
    draw_footer(c, "STACK DEMO 2-UP")
    c.showPage()

    # pair cards
    pairs = []
    links = list(DEMO_LINKS)
    for i in range(0, len(links), 2):
        pairs.append(links[i : i + 2])

    for pair in pairs:
        draw_bg(c)
        half_h = PAGE_H / 2
        for idx, item in enumerate(pair):
            title, why, url, slug = item
            top = PAGE_H if idx == 0 else half_h
            # card area
            margin = 0.45 * inch
            card_h = half_h - 0.35 * inch
            cy0 = top - half_h + 0.15 * inch if idx == 1 else half_h + 0.15 * inch
            # simplify: draw relative to band
            band_bottom = half_h if idx == 0 else 0
            band_top = PAGE_H if idx == 0 else half_h

            # green tag
            tag_y = band_top - 0.45 * inch
            c.setFillColor(YES)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(margin, tag_y, "STACK DEMO · DEMO QR")

            c.setFillColor(TEXT)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margin, tag_y - 0.28 * inch, title)
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 9)
            c.drawString(margin, tag_y - 0.48 * inch, why)

            qr_size = 1.85 * inch
            qx = PAGE_W - margin - qr_size - 0.1 * inch
            qy = band_bottom + 0.55 * inch
            c.setFillColor(white)
            c.roundRect(qx - 6, qy - 6, qr_size + 12, qr_size + 12, 6, fill=1, stroke=0)
            c.drawImage(str(QRS / f"{slug}.png"), qx, qy, width=qr_size, height=qr_size, mask="auto")

            c.setFillColor(ACCENT)
            c.setFont("Helvetica", 7)
            # short URL under title area
            url_y = tag_y - 0.75 * inch
            for ul in wrap_text(c, url, "Helvetica", 7, PAGE_W - qr_size - 1.3 * inch):
                c.drawString(margin, url_y, ul)
                url_y -= 0.14 * inch

        # dashed midline
        c.setStrokeColor(MUTED)
        c.setDash(3, 3)
        c.setLineWidth(0.8)
        c.line(0.4 * inch, half_h, PAGE_W - 0.4 * inch, half_h)
        c.setDash()
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7)
        c.drawCentredString(PAGE_W / 2, half_h + 3, "✂ cut")
        draw_footer(c, "STACK DEMO 2-UP")
        c.showPage()

    c.save()
    print("wrote", path)


# ── CONVERT PDF ────────────────────────────────────────────────────────────


def convert_cover(c: canvas.Canvas):
    draw_bg(c)
    rounded_rect(c, 0.55 * inch, PAGE_H - 1.15 * inch, 3.4 * inch, 0.42 * inch, r=8, fill=HexColor("#3a2e12"), stroke=HERO, sw=1.2)
    c.setFillColor(HERO)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.7 * inch, PAGE_H - 1.02 * inch, "STACK CONVERT  ·  AFTER THE DEMO")

    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 26)
    y = PAGE_H - 1.8 * inch
    c.drawString(0.55 * inch, y, "STACK CONVERT")
    y -= 0.4 * inch
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(ACCENT)
    c.drawString(0.55 * inch, y, "SettleUp Collections")
    y -= 0.35 * inch
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    c.drawString(0.55 * inch, y, "After the demo  ·  Brainstorm 2026 Denver")

    # small remediation recall
    rem = SHOTS / "app-remediation.png"
    max_w = PAGE_W - 1.1 * inch
    max_h = 2.35 * inch
    dw, dh, ir = fit_image(rem, max_w, max_h)
    x = (PAGE_W - dw) / 2
    y_img = y - 0.35 * inch - dh
    rounded_rect(c, x - 4, y_img - 4, dw + 8, dh + 8, r=6, fill=PANEL, stroke=BORDER)
    c.drawImage(ir, x, y_img, width=dw, height=dh, preserveAspectRatio=True, mask="auto")
    c.setFillColor(WARN)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(PAGE_W / 2, y_img - 16, "You saw this refuse gate with Nathan, Olga, and Ralph.")

    # Nathan identity
    iy = 1.55 * inch
    rounded_rect(c, 0.55 * inch, iy, PAGE_W - 1.1 * inch, 1.15 * inch, r=10, fill=PANEL, stroke=BORDER)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(0.75 * inch, iy + 0.78 * inch, "Nathan Platter")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(0.75 * inch, iy + 0.52 * inch, "Principal, Analytics & AI")
    c.drawString(0.75 * inch, iy + 0.32 * inch, "SettleUp Collections  ·  Platter Analytics")
    c.setFillColor(ACCENT)
    c.setFont("Helvetica", 9)
    c.drawString(0.75 * inch, iy + 0.12 * inch, "Book 20 min: calendly.com/nathanplatter")

    draw_footer(c, "STACK CONVERT", 1)
    c.showPage()


def convert_copy(c: canvas.Canvas):
    draw_bg(c)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.55 * inch, PAGE_H - 0.8 * inch, "Why the letter-risk gate is an investment")

    paras = [
        "Wrong dollars leaving your building is not a tooling preference. It is liability. The Dispute Queue demo showed a model that wrote $1,000 against a ledger of $20,370.53. The system checked, tried one remediation, and refused out loud.",
        "Capacity without a gate is exposure. Olga’s locked FTE (~38-57; demo uses upper ~57 for human lunch/meetings) is the ops clock; examiners already know what a paper trail must survive. A refuse-letter gate sits between AI throughput and the letter that ships.",
        "Pilot, Firm, and Letter Risk Audit are framed as investment, not a cost center. You buy a path to more volume with the same team, without shipping hallucinated balances. Proof is free to inspect. Production is your system of record, your rules, and your accountability.",
        "If wrong dollars cannot leave your building, book twenty minutes with Nathan. Bring the refuse story you just saw. We will map Pilot or Firm or a scoped Letter Risk Audit to your shop.",
    ]
    y = PAGE_H - 1.2 * inch
    for p in paras:
        rounded_rect(c, 0.55 * inch, y - 1.35 * inch, PAGE_W - 1.1 * inch, 1.4 * inch, r=10, fill=PANEL, stroke=BORDER)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 10)
        lines = wrap_text(c, p, "Helvetica", 10, PAGE_W - 1.6 * inch)
        yy = y - 0.28 * inch
        for ln in lines:
            c.drawString(0.75 * inch, yy, ln)
            yy -= 0.17 * inch
        y -= 1.55 * inch

    # pricing strip
    rounded_rect(c, 0.55 * inch, 0.7 * inch, PAGE_W - 1.1 * inch, 0.85 * inch, r=10, fill=HexColor("#3a2e12"), stroke=HERO)
    c.setFillColor(HERO)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75 * inch, 1.25 * inch, "PRICING (LOCKED)")
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.75 * inch, 0.95 * inch, "Pilot $499/mo   ·   Firm $1,299/mo   ·   Letter Risk Audit $2,500")
    draw_footer(c, "STACK CONVERT", 2)
    c.showPage()


def convert_screenshot_recall(c: canvas.Canvas):
    draw_bg(c)
    c.setFillColor(HERO)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.55 * inch, PAGE_H - 0.55 * inch, "VISUAL RECALL")
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.55 * inch, PAGE_H - 0.9 * inch, "Same refuse gate you saw on stage")

    rem = SHOTS / "app-remediation.png"
    cons = SHOTS / "app-console.png"
    max_w = PAGE_W - 1.1 * inch

    dw, dh, ir = fit_image(rem, max_w, 3.4 * inch)
    x = (PAGE_W - dw) / 2
    y = PAGE_H - 1.15 * inch - dh
    rounded_rect(c, x - 4, y - 4, dw + 8, dh + 8, r=6, fill=PANEL, stroke=BORDER)
    c.drawImage(ir, x, y, width=dw, height=dh, preserveAspectRatio=True, mask="auto")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W / 2, y - 14, "Remediation · refuse gate (same screenshot as DEMO pack)")

    dw2, dh2, ir2 = fit_image(cons, max_w, 2.5 * inch)
    x2 = (PAGE_W - dw2) / 2
    y2 = 0.85 * inch
    rounded_rect(c, x2 - 4, y2 - 4, dw2 + 8, dh2 + 8, r=6, fill=PANEL, stroke=BORDER)
    c.drawImage(ir2, x2, y2, width=dw2, height=dh2, preserveAspectRatio=True, mask="auto")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W / 2, y2 - 14, "Ops console · /app?booth=1")

    draw_footer(c, "STACK CONVERT", 3)
    c.showPage()


def convert_qr_card(c, title, why, url, slug, primary, page_no, index, total):
    draw_bg(c)
    if primary:
        rounded_rect(c, 0.55 * inch, PAGE_H - 1.0 * inch, PAGE_W - 1.1 * inch, 0.5 * inch, r=8, fill=HexColor("#3a2e12"), stroke=HERO)
        c.setFillColor(HERO)
        label = f"PRIMARY CTA  {index}/{total}  ·  STACK CONVERT  ·  book Nathan"
    else:
        rounded_rect(c, 0.55 * inch, PAGE_H - 1.0 * inch, PAGE_W - 1.1 * inch, 0.5 * inch, r=8, fill=PANEL, stroke=BORDER)
        c.setFillColor(ACCENT)
        label = f"CONVERT QR  {index}/{total}  ·  STACK CONVERT"
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 0.82 * inch, label)

    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 20)
    lines = wrap_text(c, title, "Helvetica-Bold", 20, PAGE_W - 1.2 * inch)
    y = PAGE_H - 1.55 * inch
    for ln in lines:
        c.drawCentredString(PAGE_W / 2, y, ln)
        y -= 0.3 * inch

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    c.drawCentredString(PAGE_W / 2, y - 0.05 * inch, why)

    qr_size = 3.0 * inch if primary else 2.85 * inch
    qx = (PAGE_W - qr_size) / 2
    qy = y - 0.45 * inch - qr_size
    rounded_rect(c, qx - 12, qy - 12, qr_size + 24, qr_size + 24, r=12, fill=white, stroke=HERO if primary else BORDER, sw=2 if primary else 1)
    c.drawImage(str(QRS / f"{slug}.png"), qx, qy, width=qr_size, height=qr_size, mask="auto")

    c.setFillColor(ACCENT)
    c.setFont("Helvetica", 9)
    uy = qy - 0.4 * inch
    for ul in wrap_text(c, url, "Helvetica", 9, PAGE_W - 1.4 * inch):
        c.drawCentredString(PAGE_W / 2, uy, ul)
        uy -= 0.18 * inch

    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawCentredString(PAGE_W / 2, 0.95 * inch, "SettleUp Collections  ·  find Nathan onsite or book 20 minutes")
    draw_footer(c, "STACK CONVERT", page_no)
    c.showPage()


def convert_close(c, page_no):
    draw_bg(c)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 1.5 * inch, "Next step")
    c.setFont("Helvetica", 13)
    c.setFillColor(MUTED)
    for i, ln in enumerate([
        "Book a 20-minute walkthrough with Nathan.",
        "Or find him onsite at Brainstorm 2026 Denver.",
        "",
        "Pilot $499/mo  ·  Firm $1,299/mo  ·  Letter Risk Audit $2,500",
        "",
        "calendly.com/nathanplatter",
        "settleupcollections.com",
    ]):
        c.drawCentredString(PAGE_W / 2, PAGE_H - 2.2 * inch - i * 0.32 * inch, ln)

    # primary QR again
    qr_size = 2.4 * inch
    qx = (PAGE_W - qr_size) / 2
    qy = 1.6 * inch
    rounded_rect(c, qx - 10, qy - 10, qr_size + 20, qr_size + 20, r=10, fill=white, stroke=HERO, sw=2)
    c.drawImage(str(QRS / "book-calendly.png"), qx, qy, width=qr_size, height=qr_size, mask="auto")
    c.setFillColor(HERO)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(PAGE_W / 2, qy - 0.35 * inch, "PRIMARY · Book Nathan")
    draw_footer(c, "STACK CONVERT", page_no)
    c.showPage()


def build_convert_pdf(path: Path):
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setTitle("SettleUp Collections Conversion Leavebehind — Brainstorm 2026 Denver")
    c.setAuthor("SettleUp Collections / Platter Analytics")
    convert_cover(c)
    convert_copy(c)
    convert_screenshot_recall(c)
    n = len(CONVERT_LINKS)
    for i, (title, why, url, slug, primary) in enumerate(CONVERT_LINKS, start=1):
        convert_qr_card(c, title, why, url, slug, primary, page_no=3 + i, index=i, total=n)
    convert_close(c, page_no=4 + n)
    c.save()
    print("wrote", path)


def build_convert_2up(path: Path):
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setTitle("SettleUp Collections Conversion Leavebehind 2-up")
    draw_bg(c)
    rounded_rect(c, 0.5 * inch, PAGE_H - 1.1 * inch, PAGE_W - 1.0 * inch, 0.55 * inch, r=8, fill=HexColor("#3a2e12"), stroke=HERO)
    c.setFillColor(HERO)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 0.88 * inch, "STACK CONVERT 2-UP CUTS  ·  CONVERSION pile  ·  cut on dashed midline")
    c.setFillColor(TEXT)
    c.setFont("Helvetica", 11)
    y = PAGE_H - 1.6 * inch
    for ln in [
        "Print color, US Letter, 100% scale, single-sided, 80-110 lb cardstock.",
        "This is the CONVERSION stack (Calendly + SettleUp). Keep separate from DEMO ONLY.",
        "Primary CTA is Book Nathan (calendly.com/nathanplatter).",
    ]:
        c.drawString(0.6 * inch, y, ln)
        y -= 0.28 * inch
    draw_footer(c, "STACK CONVERT 2-UP")
    c.showPage()

    links = list(CONVERT_LINKS)
    for i in range(0, len(links), 2):
        pair = links[i : i + 2]
        draw_bg(c)
        half_h = PAGE_H / 2
        for idx, item in enumerate(pair):
            title, why, url, slug, primary = item
            band_bottom = half_h if idx == 0 else 0
            band_top = PAGE_H if idx == 0 else half_h
            margin = 0.45 * inch
            tag_y = band_top - 0.45 * inch
            c.setFillColor(HERO if primary else ACCENT)
            c.setFont("Helvetica-Bold", 8)
            tag = "PRIMARY · BOOK NATHAN" if primary else "STACK CONVERT · QR"
            c.drawString(margin, tag_y, tag)
            c.setFillColor(TEXT)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(margin, tag_y - 0.28 * inch, title[:42])
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 9)
            c.drawString(margin, tag_y - 0.48 * inch, why)
            qr_size = 1.85 * inch
            qx = PAGE_W - margin - qr_size - 0.1 * inch
            qy = band_bottom + 0.55 * inch
            c.setFillColor(white)
            c.roundRect(qx - 6, qy - 6, qr_size + 12, qr_size + 12, 6, fill=1, stroke=0)
            c.drawImage(str(QRS / f"{slug}.png"), qx, qy, width=qr_size, height=qr_size, mask="auto")
            c.setFillColor(ACCENT)
            c.setFont("Helvetica", 7)
            url_y = tag_y - 0.75 * inch
            for ul in wrap_text(c, url, "Helvetica", 7, PAGE_W - qr_size - 1.3 * inch):
                c.drawString(margin, url_y, ul)
                url_y -= 0.14 * inch
        c.setStrokeColor(MUTED)
        c.setDash(3, 3)
        c.setLineWidth(0.8)
        c.line(0.4 * inch, half_h, PAGE_W - 0.4 * inch, half_h)
        c.setDash()
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7)
        c.drawCentredString(PAGE_W / 2, half_h + 3, "✂ cut")
        draw_footer(c, "STACK CONVERT 2-UP")
        c.showPage()
    c.save()
    print("wrote", path)


def main():
    ensure_qrs()
    build_demo_pdf(ROOT / "SettleUp-DisputeQueue-Demo-ONLY.pdf")
    build_demo_2up(ROOT / "SettleUp-DisputeQueue-Demo-ONLY-2up.pdf")
    build_convert_pdf(ROOT / "SettleUp-Collections-Conversion-Leavebehind.pdf")
    build_convert_2up(ROOT / "SettleUp-Collections-Conversion-Leavebehind-2up.pdf")
    print("QR count:", len(list(QRS.glob("*.png"))))


if __name__ == "__main__":
    main()
