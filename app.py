#!/usr/bin/env python3
"""ELARA Value Decoder — KI-gestütztes Werte-Profil Tool"""

import streamlit as st
import anthropic
import os
import json
import io
import base64
from pathlib import Path
from itertools import combinations
import random

# ── CONSTANTS ─────────────────────────────────────────────────────────────────

MAGENTA    = "#B60B6D"
PINK       = "#EA428E"
HELLPINK   = "#FF9DCC"
SOFT_ROSA  = "#FFEBF7"
NACHTBLAU  = "#013A5B"
PERLWEISS  = "#FFFDF8"
GOLD       = "#D8B76A"
DARK       = "#1A1A1A"

COPYRIGHT = "Copyright Corinne Furch Business Mentoring | Feminine Business CODE® – Geschützte Marke"

WERTE_GRUPPEN = [
    ["Abenteuer",     "Achtsamkeit",    "Akzeptanz",      "Authentizität",  "Balance"],
    ["Begeisterung",  "Bescheidenheit", "Bewusstsein",    "Dankbarkeit",    "Disziplin"],
    ["Ehrlichkeit",   "Eigenverantwortung","Einfachheit",  "Empathie",       "Entwicklung"],
    ["Erfolg",        "Exzellenz",      "Fairness",       "Familie",        "Freiheit"],
    ["Freude",        "Frieden",        "Fürsorge",       "Geduld",         "Gelassenheit"],
    ["Gemeinschaft",  "Gerechtigkeit",  "Gesundheit",     "Glaube",         "Grosszügigkeit"],
    ["Harmonie",      "Humor",          "Individualität", "Inspiration",    "Integrität"],
    ["Intuition",     "Klarheit",       "Kompetenz",      "Kreativität",    "Leichtigkeit"],
    ["Lernen",        "Liebe",          "Loyalität",      "Mut",            "Nachhaltigkeit"],
    ["Nähe",          "Neugier",        "Offenheit",      "Ordnung",        "Passion"],
    ["Qualität",      "Respekt",        "Ruhe",           "Selbstbestimmung","Selbstvertrauen"],
    ["Sicherheit",    "Sinn",           "Spiritualität",  "Stabilität",     "Stärke"],
    ["Tiefgang",      "Toleranz",       "Transformation", "Unabhängigkeit", "Verantwortung"],
    ["Verbindung",    "Vertrauen",      "Vision",         "Wachstum",       "Wahrheit"],
    ["Weisheit",      "Wertschätzung",  "Würde",          "Zugehörigkeit",  "Zuverlässigkeit"],
    ["Anmut",         "Anerkennung",    "Ausdauer",       "Ausdruck",       "Bedeutung"],
    ["Beitrag",       "Besonnenheit",   "Charisma",       "Demut",          "Direktheit"],
    ["Effizienz",     "Einfluss",       "Eleganz",        "Entschlossenheit","Erfüllung"],
    ["Fokus",         "Fülle",          "Führung",        "Geborgenheit",   "Genuss"],
    ["Gleichgewicht", "Herzlichkeit",   "Hingabe",        "Innovation",     "Konsequenz"],
    ["Lebendigkeit",  "Luxus",          "Menschlichkeit", "Mitgefühl",      "Natürlichkeit"],
    ["Optimismus",    "Präsenz",        "Professionalität","Reife",         "Reichtum"],
    ["Selbstachtung", "Selbstliebe",    "Seriosität",     "Souveränität",   "Stille"],
    ["Struktur",      "Treue",          "Unbeschwertheit","Verbindlichkeit","Vergebung"],
    ["Verlässlichkeit","Vitalität",     "Wohlstand",      "Zartheit",       "Zielstrebigkeit"],
    ["Zufriedenheit", "Ambition",       "Aufrichtigkeit", "Autonomie",      "Brillanz"],
    ["Energie",       "Entspannung",    "Erkenntnis",     "Expertise",      "Flexibilität"],
    ["Grenzen",       "Heilung",        "Herz",           "Idealismus",     "Kraft"],
    ["Kultur",        "Leadership",     "Relevanz",       "Schönheit",      "Selbstausdruck"],
    ["Sichtbarkeit",  "Tiefe",          "Transparenz",    "Wirkung",        "Zukunft"],
    # Synonym-Erweiterungen — kreative Richtung
    ["Originalität",  "Pioniergeist",   "Schöpferkraft",  "Erfindergeist",  "Neuartigkeit"],
    # Synonym-Erweiterungen — Mut & Entscheidung
    ["Tapferkeit",    "Kühnheit",       "Risikobereitschaft", "Beherztheit","Entscheidungsstärke"],
    # Synonym-Erweiterungen — Exzellenz & Tiefe
    ["Meisterschaft", "Könnerschaft",   "Perfektion",     "Tiefenwissen",   "Handwerk"],
    # Synonym-Erweiterungen — Verbindung & Beziehung
    ["Zuneigung",     "Wärme",          "Zusammenhalt",   "Solidarität",    "Bindung"],
    # Synonym-Erweiterungen — innere Ruhe & Stärke
    ["Zentriertheit", "Contenance",     "Fassung",        "Ganzheit",       "Verwurzelung"],
]

ALLE_WERTE = [w for g in WERTE_GRUPPEN for w in g]

# Wert-Cluster: zeigt der KI welche Werte in dieselbe Richtung zeigen
WERT_CLUSTER = {
    "Kreative Entfaltung": [
        "Kreativität", "Innovation", "Ausdruck", "Selbstausdruck", "Inspiration",
        "Brillanz", "Originalität", "Pioniergeist", "Schöpferkraft", "Erfindergeist",
        "Neuartigkeit", "Fantasie",
    ],
    "Freiheit & Autonomie": [
        "Freiheit", "Unabhängigkeit", "Autonomie", "Selbstbestimmung",
        "Eigenverantwortung", "Individualität",
    ],
    "Mut & Entscheidungsstärke": [
        "Mut", "Tapferkeit", "Kühnheit", "Risikobereitschaft", "Beherztheit",
        "Entscheidungsstärke", "Entschlossenheit", "Konsequenz",
    ],
    "Verbindung & Beziehung": [
        "Verbindung", "Nähe", "Liebe", "Zuneigung", "Wärme", "Zusammenhalt",
        "Solidarität", "Bindung", "Gemeinschaft", "Zugehörigkeit", "Familie",
        "Herzlichkeit", "Fürsorge", "Mitgefühl",
    ],
    "Führung & Wirkung": [
        "Führung", "Einfluss", "Leadership", "Wirkung", "Sichtbarkeit",
        "Charisma", "Souveränität", "Ambition", "Zielstrebigkeit",
    ],
    "Wachstum & Erkenntnis": [
        "Wachstum", "Entwicklung", "Lernen", "Transformation", "Erkenntnis",
        "Neugier", "Offenheit", "Expertise", "Tiefgang", "Tiefenwissen",
    ],
    "Exzellenz & Meisterschaft": [
        "Exzellenz", "Qualität", "Meisterschaft", "Könnerschaft", "Perfektion",
        "Handwerk", "Professionalität", "Kompetenz", "Effizienz",
    ],
    "Innere Ruhe & Stärke": [
        "Ruhe", "Stille", "Frieden", "Gelassenheit", "Entspannung", "Stabilität",
        "Gleichgewicht", "Balance", "Zentriertheit", "Contenance", "Fassung",
        "Ganzheit", "Verwurzelung",
    ],
    "Integrität & Wahrheit": [
        "Integrität", "Ehrlichkeit", "Aufrichtigkeit", "Authentizität",
        "Transparenz", "Wahrheit", "Direktheit",
    ],
    "Wohlstand & Fülle": [
        "Wohlstand", "Reichtum", "Fülle", "Erfolg", "Luxus", "Genuss",
        "Lebensqualität", "Vitalität",
    ],
    "Spiritualität & Sinn": [
        "Spiritualität", "Glaube", "Sinn", "Tiefe", "Weisheit", "Ganzheit",
        "Idealismus", "Vision", "Heilung",
    ],
}

def get_wert_cluster(wert: str) -> "str | None":
    for cluster, werte in WERT_CLUSTER.items():
        if wert in werte:
            return cluster
    return None
VOUCHER_FILE = Path(__file__).parent / "elara-voucher-codes.json"


# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ELARA Value Decoder",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@400;500;600&display=swap');

* {{ font-family: 'DM Sans', sans-serif !important; }}
h1, h2, h3, .playfair {{ font-family: 'Playfair Display', serif !important; }}

.block-container {{ max-width: 740px; padding-top: 1.5rem; padding-bottom: 4rem; }}

.elara-title {{
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: {MAGENTA};
    text-align: center;
    margin-top: 0.8rem;
    margin-bottom: 0.3rem;
    padding-top: 0.4rem;
    line-height: 1.4;
    overflow: visible;
}}
.elara-sub {{
    font-size: 1rem;
    color: {NACHTBLAU};
    text-align: center;
    font-style: italic;
    margin-bottom: 2rem;
    opacity: 0.9;
}}
.phase-pill {{
    background: {MAGENTA};
    color: white;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 0.6rem;
    letter-spacing: 0.03em;
}}
.intro-box {{
    background: {SOFT_ROSA};
    border-left: 4px solid {MAGENTA};
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin: 0.8rem 0;
    line-height: 1.85;
    color: {DARK};
    font-size: 0.97rem;
}}
.celebration {{
    background: linear-gradient(135deg, {SOFT_ROSA}, {PERLWEISS});
    border: 2px solid {GOLD};
    border-radius: 16px;
    padding: 1.8rem 2rem;
    text-align: center;
    margin: 1rem 0;
}}
.value-pill {{
    display: inline-block;
    background: white;
    border: 2px solid {MAGENTA}44;
    border-radius: 20px;
    padding: 5px 16px;
    margin: 4px;
    font-size: 0.9rem;
    color: {NACHTBLAU};
    font-weight: 500;
}}
.rank-row {{
    background: {NACHTBLAU};
    color: {PERLWEISS};
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}}
.rank-num {{
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: {GOLD};
    min-width: 36px;
}}
.rank-val {{
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    font-weight: 700;
}}
.hint {{
    color: #999;
    font-size: 0.83rem;
    font-style: italic;
    text-align: center;
    margin: 0.4rem 0 0.8rem;
}}
.counter-badge {{
    background: {SOFT_ROSA};
    color: {MAGENTA};
    font-weight: 700;
    border-radius: 8px;
    padding: 4px 14px;
    font-size: 0.9rem;
    display: inline-block;
}}
.footer-copy {{
    text-align: center;
    color: #bbb;
    font-size: 0.7rem;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #eee;
}}
div.stButton > button {{
    background: {MAGENTA};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.65rem 1.8rem;
    font-weight: 600;
    font-size: 0.95rem;
    width: 100%;
    font-family: 'DM Sans', sans-serif !important;
    transition: opacity 0.2s;
}}
div.stButton > button:hover {{ opacity: 0.85; background: {MAGENTA} !important; color: white !important; }}
div.stButton > button:focus {{ box-shadow: 0 0 0 3px {HELLPINK}; }}

.compare-area div.stButton > button {{
    background: {NACHTBLAU} !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    min-height: 100px;
    padding: 1.2rem !important;
    line-height: 1.3 !important;
    white-space: normal !important;
}}
.compare-area div.stButton > button:hover {{
    background: {MAGENTA} !important;
    opacity: 1 !important;
}}
.back-btn div.stButton > button {{
    background: #f0f0f0 !important;
    color: #666 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ───────────────────────────────────────────────────────────────────

def get_header_html() -> str:
    img_path = Path(__file__).parent / "assets" / "header.png"
    if not img_path.exists():
        return ""
    img_b64 = base64.b64encode(img_path.read_bytes()).decode()
    return f"""<div style="width:100%;border-radius:14px;overflow:hidden;margin-bottom:1.8rem;">
  <img src="data:image/png;base64,{img_b64}" style="width:100%;display:block;max-height:400px;object-fit:cover;object-position:center top;">
</div>"""


def get_client():
    # Streamlit Cloud: secrets.toml / Streamlit Secrets UI
    key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
    # Lokale Entwicklung: .env
    if not key:
        key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        env = Path(__file__).parent.parent / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    return anthropic.Anthropic(api_key=key) if key else None


def load_vouchers() -> dict:
    if VOUCHER_FILE.exists():
        return json.loads(VOUCHER_FILE.read_text(encoding="utf-8"))
    return {}


def save_vouchers(data: dict):
    VOUCHER_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def check_and_use_voucher(code: str) -> tuple:
    code = code.upper().strip()
    if not code:
        return False, ""
    vouchers = load_vouchers()

    # Präfix-Codes: z.B. "ELARA-ANNA" matcht den Eintrag "ELARA-*"
    lookup = code
    if code not in vouchers:
        parts = code.split("-")
        if len(parts) >= 2:
            prefix_key = parts[0] + "-*"
            if prefix_key in vouchers:
                lookup = prefix_key
    if lookup not in vouchers:
        return False, "Dieser Code ist nicht gültig."

    v = vouchers[lookup]
    if not v.get("active", True):
        return False, "Dieser Code ist nicht mehr aktiv."
    max_uses = v.get("max_uses", 0)
    uses = v.get("uses", 0)
    if max_uses > 0 and uses >= max_uses:
        return False, "Dieser Code wurde bereits verwendet."
    vouchers[lookup]["uses"] = uses + 1
    save_vouchers(vouchers)
    return True, "Code akzeptiert."


def check_email_access(email: str) -> bool:
    """Prüft ob die E-Mail in der autorisierten Liste ist.
    Liest aus Streamlit Secrets (AUTHORIZED_EMAILS) — kommagetrennte Liste.
    Später: Google Sheet Anbindung via gspread.
    """
    email = email.strip().lower()
    if not email:
        return False
    try:
        raw = st.secrets.get("AUTHORIZED_EMAILS", "") if hasattr(st, "secrets") else ""
        if raw:
            authorized = [e.strip().lower() for e in raw.split(",") if e.strip()]
            return email in authorized
    except Exception:
        pass
    return False


def compute_top10(werte_set: set) -> list:
    ordered = [w for w in ALLE_WERTE if w in werte_set]
    return ordered


def get_pairs(n: int) -> list:
    return list(combinations(range(n), 2))


def rank_by_wins(items: list, results: list, pairs: list) -> list:
    scores = {i: 0 for i in range(len(items))}
    for r in results:
        scores[r] += 1
    ranked_idx = sorted(range(len(items)), key=lambda i: scores[i], reverse=True)
    return [items[i] for i in ranked_idx], {items[i]: scores[i] for i in range(len(items))}


def generate_direction_analysis(client, ranking: list, top10: list, name: str) -> str:
    clusters_hit = {}
    for w in top10:
        c = get_wert_cluster(w)
        if c:
            clusters_hit.setdefault(c, []).append(w)

    cluster_info = "\n".join(
        f"- {c}: {', '.join(ws)}" for c, ws in clusters_hit.items()
    )

    raw = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": f"""Du analysierst das Werteprofil von {name}.

Ihre Top 3 Kernwerte sind: {ranking[0]}, {ranking[1]}, {ranking[2]}
Ihre Top 10 Werte ordnen sich in diese Themen-Cluster ein:
{cluster_info}

Schreibe 3-4 Sätze: Welche Hauptrichtung(en) zeigen diese Werte zusammen?
Falls mehrere Werte aus demselben Cluster stammen, benenne das explizit als Kernthema.
Kein ß. Direkte du-Ansprache. Keine Floskeln. Warm, präzise, tiefgründig."""}]
    ).content[0].text.strip()
    return raw


def generate_scenario(client, va: str, vb: str, name: str) -> dict:
    raw = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=350,
        messages=[{"role": "user", "content": f"""Du hilfst {name} dabei, herauszufinden, was ihr wirklich wichtiger ist: '{va}' oder '{vb}'.

Schreibe eine kurze, konkrete Lebenssituation, in der diese zwei Werte in Konflikt geraten.
Direkte du-Ansprache. Warm und klar. Keine Wertung.

Format GENAU so (nichts weiter):

FRAGE: [Die Situation, 1-2 Sätze]
OPTION A: [Kurze Wahl für {va}]
OPTION B: [Kurze Wahl für {vb}]

Kein ß. Kein ss statt ß vergessen."""}]
    ).content[0].text.strip()

    result = {"frage": raw, "a": va, "b": vb}
    for line in raw.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            k = key.strip().upper()
            if k == "FRAGE":
                result["frage"] = val.strip()
            elif k == "OPTION A":
                result["a"] = val.strip()
            elif k == "OPTION B":
                result["b"] = val.strip()
    return result


def build_pdf(name: str, top10: list, top5: list, ranking: list) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                     Table, TableStyle, HRFlowable)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.colors import HexColor

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2*cm, bottomMargin=2.2*cm)

    M  = HexColor(MAGENTA)
    NB = HexColor(NACHTBLAU)
    SR = HexColor(SOFT_ROSA)
    G  = HexColor(GOLD)
    PW = HexColor(PERLWEISS)
    DK = HexColor(DARK)

    def style(name_, **kw):
        defaults = dict(fontName="Helvetica", fontSize=10, textColor=DK)
        defaults.update(kw)
        return ParagraphStyle(name_, **defaults)

    s_title   = style("title",  fontName="Helvetica-Bold", fontSize=22, textColor=M,  alignment=TA_CENTER, spaceAfter=4)
    s_sub     = style("sub",    fontName="Helvetica-Oblique", fontSize=11, textColor=NB, alignment=TA_CENTER, spaceAfter=6)
    s_name_   = style("name_",  fontName="Helvetica", fontSize=12, textColor=NB, alignment=TA_CENTER, spaceAfter=2)
    s_sec     = style("sec",    fontName="Helvetica-Bold", fontSize=13, textColor=NB, spaceBefore=16, spaceAfter=8)
    s_body    = style("body",   fontName="Helvetica", fontSize=10, textColor=DK, spaceAfter=3)
    s_rank_   = style("rank_",  fontName="Helvetica-Bold", fontSize=13, textColor=PW)
    s_italic  = style("ital",   fontName="Helvetica-Oblique", fontSize=10, textColor=NB,
                      alignment=TA_CENTER, spaceBefore=6, spaceAfter=12)
    s_footer  = style("foot",   fontName="Helvetica", fontSize=7.5, textColor=colors.grey, alignment=TA_CENTER)

    story = []
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("ELARA Value Decoder", s_title))
    story.append(Spacer(1, 1.0*cm))
    story.append(Paragraph("Was bleibt, wenn alles andere wegfällt – deine Werte, dein Kompass.", s_sub))
    story.append(Paragraph(f"Persönliches Werte-Profil von <b>{name}</b>", s_name_))
    story.append(HRFlowable(width="100%", thickness=2, color=M, spaceAfter=18))

    # Top 3
    story.append(Paragraph("Dein Kompass — Die 3 Kernwerte", s_sec))
    medals = ["1.", "2.", "3."]
    for i, (w, med) in enumerate(zip(ranking[:3], medals)):
        data = [[Paragraph(
            f'<font color="{GOLD}" size="15"><b>{med}</b></font>'
            f'&nbsp;&nbsp;<font color="{PERLWEISS}" size="13"><b>{w}</b></font>',
            s_rank_
        )]]
        t = Table(data, colWidths=[14.5*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), NB),
            ("TOPPADDING",    (0,0), (-1,-1), 14),
            ("BOTTOMPADDING", (0,0), (-1,-1), 14),
            ("LEFTPADDING",   (0,0), (-1,-1), 20),
            ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.28*cm))

    story.append(Paragraph(
        "Diese drei Werte sind dein Fundament. Ihre Reihenfolge darf sich verschieben –"
        " das ist kein Widerspruch, sondern Entwicklung.",
        s_italic
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=SR, spaceAfter=14))

    # Top 5
    story.append(Paragraph("Dein innerer Kreis — Top 5", s_sec))
    rows5 = [[Paragraph(f"• {w}", s_body)] for w in top5]
    t5 = Table(rows5, colWidths=[14.5*cm])
    t5.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), SR),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 16),
    ]))
    story.append(t5)
    story.append(Spacer(1, 0.5*cm))

    # Top 10
    story.append(Paragraph("Deine Wertewelt — Top 10", s_sec))
    col_a = top10[:5]
    col_b = top10[5:10]
    rows10 = [[Paragraph(f"• {a}", s_body), Paragraph(f"• {b}", s_body) if i < len(col_b) else Paragraph("", s_body)]
              for i, (a, b) in enumerate(zip(col_a, col_b + [""] * (5 - len(col_b))))]
    t10 = Table(rows10, colWidths=[7*cm, 7.5*cm])
    t10.setStyle(TableStyle([
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    story.append(t10)

    story.append(Spacer(1, 1.2*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceAfter=8))
    story.append(Paragraph(COPYRIGHT, s_footer))

    doc.build(story)
    return buf.getvalue()


# ── SESSION STATE ─────────────────────────────────────────────────────────────

DEFAULTS: dict = {
    "screen":           "login",
    "name":             "",
    "email":            "",
    "p1_group":         0,
    "p1_gruppen":       None,   # shuffled copy of WERTE_GRUPPEN — set on first use
    "p1_saved":         None,   # set() of confirmed selections — initialized on first use
    "p2_selected":      [],
    "p1_alle_selected": [],
    "top10":            [],
    "top5":             [],
    "p3_pairs":         [],
    "p3_idx":           0,
    "p3_results":       [],
    "top3":             [],
    "p4_pairs":         [],
    "p4_idx":           0,
    "p4_results":       [],
    "p4_scenario":      None,
    "p4_scenario_done": False,
    "final_ranking":    [],
    "pdf_bytes":          None,
    "direction_analysis": None,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def go(screen: str):
    st.session_state["screen"] = screen
    st.rerun()


def footer():
    st.markdown(f'<div class="footer-copy">{COPYRIGHT}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: LOGIN
# ══════════════════════════════════════════════════════════════════════════════

def screen_login():
    header = get_header_html()
    if header:
        st.markdown(header, unsafe_allow_html=True)
    else:
        st.markdown('<div class="elara-title">ELARA Value Decoder</div>', unsafe_allow_html=True)
        st.markdown('<div class="elara-sub">Was bleibt, wenn alles andere wegfällt – deine Werte, dein Kompass.</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Auto-grant via URL param
    url_code = st.query_params.get("code", "")
    if url_code:
        valid, _ = check_and_use_voucher(url_code)
        if valid and "url_access" not in st.session_state:
            st.session_state["url_access"] = True

    with st.form("login_form"):
        email_input = st.text_input(
            "Deine E-Mail-Adresse",
            placeholder="Mit dieser E-Mail hast du gekauft"
        )
        name = st.text_input("Wie heisst du?", placeholder="Dein Vorname")
        code_input = st.text_input(
            "Gutscheincode (optional)",
            placeholder="Falls du einen Code hast – hier eingeben"
        )
        submitted = st.form_submit_button("Starten →", use_container_width=True)

    if submitted:
        name   = name.strip()
        email  = email_input.strip().lower()
        code   = code_input.strip()

        if not name:
            st.error("Bitte gib deinen Vornamen ein.")
            st.stop()
        if not email:
            st.error("Bitte gib deine E-Mail-Adresse ein.")
            st.stop()

        # Zugang prüfen: E-Mail ODER Code
        has_url_access   = st.session_state.get("url_access", False)
        email_authorized = check_email_access(email)
        code_valid       = False
        if code:
            code_valid, msg = check_and_use_voucher(code)

        if not has_url_access and not email_authorized and not code_valid:
            if code and not code_valid:
                st.error(msg)
            else:
                st.error("Diese E-Mail-Adresse hat keinen Zugang. Bitte prüfe deine Kaufbestätigung oder gib einen Gutscheincode ein.")
            st.stop()

        st.session_state["name"]  = name
        st.session_state["email"] = email
        go("intro")

    st.markdown(
        f'<div style="text-align:center;color:#bbb;font-size:0.78rem;margin-top:1.5rem;">'
        f'CHF 47.– · Einmalig · Dein persönliches Werte-Profil</div>',
        unsafe_allow_html=True
    )
    footer()


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: INTRO
# ══════════════════════════════════════════════════════════════════════════════

def screen_intro():
    name = st.session_state["name"]
    header = get_header_html()
    if header:
        st.markdown(header, unsafe_allow_html=True)
    else:
        st.markdown('<div class="elara-title">ELARA Value Decoder</div>', unsafe_allow_html=True)
        st.markdown('<div class="elara-sub">Was bleibt, wenn alles andere wegfällt – deine Werte, dein Kompass.</div>', unsafe_allow_html=True)

    st.markdown(f"### Hallo {name} &nbsp;👋", unsafe_allow_html=True)
    st.markdown("**⏱ Zeitaufwand: ca. 30 Minuten**")
    st.markdown("")

    st.markdown("#### Wo sind deine Werte wichtig?")
    st.markdown(f"""<div class="intro-box">
Deine Werte beeinflussen mehr, als du vielleicht denkst:<br><br>
<b>Berufswahl</b> – Welche Tätigkeit gibt dir wirklich Sinn?<br>
<b>Firmenwahl</b> – In welcher Kultur kannst du aufblühen?<br>
<b>Mitarbeiterwahl</b> – Wen willst du wirklich an deiner Seite?<br>
<b>Partnerschaft & Geschäftsaufbau</b> – Was braucht es, damit etwas wirklich trägt?
</div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="intro-box">
Herzlich willkommen – und ehrlich gesagt: guter Entscheid.<br><br>
Nicht jede nimmt sich die Zeit, wirklich hinzuschauen. Zu fragen: Was trägt mich eigentlich?
Was ist mir – jenseits von Erwartungen, Rollen und dem ganzen Lärm des Alltags – wirklich wichtig?<br><br>
Du hast dich entschieden, genau das herauszufinden. Und das ist keine Kleinigkeit.<br><br>
Deine Werte sind kein Nice-to-have. Sie sind der unsichtbare Faden, der durch alle deine Entscheidungen
läuft – ob du sie kennst oder nicht. Wenn du sie kennst, entscheidest du klarer.
Du weisst schneller, was dir ein Ja wert ist – und was ein klares Nein verdient.<br><br>
Der ELARA Value Decoder führt dich Schritt für Schritt zu deinen drei wichtigsten Werten.
Nicht irgendwelchen – sondern deinen.<br><br>
Ich freue mich, dass du da bist. Lass uns anfangen.
</div>""", unsafe_allow_html=True)

    st.info(
        "Nimm dir diese 30 Minuten bewusst – ohne Handy, ohne Unterbrechung, ohne Erwartung. "
        "Lass die Antworten kommen, anstatt sie zu suchen. "
        "Dein erster Impuls ist meistens der ehrlichste."
    )
    st.markdown("")
    if st.button("Los geht's →"):
        go("phase1")
    footer()


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: PHASE 1 — 150 WERTE IN 5ER-GRUPPEN
# ══════════════════════════════════════════════════════════════════════════════

def screen_phase1():
    idx   = st.session_state["p1_group"]

    # Einmalig beim ersten Aufruf: Gruppen mischen
    if st.session_state.get("p1_gruppen") is None:
        gruppen = [list(g) for g in WERTE_GRUPPEN]
        random.shuffle(gruppen)
        st.session_state["p1_gruppen"] = gruppen
    gruppen = st.session_state["p1_gruppen"]
    total   = len(gruppen)

    # p1_saved ist die einzige Quelle der Wahrheit.
    # Streamlit löscht Checkbox-Widget-Keys sobald die Gruppe wechselt —
    # deshalb speichern wir explizit vor jedem Seitenwechsel.
    if st.session_state.get("p1_saved") is None:
        st.session_state["p1_saved"] = set()
    saved: set = st.session_state["p1_saved"]

    # ── Alle Gruppen durchgegangen ────────────────────────────────────────────
    if idx >= total:
        n    = len(saved)
        wort = "Wert" if n == 1 else "Werte"
        if n < 5:
            st.markdown('<span class="phase-pill">Phase 1</span>', unsafe_allow_html=True)
            st.markdown("### Noch ein bisschen mehr")
            st.warning(
                f"Du hast {n} {wort} ausgewählt. "
                "Für den nächsten Schritt brauchst du mindestens 5. "
                "Geh nochmals durch die Liste – und klicke an, was dich noch ansprechen könnte."
            )
            if st.button("← Nochmals durchgehen"):
                # Bestehende Auswahl BEHALTEN — nur von vorne durchgehen
                st.session_state["p1_group"] = 0
                for w in ALLE_WERTE:
                    st.session_state.pop(f"v_{w}", None)
                st.rerun()
            footer()
            return

        top10 = compute_top10(saved)[:10]
        st.session_state["top10"] = top10
        go("top10")
        return

    # ── Aktuelle Gruppe anzeigen ──────────────────────────────────────────────
    gruppe = gruppen[idx]

    # Nur initialisieren wenn Key fehlt (Gruppe gerade gewechselt) — nie überschreiben
    for w in gruppe:
        if f"v_{w}" not in st.session_state:
            st.session_state[f"v_{w}"] = w in saved

    st.markdown('<span class="phase-pill">Phase 1 – Entdeckungsrunde</span>', unsafe_allow_html=True)
    st.progress(idx / total)
    st.markdown(
        f'<div class="hint">Gruppe {idx+1} von {total} &nbsp;·&nbsp; {len(saved)} Werte ausgewählt</div>',
        unsafe_allow_html=True
    )
    st.markdown("### Was spricht dich an?")
    st.markdown('<div class="hint">Klicke an, was dich berührt – egal warum. Vertrau deinem ersten Impuls.</div>', unsafe_allow_html=True)
    st.markdown("")

    for w in gruppe:
        st.checkbox(w, key=f"v_{w}")

    def _save_gruppe():
        for w in gruppe:
            if st.session_state.get(f"v_{w}", False):
                saved.add(w)
            else:
                saved.discard(w)
        # Widget-Keys löschen, damit die nächste Gruppe sauber initialisiert
        for w in gruppe:
            st.session_state.pop(f"v_{w}", None)

    st.markdown("")
    col_back, col_next = st.columns([1, 2])
    with col_back:
        if idx > 0:
            st.markdown('<div class="back-btn">', unsafe_allow_html=True)
            if st.button("← Zurück", key="p1_back"):
                _save_gruppe()
                prev = gruppen[idx - 1]
                for w in prev:
                    st.session_state.pop(f"v_{w}", None)
                st.session_state["p1_group"] = idx - 1
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    with col_next:
        label = "Weiter →" if idx < total - 1 else "Auswertung →"
        if st.button(label, key="p1_next"):
            _save_gruppe()
            st.session_state["p1_group"] = idx + 1
            st.rerun()

    footer()


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: PICK TOP 10 (wenn mehr als 10 ausgewählt)
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: TOP 10 REVEAL
# ══════════════════════════════════════════════════════════════════════════════

def screen_top10():
    top10 = st.session_state["top10"]
    name  = st.session_state["name"]

    st.markdown(f"""<div class="celebration">
<div style="font-size:2rem;">🎉</div>
<div class="playfair" style="font-size:1.6rem;font-weight:700;color:{NACHTBLAU};margin:0.5rem 0;">
Das ist ein grosser Schritt, {name}!</div>
<div style="color:{DARK};font-size:0.95rem;line-height:1.7;margin-top:0.5rem;">
Du hast soeben deine Top 10 Werte identifiziert.<br>
Das klingt nach wenig – ist es aber nicht.<br>
Die meisten Menschen wissen nicht einmal, was ihre wichtigsten fünf Werte sind.<br><br>
Und gleichzeitig: Zehn sind noch zu viele, um wirklich als Kompass zu dienen.<br>
Deshalb gehen wir jetzt tiefer.
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("#### Deine Top 10:")
    for w in top10:
        st.markdown(f'<span class="value-pill">{w}</span>', unsafe_allow_html=True)

    st.markdown("")
    if st.button("Weiter zu Phase 2 →"):
        st.session_state["p2_selected"] = []
        go("phase2")
    footer()


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: PHASE 2 — TOP 10 → TOP 5
# ══════════════════════════════════════════════════════════════════════════════

def screen_phase2():
    top10 = st.session_state["top10"]

    st.markdown('<span class="phase-pill">Phase 2 – Eingrenzung</span>', unsafe_allow_html=True)
    st.markdown("### Welche fünf treffen dich am tiefsten?")
    st.markdown('<div class="hint">Klick schnell – dein Bauch weiss es.</div>', unsafe_allow_html=True)
    st.markdown("")

    # Init checkboxes
    for w in top10:
        if f"p2_{w}" not in st.session_state:
            st.session_state[f"p2_{w}"] = False

    selected_count = sum(1 for w in top10 if st.session_state.get(f"p2_{w}", False))
    st.markdown(
        f'<div style="text-align:right;"><span class="counter-badge">{selected_count} / 5 ausgewählt</span></div>',
        unsafe_allow_html=True
    )
    st.markdown("")

    cols = st.columns(2)
    for i, w in enumerate(top10):
        with cols[i % 2]:
            st.checkbox(w, key=f"p2_{w}")

    st.markdown("")
    if st.button("Weiter →"):
        top5 = [w for w in top10 if st.session_state.get(f"p2_{w}", False)]
        if len(top5) != 5:
            st.error(f"Bitte wähle genau 5 Werte aus. Du hast {len(top5)} ausgewählt.")
        else:
            st.session_state["top5"] = top5
            st.session_state["p3_pairs"]   = get_pairs(5)
            st.session_state["p3_idx"]     = 0
            st.session_state["p3_results"] = []
            go("phase3")
    footer()


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: PHASE 3 — PAARVERGLEICH TOP 5 → TOP 3
# ══════════════════════════════════════════════════════════════════════════════

def screen_phase3():
    top5  = st.session_state["top5"]
    pairs = st.session_state["p3_pairs"]
    idx   = st.session_state["p3_idx"]

    if idx >= len(pairs):
        # Calculate top 3
        ranked, _ = rank_by_wins(top5, st.session_state["p3_results"], pairs)
        st.session_state["top3"] = ranked[:3]
        go("top3")
        return

    i, j  = pairs[idx]
    va, vb = top5[i], top5[j]

    st.markdown('<span class="phase-pill">Phase 3 – Vertiefung</span>', unsafe_allow_html=True)
    st.progress(idx / len(pairs))
    st.markdown(f'<div class="hint">Vergleich {idx+1} von {len(pairs)}</div>', unsafe_allow_html=True)

    st.markdown("### Wenn du nur einen davon behalten könntest – welcher wäre es?")
    st.markdown("")

    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:center;gap:1rem;margin:1rem 0 1.5rem;">
        <div style="background:{SOFT_ROSA};border:2px solid {MAGENTA};border-radius:12px;
                    padding:1rem 1.5rem;text-align:center;flex:1;
                    font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:700;color:{NACHTBLAU};">
            {va}
        </div>
        <div style="color:{MAGENTA};font-size:1.4rem;font-weight:700;flex-shrink:0;">vs</div>
        <div style="background:{SOFT_ROSA};border:2px solid {MAGENTA};border-radius:12px;
                    padding:1rem 1.5rem;text-align:center;flex:1;
                    font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:700;color:{NACHTBLAU};">
            {vb}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"✓ {va}", key=f"p3a_{idx}", use_container_width=True):
            st.session_state["p3_results"].append(i)
            st.session_state["p3_idx"] += 1
            st.rerun()
    with col2:
        if st.button(f"✓ {vb}", key=f"p3b_{idx}", use_container_width=True):
            st.session_state["p3_results"].append(j)
            st.session_state["p3_idx"] += 1
            st.rerun()

    st.markdown(
        '<div class="hint" style="margin-top:1.2rem;">Kein Richtig oder Falsch. Einfach fühlen.</div>',
        unsafe_allow_html=True
    )
    footer()


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: TOP 3 REVEAL
# ══════════════════════════════════════════════════════════════════════════════

def screen_top3():
    top3 = st.session_state["top3"]
    name = st.session_state["name"]

    st.markdown(f"""<div class="celebration">
<div style="font-size:2rem;">🎉</div>
<div class="playfair" style="font-size:1.5rem;font-weight:700;color:{NACHTBLAU};margin:0.5rem 0;">
Du hast deine Top 3, {name}!</div>
<div style="color:{DARK};font-size:0.95rem;line-height:1.7;margin-top:0.5rem;">
Das sind die drei Werte, die dich am tiefsten tragen.<br>
Sie werden sich in der Regel nie mehr grundlegend verändern.<br><br>
<i>Wichtig: Die Reihenfolge deiner Top 3 darf sich verschieben – das ist kein Widerspruch, sondern Entwicklung.
Du veränderst dich, deine Prioritäten auch. Das ist gesund und gewollt.</i>
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("")
    for w in top3:
        st.markdown(f'<span class="value-pill" style="font-size:1.1rem;padding:8px 22px;">{w}</span>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown("#### Was ist dein Nr. 1 Wert?")
    st.markdown("Im nächsten Schritt finden wir die genaue Reihenfolge heraus.")
    st.markdown("")

    if st.button("Weiter zu Phase 4 →"):
        st.session_state["p4_pairs"]         = get_pairs(3)
        st.session_state["p4_idx"]           = 0
        st.session_state["p4_results"]       = []
        st.session_state["p4_scenario"]      = None
        st.session_state["p4_scenario_done"] = False
        go("phase4")
    footer()


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: PHASE 4 — PRIORISIERUNG TOP 3
# ══════════════════════════════════════════════════════════════════════════════

def screen_phase4():
    top3  = st.session_state["top3"]
    pairs = st.session_state["p4_pairs"]
    idx   = st.session_state["p4_idx"]

    # ── Step A: pairwise comparisons ──────────────────────────────────────────
    if idx < len(pairs):
        i, j   = pairs[idx]
        va, vb = top3[i], top3[j]

        st.markdown('<span class="phase-pill">Phase 4 – Priorisierung</span>', unsafe_allow_html=True)
        st.progress(idx / (len(pairs) + 1))
        st.markdown(f'<div class="hint">Vergleich {idx+1} von {len(pairs)}</div>', unsafe_allow_html=True)

        st.markdown("### Wenn du nur einen davon behalten könntest – welcher wäre es?")
        st.markdown("")

        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:center;gap:1rem;margin:1rem 0 1.5rem;">
            <div style="background:{SOFT_ROSA};border:2px solid {MAGENTA};border-radius:12px;
                        padding:1rem 1.5rem;text-align:center;flex:1;
                        font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:700;color:{NACHTBLAU};">
                {va}
            </div>
            <div style="color:{MAGENTA};font-size:1.4rem;font-weight:700;flex-shrink:0;">vs</div>
            <div style="background:{SOFT_ROSA};border:2px solid {MAGENTA};border-radius:12px;
                        padding:1rem 1.5rem;text-align:center;flex:1;
                        font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:700;color:{NACHTBLAU};">
                {vb}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✓ {va}", key=f"p4a_{idx}", use_container_width=True):
                st.session_state["p4_results"].append(i)
                st.session_state["p4_idx"] += 1
                st.rerun()
        with col2:
            if st.button(f"✓ {vb}", key=f"p4b_{idx}", use_container_width=True):
                st.session_state["p4_results"].append(j)
                st.session_state["p4_idx"] += 1
                st.rerun()

        st.markdown(
            '<div class="hint" style="margin-top:1.2rem;">Kein Richtig oder Falsch. Einfach fühlen.</div>',
            unsafe_allow_html=True
        )
        footer()
        return

    # ── Step B: scenario question ─────────────────────────────────────────────
    if not st.session_state["p4_scenario_done"]:
        ranked, _ = rank_by_wins(top3, st.session_state["p4_results"], pairs)

        if st.session_state["p4_scenario"] is None:
            client = get_client()
            with st.spinner("Einen Moment – ich bereite eine letzte Frage vor..."):
                if client:
                    sc = generate_scenario(client, ranked[0], ranked[1], st.session_state["name"])
                else:
                    sc = {
                        "frage": f"Wenn du wählen müsstest – was ist dir letztlich wichtiger: {ranked[0]} oder {ranked[1]}?",
                        "a": ranked[0],
                        "b": ranked[1],
                    }
            st.session_state["p4_scenario"] = sc
            st.rerun()

        sc = st.session_state["p4_scenario"]

        st.markdown('<span class="phase-pill">Phase 4 – Letzte Frage</span>', unsafe_allow_html=True)
        st.markdown("### Noch eine Situation")
        st.markdown(f'<div class="intro-box">{sc["frage"]}</div>', unsafe_allow_html=True)
        st.markdown("")

        st.markdown('<div class="compare-area">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(sc["a"], key="p4_sc_a", use_container_width=True):
                # Option A won → ranked[0] confirmed as #1
                st.session_state["final_ranking"] = ranked
                st.session_state["p4_scenario_done"] = True
                go("result")
        with col2:
            if st.button(sc["b"], key="p4_sc_b", use_container_width=True):
                # Option B won → swap #1 and #2
                adjusted = [ranked[1], ranked[0]] + ranked[2:]
                st.session_state["final_ranking"] = adjusted
                st.session_state["p4_scenario_done"] = True
                go("result")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="hint" style="margin-top:1.2rem;">Kein Richtig oder Falsch. Dein Bauch weiss die Antwort.</div>',
            unsafe_allow_html=True
        )
        footer()


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN: RESULT — AUSWERTUNGSBLATT
# ══════════════════════════════════════════════════════════════════════════════

def screen_result():
    name    = st.session_state["name"]
    ranking = st.session_state["final_ranking"]
    top5    = st.session_state["top5"]
    top10   = st.session_state["top10"]

    st.markdown('<div class="elara-title">Dein Werte-Profil</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="elara-sub">ELARA Value Decoder · {name}</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Top 3 – Kompass
    st.markdown("#### Dein Kompass — Die 3 Kernwerte")
    medals_html = ["1.", "2.", "3."]
    for i, (w, med) in enumerate(zip(ranking[:3], medals_html)):
        st.markdown(
            f'<div class="rank-row">'
            f'<span class="rank-num">{med}</span>'
            f'<span class="rank-val">{w}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("")
    st.markdown(
        f'<div style="background:{SOFT_ROSA};border-radius:8px;padding:1rem 1.3rem;'
        f'font-style:italic;color:{NACHTBLAU};font-size:0.95rem;line-height:1.7;">'
        f'Diese drei Werte sind dein Fundament. Ihre Reihenfolge darf sich verschieben – '
        f'das ist kein Widerspruch, sondern Entwicklung.</div>',
        unsafe_allow_html=True
    )

    st.markdown("")

    # Richtungsanalyse durch KI
    if "direction_analysis" not in st.session_state:
        client = get_client()
        if client:
            with st.spinner("Deine Richtung wird analysiert..."):
                try:
                    st.session_state["direction_analysis"] = generate_direction_analysis(
                        client, ranking, top10, name
                    )
                except Exception:
                    st.session_state["direction_analysis"] = None
        else:
            st.session_state["direction_analysis"] = None

    if st.session_state.get("direction_analysis"):
        st.markdown(
            f'<div style="background:{SOFT_ROSA};border-left:4px solid {MAGENTA};'
            f'border-radius:0 8px 8px 0;padding:1rem 1.3rem;color:{NACHTBLAU};'
            f'font-size:0.97rem;line-height:1.8;margin:0.5rem 0 1rem;">'
            f'<strong>Deine Richtung:</strong><br>{st.session_state["direction_analysis"]}'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Dein innerer Kreis — Top 5")
        for w in top5:
            st.markdown(f'<span class="value-pill">{w}</span>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### Deine Wertewelt — Top 10")
        for w in top10:
            st.markdown(f'<span class="value-pill">{w}</span>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown("---")

    # PDF download
    if st.session_state["pdf_bytes"] is None:
        with st.spinner("PDF wird erstellt..."):
            try:
                st.session_state["pdf_bytes"] = build_pdf(name, top10, top5, ranking)
            except Exception as e:
                st.warning(f"PDF konnte nicht erstellt werden: {e}")

    if st.session_state["pdf_bytes"]:
        st.download_button(
            label="⬇ Werte-Profil als PDF herunterladen",
            data=st.session_state["pdf_bytes"],
            file_name=f"ELARA-Werte-Profil-{name}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.markdown("")
    if st.button("Neues Profil erstellen", key="restart"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        go("login")

    footer()


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════

SCREENS = {
    "login":   screen_login,
    "intro":   screen_intro,
    "phase1":  screen_phase1,
    "top10":   screen_top10,
    "phase2":  screen_phase2,
    "phase3":  screen_phase3,
    "top3":    screen_top3,
    "phase4":  screen_phase4,
    "result":  screen_result,
}

SCREENS.get(st.session_state["screen"], screen_login)()
