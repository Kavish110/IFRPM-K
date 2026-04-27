from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

OUTPUT = "/Users/jalpatel/College/Spring2026/IFRPM/IFRPM_Quad_Chart.pdf"

# ── Palette ────────────────────────────────────────────────────────────────
DARK_BLUE  = colors.HexColor("#1B3A6B")
MID_BLUE   = colors.HexColor("#2E5FA3")
DARK_RED   = colors.HexColor("#8B1A1A")
DARK_GREEN = colors.HexColor("#2E6B45")
ACCENT     = colors.HexColor("#F4A300")
WHITE      = colors.white
TEXT_DARK  = colors.HexColor("#1A1A2E")
DIVIDER    = colors.HexColor("#B0BEC5")

# Quadrant backgrounds (light tints)
BG_TL = colors.HexColor("#EAF1FB")  # soft blue-white  – Accomplishments
BG_TR = colors.HexColor("#E3EFF9")  # light sky-blue   – Next Tasks
BG_BL = colors.HexColor("#FDF0F0")  # soft rose-white  – Risks
BG_BR = colors.HexColor("#EDF7F1")  # light mint-green – Plan

W, H = landscape(letter)   # 792 × 612 pt

MARGIN   = 18
TITLE_H  = 36
FOOTER_H = 18
GAP      = 3

QW = (W - 2*MARGIN - GAP) / 2
QH = (H - 2*MARGIN - TITLE_H - FOOTER_H - GAP) / 2

TOP    = MARGIN + FOOTER_H + GAP + QH
BOTTOM = MARGIN + FOOTER_H
LEFT   = MARGIN
RIGHT  = MARGIN + QW + GAP

HEADER_H = 22
PAD      = 8
LH       = 9.5   # normal line height
LH_SM    = 8.5   # small line height


# ── Drawing helpers ────────────────────────────────────────────────────────

def draw_quad(c, x, y, w, h, header_text, header_color, bg_color, content_fn):
    # Background
    c.setFillColor(bg_color)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=0)

    # Header bar
    c.setFillColor(header_color)
    c.roundRect(x, y+h-HEADER_H, w, HEADER_H, 6, fill=1, stroke=0)
    c.rect(x, y+h-HEADER_H, w, HEADER_H/2, fill=1, stroke=0)  # square bottom corners

    # Border
    c.setStrokeColor(header_color)
    c.setLineWidth(1.5)
    c.roundRect(x, y, w, h, 6, fill=0, stroke=1)

    # Header text
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + PAD, y + h - HEADER_H + 6, header_text)

    content_fn(c, x + PAD, y + h - HEADER_H - PAD, w - 2*PAD)


def section_label(c, x, y, text, color=DARK_BLUE):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x, y, text)
    return y - LH - 1


def wrap_text(c, x, y, text, max_w, font="Helvetica", size=7.5, indent=0, color=TEXT_DARK):
    """Draw wrapped text, return new y."""
    c.setFillColor(color)
    c.setFont(font, size)
    words = text.split()
    line = ""
    bx = x + indent
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, font, size) <= max_w - indent:
            line = test
        else:
            c.drawString(bx, y, line)
            y -= LH_SM
            line = word
    if line:
        c.drawString(bx, y, line)
    return y - LH_SM


def bullet(c, x, y, text, w, size=7.5, indent=8, color=TEXT_DARK):
    c.setFillColor(color)
    c.setFont("Helvetica", size)
    c.drawString(x + indent - 6, y, "\u2022")
    return wrap_text(c, x, y, text, w, size=size, indent=indent, color=color)


def person_row(c, x, y, name, role, text, w):
    """One-liner row: Name (bold) | Role (italic) | text."""
    c.setFillColor(DARK_BLUE)
    c.setFont("Helvetica-Bold", 7.5)
    nw = c.stringWidth(name + "  ", "Helvetica-Bold", 7.5)
    c.drawString(x + 8, y, name)

    c.setFillColor(colors.HexColor("#555577"))
    c.setFont("Helvetica-Oblique", 7)
    rw = c.stringWidth(role + "  ", "Helvetica-Oblique", 7)
    c.drawString(x + 8 + nw, y, role)

    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica", 7.5)
    return wrap_text(c, x, y - LH_SM, text, w, size=7.5, indent=8, color=TEXT_DARK)


def badge(c, x, y, text, bg=ACCENT, fg=WHITE, size=6.5):
    """Small colored badge."""
    tw = c.stringWidth(text, "Helvetica-Bold", size) + 8
    c.setFillColor(bg)
    c.roundRect(x, y - 1, tw, 10, 2, fill=1, stroke=0)
    c.setFillColor(fg)
    c.setFont("Helvetica-Bold", size)
    c.drawString(x + 4, y + 1, text)
    return tw


# ── Quadrant content ───────────────────────────────────────────────────────

def tl_content(c, x, y, w):
    """Top-Left: Latest Accomplishments"""

    # ── Phase status overview — 3 columns ─────────────────────────────────
    col_w = (w - 8) / 3

    def phase_block(bx, by, bw, phase_label, sub, status_col, tasks):
        bh = len(tasks) * LH_SM + 28
        c.setFillColor(colors.HexColor("#FFFFFF"))
        c.roundRect(bx, by - bh, bw, bh, 4, fill=1, stroke=0)
        c.setStrokeColor(status_col)
        c.setLineWidth(1)
        c.roundRect(bx, by - bh, bw, bh, 4, fill=0, stroke=1)
        # Phase label
        c.setFillColor(status_col)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawString(bx + 4, by - 10, phase_label)
        # Done badge
        badge(c, bx + bw - 34, by - 11, "\u2713 DONE", bg=colors.HexColor("#2E6B45"), size=6)
        # Sub label
        c.setFillColor(colors.HexColor("#444466"))
        c.setFont("Helvetica-Oblique", 6)
        c.drawString(bx + 4, by - 20, sub)
        ty = by - 30
        for t in tasks:
            c.setFillColor(TEXT_DARK)
            c.setFont("Helvetica", 6)
            # wrap within block
            words = t.split()
            line = ""
            lx = bx + 9
            for word in words:
                test = (line + " " + word).strip()
                if c.stringWidth(test, "Helvetica", 6) <= bw - 13:
                    line = test
                else:
                    c.drawString(lx, ty, "\u2022 " + line if line == t.split()[0] else line)
                    ty -= LH_SM - 1
                    line = word
            if line:
                prefix = "\u2022 " if not any(c2.drawString for c2 in []) else ""
                c.drawString(lx, ty, "\u2022 " + line)
            ty -= LH_SM
        return ty

    block_h = 4 * LH_SM + 28

    phase_block(x,                  y, col_w,
        "Phase 1 — Problem Framing", "Sequential",
        DARK_BLUE,
        ["Defined IFRPM scope & objectives",
         "Selected NGAFID, CMAPSS, PCoE datasets",
         "Set eval metrics: RMSE, MAE, F1",
         "Laid out 9-phase architecture"])

    phase_block(x + col_w + 4,     y, col_w,
        "Phase 2 — Data Eng. + Backend", "Parallel tracks",
        MID_BLUE,
        ["Data: all 4 datasets \u2192 CSV/PKL",
         "Infra: FastAPI backend built",
         "DB schema + risk scoring live",
         "Weather API integrated"])

    phase_block(x + 2*(col_w + 4), y, col_w,
        "Phase 3 — Feature Engineering", "Parallel w/ Phase 2",
        colors.HexColor("#6A3FA0"),
        ["Rolling stats & trend slopes",
         "Composite Health Index (0\u20131)",
         "Sensor normalization pipeline",
         "Feature store committed to repo"])

    y -= block_h + 6

    # Divider
    c.setStrokeColor(DIVIDER)
    c.setLineWidth(0.5)
    c.line(x, y + 2, x + w, y + 2)
    y -= 8

    # ── Per-person one-liners ──────────────────────────────────────────────
    c.setFillColor(DARK_BLUE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x, y, "Team Contributions (Phases 2 & 3)")
    y -= LH + 1

    rows = [
        ("Jal",        "Backend",          "FastAPI backend, DB schema, risk scoring, weather API, feature engineering utils & health index  [Infra + Ph.3]"),
        ("Kavish",     "Data Eng.",        "Cleaned NGAFID aviation maintenance logs \u2192 CSV + PKL (2,019 records)  [Data track]"),
        ("Deveshree",  "Data Eng.",        "Merged NASA CMAPSS sensor data with RUL labels across all 4 sub-datasets  [Data track]"),
        ("Prem",       "Data Eng.",        "Structured NASA battery degradation cycles into RUL-ready feature files (2,771 rows)  [Data track]"),
        ("Hrishikesh", "Maint. Analytics", "Processed capacitor EIS + transient stress data; completed degradation EDA notebook  [Data track]"),
    ]

    for name, role, text in rows:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 1, y, "\u25cf")

        c.setFillColor(DARK_BLUE)
        c.setFont("Helvetica-Bold", 7.5)
        nw = c.stringWidth(name + "  ", "Helvetica-Bold", 7.5)
        c.drawString(x + 10, y, name)

        c.setFillColor(colors.HexColor("#555577"))
        c.setFont("Helvetica-Oblique", 6.5)
        c.drawString(x + 10 + nw, y, "(" + role + ")")

        y -= LH_SM + 1
        y = wrap_text(c, x, y, text, w, size=7, indent=10, color=TEXT_DARK)
        y -= 1


def tr_content(c, x, y, w):
    """Top-Right: Next Major Tasks & Owners"""
    y = section_label(c, x, y, "Phase 4 — RUL Model Development  (Week 5–7)", MID_BLUE)
    y = bullet(c, x, y, "Baseline regression models (RF, XGBoost) for benchmarking  — TM-B", w)
    y = bullet(c, x, y, "LSTM / GRU temporal degradation models  — TM-B", w)
    y = bullet(c, x, y, "SHAP explainability + cross-unit validation  — TM-B + TM-C", w)
    y -= 4

    y = section_label(c, x, y, "Phase 5 — Maintenance Risk Scoring  (Week 8)", MID_BLUE)
    y = bullet(c, x, y, "Map RUL predictions to CRITICAL / HIGH / MEDIUM / LOW bands  — TM-C", w)
    y = bullet(c, x, y, "Configurable threshold-based alert trigger logic  — TM-D", w)
    y -= 4

    y = section_label(c, x, y, "Phase 7 — Frontend Dashboard  (Week 8–9)", MID_BLUE)
    y = bullet(c, x, y, "Fleet-wide health overview + component RUL charts  — TM-E", w)
    y = bullet(c, x, y, "Alert panel, degradation plots, weather impact view  — TM-E", w)


def bl_content(c, x, y, w):
    """Bottom-Left: Risks / Barriers"""
    risks = [
        ("Data Heterogeneity",
         "Simulated engine data, real flight logs & component stress tests cannot be merged — requires separate per-dataset modeling pipelines"),
        ("Sparse Maintenance Labels",
         "NGAFID maintenance events are rare vs. total flight records — risk of class imbalance and biased models; mitigation: oversampling + anomaly detection"),
        ("Large Data Volume",
         "Time-series flight logs increase preprocessing time; mitigation: serialized PKL format, batched dataloaders"),
        ("Dataset Alignment",
         "Different sensors, time scales, and failure definitions across datasets; mitigation: conceptual feature mapping instead of raw data merging"),
    ]
    for title, desc in risks:
        c.setFillColor(DARK_RED)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(x + 2, y, "\u26a0  " + title)
        y -= LH_SM + 1
        y = wrap_text(c, x, y, desc, w, size=7, indent=10,
                      color=colors.HexColor("#5A1010"))
        y -= 3


def br_content(c, x, y, w):
    """Bottom-Right: Remaining Activities & Plan"""
    phases = [
        ("Phase 4",  "RUL Model Development",            "Baseline \u2192 LSTM/GRU \u2192 Transformer; SHAP explainability",          "Wks 5\u20137"),
        ("Phase 5",  "Risk Scoring Engine",              "RUL → maintenance urgency bands + configurable alert triggers",    "Wk 8"),
        ("Phase 6",  "Backend Completion",               "Plug trained models into inference endpoints; integration testing", "Wk 8"),
        ("Phase 7",  "Frontend Dashboard",               "Fleet health views, RUL charts, alert panel, weather indicators",  "Wks 8–9"),
        ("Phase 8",  "Validation & Stress Testing",      "Simulated failure scenarios, noise injection, latency testing",    "Wk 9"),
        ("Phase 9",  "Documentation & Final Report",     "Architecture diagrams, model results, thesis-ready report + deck", "Wk 10"),
    ]

    for phase, title, desc, timeline in phases:
        # Phase label + title
        c.setFillColor(DARK_GREEN)
        c.setFont("Helvetica-Bold", 7.5)
        label = phase + " — " + title
        c.drawString(x, y, label)

        # Timeline badge (right-aligned)
        tw = badge(c, x + w - c.stringWidth(timeline, "Helvetica-Bold", 6.5) - 12,
                   y, timeline, bg=ACCENT)
        y -= LH_SM + 1

        # Desc
        y = wrap_text(c, x, y, desc, w, size=7, indent=8,
                      color=colors.HexColor("#1A3A2A"))
        y -= 3


# ── Build PDF ──────────────────────────────────────────────────────────────

c = canvas.Canvas(OUTPUT, pagesize=landscape(letter))
c.setTitle("IFRPM Quad Chart — Status Update")

# Page white background
c.setFillColor(WHITE)
c.rect(0, 0, W, H, fill=1, stroke=0)

# Title bar
c.setFillColor(DARK_BLUE)
c.rect(MARGIN, H - MARGIN - TITLE_H, W - 2*MARGIN, TITLE_H, fill=1, stroke=0)
c.setFillColor(WHITE)
c.setFont("Helvetica-Bold", 13)
c.drawString(MARGIN + 10, H - MARGIN - TITLE_H + 11,
             "IFRPM — Intelligent Flight Reliability & Predictive Maintenance")
c.setFillColor(ACCENT)
c.setFont("Helvetica-Bold", 9)
tag = "Status Check-In  |  Spring 2026"
c.drawString(W - MARGIN - c.stringWidth(tag, "Helvetica-Bold", 9) - 10,
             H - MARGIN - TITLE_H + 11, tag)

# Footer
c.setStrokeColor(DIVIDER)
c.setLineWidth(0.5)
c.line(MARGIN, MARGIN + FOOTER_H - 4, W - MARGIN, MARGIN + FOOTER_H - 4)
c.setFillColor(colors.HexColor("#666688"))
c.setFont("Helvetica", 6.5)
c.drawString(MARGIN, MARGIN + 4, "Team IFRPM  |  github.com/jalpatel11/IFRPM")
date_str = "March 2026"
c.drawString(W - MARGIN - c.stringWidth(date_str, "Helvetica", 6.5), MARGIN + 4, date_str)

# 4 Quadrants
quad_defs = [
    (LEFT,  TOP,    "  ✓  Latest Accomplishments",       DARK_BLUE,  BG_TL, tl_content),
    (RIGHT, TOP,    "  ▶  Next Major Tasks & Owners",    MID_BLUE,   BG_TR, tr_content),
    (LEFT,  BOTTOM, "  ⚠  Risks / Barriers",             DARK_RED,   BG_BL, bl_content),
    (RIGHT, BOTTOM, "  ◎  Remaining Activities & Plan",  DARK_GREEN, BG_BR, br_content),
]

for qx, qy, header, hcol, bgcol, fn in quad_defs:
    draw_quad(c, qx, qy, QW, QH, header, hcol, bgcol, fn)

c.save()
print(f"Saved: {OUTPUT}")
