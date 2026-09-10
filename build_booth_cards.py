#!/usr/bin/env python3
"""Rebuild Stack A QR cardstock + 2-up without public list prices."""
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
QRS = ROOT / "qrs"
PAGE_W, PAGE_H = letter

BG = HexColor("#0f1419")
PANEL = HexColor("#1a2332")
BORDER = HexColor("#2a3544")
TEXT = HexColor("#e7ecf3")
MUTED = HexColor("#8b9bb4")
ACCENT = HexColor("#5b9fd4")
YES = HexColor("#3ecf8e")
HERO = HexColor("#f0a020")
WARN = HexColor("#fbbf24")

FOOT = "Brainstorm 2026 Denver  ·  Platter Analytics  ·  Book 20 min  ·  calendly.com/nathanplatter"
FOOT_2UP = "Brainstorm 2026 Denver · Platter Analytics · Book 20 min · Cut on dashed line"

CARDS = [
    {
        "tag": "PRIMARY",
        "title": "Book a 20-minute discovery",
        "kicker": "PRIMARY AISLE CARD",
        "url": "calendly.com/nathanplatter",
        "qr": "book-calendly.png",
        "scan": "Scan to open Calendly",
        "why": [
            "Walk the refuse gate on your dispute stack - not a brochure tour.",
            "Proof already in: model $1,000 vs ledger $20,370.53 · refused.",
            "Book 20 minutes. Prices after a real intro. Do not aisle-buy.",
            "Nathan Platter · Principal, Analytics & AI | Revenue & GTM Intelligence.",
            "Investment frame: capacity you can defend after send.",
        ],
    },
    {
        "tag": "DEMO",
        "title": "Open the refused-letter demo",
        "kicker": "LIVE DEMO",
        "url": "nathanplatteruser.github.io/dispute-agent-demo/DEMO-OUTPUT.html",
        "qr": "demo-letter.png",
        "scan": "Scan to open letter demo",
        "why": [
            "Public DEMO-OUTPUT - the one letter out of 300 we refused.",
            "Run stats: 300 drafted / 20 blocked / 19 remediated / 1 hard refuse.",
            "Thesis: refuse over hallucinate. Wrong dollars don't leave.",
            "No login. Phone or laptop. Show the mismatch strip first.",
            "Then book discovery. Do not aisle-buy Firm cold.",
        ],
    },
    {
        "tag": "RADAR",
        "title": "People board · Brainstorm 2026",
        "kicker": "CONFERENCE RADAR",
        "url": "nathanplatteruser.github.io/brainstorm-2026-radar/",
        "qr": "radar.png",
        "scan": "Scan to open SettleUp radar",
        "why": [
            "Fit + priority radar for aisle targeting between demos.",
            "Phone-first. Use after the refuse wow - not instead of it.",
            "Book 20 minutes for Pilot / Firm / Audit / Desk.",
            "Prices after a real intro. No public list prices on this card.",
            "Platter Analytics / SettleUp Collections.",
        ],
    },
    {
        "tag": "PRICING",
        "title": "Pilot · Firm · Letter Risk Audit · Desk",
        "kicker": "PRICING AFTER INTRO",
        "url": "nathanplatteruser.github.io/settleup-booth-kit/#pricing",
        "qr": "pricing.png",
        "scan": "Scan to book a price conversation",
        "why": [
            "Book 20 minutes. Prices after a real intro.",
            "Named paths only. No aisle swipe prices. No Stripe on this card.",
            "Audit is the short, dense one-time. Desk is stay-on-the-desk.",
            "ROI frame: defendable capacity, not a cost-center AI toy.",
            "Scan for the booth kit intro, then book Calendly.",
        ],
    },
    {
        "tag": "ASK",
        "title": "Who owns letter risk before send?",
        "kicker": "CONVERSATION CARD",
        "url": "calendly.com/nathanplatter",
        "qr": "book-calendly.png",
        "scan": "Scan to book discovery",
        "why": [
            "Compliant tone is not ledger truth. Echoed complaint dollars ship risk.",
            "Ask: who signs the stop when the model is wrong?",
            "Our gate: check, one remediation, loud refuse.",
            "Proof: $1,000 vs $20,370.53 · 300 / 20 / 19 / 1.",
            "Scan to book 20 minutes. Bring your send path.",
        ],
    },
    {
        "tag": "SESSION",
        "title": "Session proof card · refuse live",
        "kicker": "FACILITATOR / SESSION",
        "url": "calendly.com/nathanplatter",
        "qr": "book-calendly.png",
        "scan": "Scan to book · facilitator CTA",
        "why": [
            "Hook: \"Model wrote a thousand. Ledger says twenty. We didn't send it.\"",
            "Stats: 300 drafted / 20 blocked / 19 remediated / 1 refuse.",
            "Soft close: book discovery or send the refuse pack tonight.",
            "Never open mega-nav marketing as the demo surface.",
            "Scan Calendly. Capture name, firm, role, one pain.",
        ],
    },
]


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


def draw_bg(c):
    c.setFillColor(BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)


def draw_footer(c, text, page_no=None):
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(0.55 * inch, 0.38 * inch, text)
    if page_no is not None:
        c.drawRightString(PAGE_W - 0.55 * inch, 0.38 * inch, page_no)


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


def brand_header(c, tag):
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.55 * inch, PAGE_H - 0.62 * inch, "SettleUp")
    c.setFillColor(ACCENT)
    c.drawString(1.85 * inch, PAGE_H - 0.62 * inch, "Collections")
    c.setFillColor(YES)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(0.55 * inch, PAGE_H - 0.82 * inch, "REFUSE OVER HALLUCINATE")
    rounded_rect(
        c,
        PAGE_W - 2.35 * inch,
        PAGE_H - 0.85 * inch,
        1.8 * inch,
        0.36 * inch,
        r=8,
        fill=HexColor("#3a2e12") if tag in ("PRIMARY", "PRICING") else PANEL,
        stroke=HERO if tag in ("PRIMARY", "PRICING") else BORDER,
    )
    c.setFillColor(HERO if tag in ("PRIMARY", "PRICING") else ACCENT)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(PAGE_W - 1.45 * inch, PAGE_H - 0.73 * inch, tag)


def cover_page(c):
    draw_bg(c)
    brand_header(c, "COVER")
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(0.55 * inch, PAGE_H - 1.55 * inch, "SettleUp Brainstorm")
    c.drawString(0.55 * inch, PAGE_H - 1.95 * inch, "QR Cardstock Stack")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    c.drawString(0.55 * inch, PAGE_H - 2.35 * inch, "US Letter · portrait · one QR card per page · Brainstorm 2026 Denver")

    y = PAGE_H - 2.9 * inch
    rounded_rect(c, 0.55 * inch, y - 3.35 * inch, PAGE_W - 1.1 * inch, 3.5 * inch, r=12, fill=PANEL, stroke=BORDER)
    lines = [
        "Print COLOR (not B&W). Dark background is intentional.",
        "Paper: 80-110 lb cardstock OR glossy cover stock.",
        "Do NOT scale / fit to page. Actual size / 100%.",
        "Single-sided. One card per letter page (standee-ready).",
        "Optional: light trim to 5x7 or keep full letter for table stands.",
        "Also print SettleUp-QR-2up-cut.pdf for scissors cut cards.",
        "Cut marks optional. Center QR is the target; keep URL readable.",
        "Qty suggestion: 25-40 of Book/Calendly as primary aisle;",
        "  10-15 each of demo, radar, pricing, letter-risk, facilitator.",
        "Brand: Platter Analytics / SettleUp Collections",
        "No public list prices on these cards. Book 20 minutes.",
        "Prices after a real intro. Refuse-fixture $1,000 vs $20,370.53 stays.",
    ]
    c.setFillColor(TEXT)
    c.setFont("Helvetica", 11)
    yy = y - 0.28 * inch
    for ln in lines:
        c.drawString(0.75 * inch, yy, ln)
        yy -= 0.24 * inch
    draw_footer(c, FOOT, "COVER")
    c.showPage()


def card_page(c, card, index, total):
    draw_bg(c)
    brand_header(c, card["tag"])
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 22)
    y = PAGE_H - 1.35 * inch
    for ln in wrap_text(c, card["title"], "Helvetica-Bold", 22, PAGE_W - 1.2 * inch):
        c.drawString(0.55 * inch, y, ln)
        y -= 0.32 * inch
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.55 * inch, y - 0.02 * inch, card["kicker"])

    qr_size = 2.7 * inch
    qx = (PAGE_W - qr_size) / 2
    qy = y - 0.45 * inch - qr_size
    rounded_rect(c, qx - 12, qy - 12, qr_size + 24, qr_size + 24, r=12, fill=white, stroke=HERO if card["tag"] == "PRIMARY" else BORDER, sw=2 if card["tag"] == "PRIMARY" else 1)
    c.drawImage(str(QRS / card["qr"]), qx, qy, width=qr_size, height=qr_size, mask="auto")

    c.setFillColor(ACCENT)
    c.setFont("Helvetica", 9)
    uy = qy - 0.32 * inch
    for ul in wrap_text(c, card["url"], "Helvetica", 9, PAGE_W - 1.4 * inch):
        c.drawCentredString(PAGE_W / 2, uy, ul)
        uy -= 0.16 * inch
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(PAGE_W / 2, uy - 0.04 * inch, card["scan"])

    box_top = uy - 0.28 * inch
    box_h = 2.05 * inch
    rounded_rect(c, 0.55 * inch, box_top - box_h, PAGE_W - 1.1 * inch, box_h, r=10, fill=PANEL, stroke=BORDER)
    c.setFillColor(HERO)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.75 * inch, box_top - 0.28 * inch, "Why scan")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    yy = box_top - 0.52 * inch
    for ln in card["why"]:
        c.drawString(0.75 * inch, yy, ln)
        yy -= 0.22 * inch

    draw_footer(c, FOOT, f"{index}/{total}")
    c.showPage()


def build_cardstock(path: Path):
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setTitle("SettleUp Brainstorm QR Cardstock")
    c.setAuthor("SettleUp Collections / Platter Analytics")
    cover_page(c)
    n = len(CARDS)
    for i, card in enumerate(CARDS, start=1):
        card_page(c, card, i, n)
    c.save()
    print("wrote", path)


def two_up_cover(c):
    draw_bg(c)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(0.55 * inch, PAGE_H - 1.2 * inch, "SettleUp QR · 2-up cut sheets")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12)
    y = PAGE_H - 1.7 * inch
    for ln in [
        "Print COLOR · 80-110 lb cardstock · Actual size 100% · single-sided.",
        "Each page = 2 cards. Cut on the dashed midline.",
        "Same six cards as the full-letter stack (no cover in cut count).",
        "Tell clerk: color, cardstock, do not scale, cut on dashes optional.",
        "No public list prices. Book 20 minutes. Prices after a real intro.",
    ]:
        c.drawString(0.55 * inch, y, ln)
        y -= 0.28 * inch
    draw_footer(c, FOOT, "2UP COVER")
    c.showPage()


def two_up_half(c, card, band_bottom, band_top):
    margin = 0.45 * inch
    tag_y = band_top - 0.42 * inch
    c.setFillColor(HERO if card["tag"] in ("PRIMARY", "PRICING") else ACCENT)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin, tag_y, f"SettleUp Collections  ·  {card['tag']}")
    c.setFillColor(YES)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(margin, tag_y - 0.16 * inch, "REFUSE OVER HALLUCINATE")
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margin, tag_y - 0.42 * inch, card["title"][:48])
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    yy = tag_y - 0.64 * inch
    for ln in card["why"][:4]:
        for wrapped in wrap_text(c, ln, "Helvetica", 8, PAGE_W - 3.5 * inch):
            c.drawString(margin, yy, wrapped)
            yy -= 0.14 * inch
    qr_size = 1.7 * inch
    qx = PAGE_W - margin - qr_size - 0.08 * inch
    qy = band_bottom + 0.55 * inch
    c.setFillColor(white)
    c.roundRect(qx - 6, qy - 6, qr_size + 12, qr_size + 12, 6, fill=1, stroke=0)
    c.drawImage(str(QRS / card["qr"]), qx, qy, width=qr_size, height=qr_size, mask="auto")
    c.setFillColor(ACCENT)
    c.setFont("Helvetica", 7)
    url_y = yy - 0.08 * inch
    for ul in wrap_text(c, card["url"], "Helvetica", 7, PAGE_W - qr_size - 1.4 * inch):
        c.drawString(margin, url_y, ul)
        url_y -= 0.12 * inch


def build_2up(path: Path):
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setTitle("SettleUp QR 2-up cut")
    two_up_cover(c)
    half_h = PAGE_H / 2
    for i in range(0, len(CARDS), 2):
        pair = CARDS[i : i + 2]
        draw_bg(c)
        for idx, card in enumerate(pair):
            band_bottom = half_h if idx == 0 else 0
            band_top = PAGE_H if idx == 0 else half_h
            two_up_half(c, card, band_bottom, band_top)
        c.setStrokeColor(MUTED)
        c.setDash(3, 3)
        c.setLineWidth(0.8)
        c.line(0.4 * inch, half_h, PAGE_W - 0.4 * inch, half_h)
        c.setDash()
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7)
        c.drawCentredString(PAGE_W / 2, half_h + 3, "cut")
        draw_footer(c, FOOT_2UP)
        c.showPage()
    c.save()
    print("wrote", path)


def stack_b_pricing_page(path: Path):
    """One-page STACK B pricing card: book first, no list prices."""
    import qrcode

    qr_path = ROOT / "demo-assets" / "qrs" / "pricing-pages.png"
    url = "https://nathanplatteruser.github.io/settleup-booth-kit/#pricing"
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(qr_path)

    c = canvas.Canvas(str(path), pagesize=letter)
    draw_bg(c)
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.55 * inch, PAGE_H - 0.62 * inch, "SettleUp")
    c.setFillColor(ACCENT)
    c.drawString(1.85 * inch, PAGE_H - 0.62 * inch, "Collections")
    c.setFillColor(HERO)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.55 * inch, PAGE_H - 0.84 * inch, "STACK B  ·  Demo Assets")
    c.setFillColor(YES)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(0.55 * inch, PAGE_H - 1.04 * inch, "REFUSE OVER HALLUCINATE")

    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(0.55 * inch, PAGE_H - 1.5 * inch, "Pricing")
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.55 * inch, PAGE_H - 1.78 * inch, "BOOK 20 MINUTES  ·  PRICES AFTER A REAL INTRO")

    rounded_rect(c, 0.55 * inch, PAGE_H - 2.28 * inch, PAGE_W - 1.1 * inch, 0.32 * inch, r=6, fill=HexColor("#3a2e12"), stroke=HERO)
    c.setFillColor(WARN)
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 2.18 * inch, "STACK B  ·  Demo Assets (not primary aisle Calendly)")

    qr_size = 2.7 * inch
    qx = (PAGE_W - qr_size) / 2
    qy = PAGE_H - 2.55 * inch - qr_size
    rounded_rect(c, qx - 12, qy - 12, qr_size + 24, qr_size + 24, r=12, fill=white, stroke=BORDER)
    c.drawImage(str(qr_path), qx, qy, width=qr_size, height=qr_size, mask="auto")
    c.setFillColor(ACCENT)
    c.setFont("Helvetica", 9)
    c.drawCentredString(PAGE_W / 2, qy - 0.32 * inch, "nathanplatteruser.github.io/settleup-booth-kit/#pricing")
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(PAGE_W / 2, qy - 0.52 * inch, "Scan to open · human-readable URL above")

    rounded_rect(c, 0.55 * inch, 1.05 * inch, PAGE_W - 1.1 * inch, 1.7 * inch, r=10, fill=PANEL, stroke=BORDER)
    c.setFillColor(HERO)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.75 * inch, 2.45 * inch, "Why scan")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    yy = 2.18 * inch
    for ln in [
        "Book 20 minutes. Prices after a real intro.",
        "No public list prices on this card. No Stripe.",
        "Pilot / Firm / Audit / Desk are named paths, not aisle swipe prices.",
        "After refuse story, not before.",
    ]:
        c.drawString(0.75 * inch, yy, ln)
        yy -= 0.22 * inch
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(0.55 * inch, 0.38 * inch, "Brainstorm 2026 Denver · Platter Analytics · STACK B · Demo Assets")
    c.drawRightString(PAGE_W - 0.55 * inch, 0.38 * inch, "6/15")
    c.save()


def stack_b_2up_pricing_sheet(path: Path, original_2up: Path):
    """Rebuild the 2-up sheet that holds the pricing half (page 4)."""
    # Keep the Polsia-home half copy (no list prices) and rewrite the pricing half.
    import qrcode

    home_qr = ROOT / "demo-assets" / "qrs" / "booth-kit.png"
    price_qr = ROOT / "demo-assets" / "qrs" / "pricing-pages.png"
    # home half on this sheet is still the Polsia mirror in the original file.
    # We only change the pricing half URL/copy; keep the top card as-is by
    # stamping a dark panel over the bottom half from a freshly drawn sheet
    # that matches STACK B style for both halves without list prices.

    c = canvas.Canvas(str(path), pagesize=letter)
    draw_bg(c)
    half_h = PAGE_H / 2
    halves = [
        {
            "lane": "POLSIA / LIVE",
            "title": "Polsia mirror home",
            "sub": "settleupcollections.polsia.io",
            "url": "settleupcollections.polsia.io/",
            "why": "Mirror of the live SettleUp app.",
            "n": "5/15",
            "qr": None,
        },
        {
            "lane": "PRICING INTRO",
            "title": "Pricing",
            "sub": "Book 20 minutes. Prices after a real intro.",
            "url": "nathanplatteruser.github.io/settleup-booth-kit/#pricing",
            "why": "No public list prices. After refuse story, not before.",
            "n": "6/15",
            "qr": str(price_qr),
        },
    ]
    # Generate a QR for the polsia URL so the top half stays scannable.
    polsia_tmp = ROOT / "demo-assets" / "qrs" / "_polsia-home-tmp.png"
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
    qr.add_data("https://settleupcollections.polsia.io/")
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(polsia_tmp)
    halves[0]["qr"] = str(polsia_tmp)

    for idx, card in enumerate(halves):
        band_bottom = half_h if idx == 0 else 0
        band_top = PAGE_H if idx == 0 else half_h
        margin = 0.45 * inch
        tag_y = band_top - 0.42 * inch
        c.setFillColor(HERO)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin, tag_y, f"SettleUp Collections  ·  {card['lane']}")
        c.setFillColor(YES)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(margin, tag_y - 0.16 * inch, "REFUSE OVER HALLUCINATE · STACK B")
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, tag_y - 0.42 * inch, card["title"])
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9)
        c.drawString(margin, tag_y - 0.62 * inch, card["sub"])
        c.setFillColor(ACCENT)
        c.setFont("Helvetica", 8)
        yy = tag_y - 0.84 * inch
        for ul in wrap_text(c, card["url"], "Helvetica", 8, PAGE_W - 3.6 * inch):
            c.drawString(margin, yy, ul)
            yy -= 0.14 * inch
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9)
        c.drawString(margin, yy - 0.06 * inch, card["why"])
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(ACCENT)
        c.drawString(margin, band_bottom + 0.42 * inch, card["n"])
        qr_size = 1.7 * inch
        qx = PAGE_W - margin - qr_size - 0.08 * inch
        qy = band_bottom + 0.55 * inch
        c.setFillColor(white)
        c.roundRect(qx - 6, qy - 6, qr_size + 12, qr_size + 12, 6, fill=1, stroke=0)
        c.drawImage(card["qr"], qx, qy, width=qr_size, height=qr_size, mask="auto")

    c.setStrokeColor(MUTED)
    c.setDash(3, 3)
    c.line(0.4 * inch, half_h, PAGE_W - 0.4 * inch, half_h)
    c.setDash()
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7)
    c.drawCentredString(PAGE_W / 2, half_h + 3, "cut")
    c.setFont("Helvetica", 8)
    c.drawString(0.55 * inch, 0.38 * inch, "Brainstorm 2026 Denver · Platter Analytics · STACK B · Demo Assets")
    c.drawRightString(PAGE_W - 0.55 * inch, 0.38 * inch, "Sheet 3/8")
    c.save()
    if polsia_tmp.exists():
        polsia_tmp.unlink()


def replace_pdf_page(src: Path, dest: Path, page_index: int, replacement: Path):
    reader = PdfReader(str(src))
    repl = PdfReader(str(replacement))
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        writer.add_page(repl.pages[0] if i == page_index else page)
    writer.write(str(dest))
    print("patched", dest, "page", page_index + 1)


def patch_stack_b():
    tmp_dir = ROOT / "demo-assets" / "_tmp_price_lock"
    tmp_dir.mkdir(exist_ok=True)
    page7 = tmp_dir / "stackb-page7.pdf"
    sheet3 = tmp_dir / "stackb-2up-sheet3.pdf"
    stack_b_pricing_page(page7)
    stack_b_2up_pricing_sheet(sheet3, ROOT / "demo-assets" / "SettleUp-DemoAssets-QR-2up-cut.pdf")
    replace_pdf_page(
        ROOT / "demo-assets" / "SettleUp-DemoAssets-QR-Cardstock.pdf",
        ROOT / "demo-assets" / "SettleUp-DemoAssets-QR-Cardstock.pdf",
        6,
        page7,
    )
    replace_pdf_page(
        ROOT / "demo-assets" / "SettleUp-DemoAssets-QR-2up-cut.pdf",
        ROOT / "demo-assets" / "SettleUp-DemoAssets-QR-2up-cut.pdf",
        3,
        sheet3,
    )
    for p in tmp_dir.iterdir():
        p.unlink()
    tmp_dir.rmdir()


def main():
    build_cardstock(ROOT / "SettleUp-Brainstorm-QR-Cardstock.pdf")
    build_2up(ROOT / "SettleUp-QR-2up-cut.pdf")
    patch_stack_b()


if __name__ == "__main__":
    main()
