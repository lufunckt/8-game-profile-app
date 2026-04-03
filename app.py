
import json
from pathlib import Path
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent

@st.cache_data
def load_json(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))

hero_profiles = load_json("8_game_hero_profiles_v2.json")
opponent_profiles = load_json("8_game_opponent_profiles_v2.json")
comparison_profiles = load_json("8_game_comparison_profiles_v2.json")
summary_data = load_json("8_game_profile_summary_v2.json")

hero = summary_data["hero"]
hero_overall = comparison_profiles[0]["hero_overall"] if comparison_profiles else {}

st.set_page_config(page_title="8-Game Profile Lab", page_icon="♠️", layout="wide")

# ─── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Exo+2:wght@300;400;500;600;700;800&family=Share+Tech+Mono&display=swap');

/* ── BASE ── */
html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif !important;
}
.stApp {
    background: #060b18 !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,200,255,0.08) 0%, transparent 70%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(180,0,255,0.06) 0%, transparent 60%);
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1020 0%, #060b18 100%) !important;
    border-right: 1px solid rgba(0,200,255,0.15) !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #a0c8ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em;
    padding: 6px 0;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    color: #00d4ff !important;
}

/* ── HERO TITLE ── */
.hero-title {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: clamp(1.8rem, 5vw, 3.2rem);
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    background: linear-gradient(135deg, #00d4ff 0%, #bf00ff 50%, #ff6b35 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
    text-shadow: none;
}
.hero-sub {
    font-family: 'Share Tech Mono', monospace;
    color: rgba(0,212,255,0.6);
    font-size: 0.75rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* ── STAT CARDS (metric boxes) ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.07) 0%, rgba(30,20,60,0.8) 100%) !important;
    border: 1px solid rgba(0,212,255,0.25) !important;
    border-radius: 14px !important;
    padding: 14px 16px !important;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, transform 0.2s;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(0,212,255,0.6) !important;
    transform: translateY(-2px);
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, #00d4ff, #bf00ff);
    border-radius: 3px 0 0 3px;
}
[data-testid="stMetricLabel"] p {
    font-family: 'Share Tech Mono', monospace !important;
    color: rgba(0,212,255,0.7) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}

/* ── SECTION HEADERS ── */
.section-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #00d4ff;
    border-bottom: 1px solid rgba(0,212,255,0.2);
    padding-bottom: 8px;
    margin: 1.5rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── OPPONENT CARD GRID ── */
.opp-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
    gap: 12px;
    margin: 1rem 0;
}
.opp-card {
    background: linear-gradient(135deg, rgba(15,25,50,0.95) 0%, rgba(10,15,35,0.9) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 14px 12px;
    cursor: pointer;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
    text-align: center;
}
.opp-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
}
.opp-card.selected {
    border-color: rgba(0,212,255,0.7) !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.2), inset 0 0 20px rgba(0,212,255,0.04);
}
.opp-card-accent {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 14px 14px 0 0;
}
.opp-avatar {
    width: 46px; height: 46px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    margin: 6px auto 8px auto;
    font-weight: 700;
    border: 2px solid rgba(255,255,255,0.15);
}
.opp-name {
    font-family: 'Exo 2', sans-serif;
    font-weight: 700;
    font-size: 0.82rem;
    color: #e8f0ff;
    margin-bottom: 4px;
    word-break: break-all;
    line-height: 1.2;
}
.opp-stats-mini {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: rgba(160,200,255,0.7);
    line-height: 1.6;
}
.opp-badge {
    display: inline-block;
    padding: 2px 7px;
    border-radius: 20px;
    font-size: 0.6rem;
    font-weight: 700;
    font-family: 'Share Tech Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 5px;
}
.badge-alta { background: rgba(0,255,160,0.15); color: #00ffa0; border: 1px solid rgba(0,255,160,0.3); }
.badge-media { background: rgba(255,200,0,0.15); color: #ffc800; border: 1px solid rgba(255,200,0,0.3); }
.badge-baixa { background: rgba(255,80,80,0.15); color: #ff5050; border: 1px solid rgba(255,80,80,0.3); }

/* ── PLAYER DETAIL PANEL ── */
.player-panel {
    background: linear-gradient(135deg, rgba(0,212,255,0.04) 0%, rgba(10,15,40,0.95) 100%);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 18px;
    padding: 20px;
    margin-top: 12px;
}
.player-panel-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 16px;
}
.player-panel-avatar {
    width: 56px; height: 56px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem;
    flex-shrink: 0;
    border: 2px solid rgba(255,255,255,0.2);
}
.player-panel-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.04em;
}
.player-panel-label {
    font-size: 0.8rem;
    color: rgba(160,200,255,0.8);
    margin-top: 2px;
}

/* ── VARIANT PILL ── */
.variant-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,212,255,0.1);
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 20px;
    padding: 4px 12px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #00d4ff;
    margin: 3px;
    cursor: pointer;
    transition: all 0.2s;
}
.variant-pill:hover, .variant-pill.active {
    background: rgba(0,212,255,0.25);
    border-color: #00d4ff;
}

/* ── STAT BAR ── */
.stat-bar-wrap {
    margin: 6px 0;
}
.stat-bar-label {
    display: flex;
    justify-content: space-between;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: rgba(160,200,255,0.8);
    margin-bottom: 3px;
}
.stat-bar-track {
    height: 6px;
    background: rgba(255,255,255,0.06);
    border-radius: 10px;
    overflow: hidden;
}
.stat-bar-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 0.6s ease;
}

/* ── ANALYSIS OUTPUT ── */
.analysis-box {
    background: rgba(0,5,15,0.7);
    border: 1px solid rgba(0,212,255,0.15);
    border-left: 3px solid #00d4ff;
    border-radius: 10px;
    padding: 16px;
    font-family: 'Exo 2', sans-serif;
    font-size: 0.88rem;
    color: #c8deff;
    line-height: 1.75;
    white-space: pre-wrap;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,212,255,0.15) 0%, rgba(100,0,255,0.15) 100%) !important;
    border: 1px solid rgba(0,212,255,0.4) !important;
    border-radius: 10px !important;
    color: #00d4ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    transition: all 0.25s !important;
    padding: 8px 16px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,212,255,0.3) 0%, rgba(150,0,255,0.3) 100%) !important;
    border-color: #00d4ff !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.25) !important;
    transform: translateY(-1px);
}

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(10,20,45,0.95) !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
    border-radius: 10px !important;
    color: #c8deff !important;
    font-family: 'Exo 2', sans-serif !important;
}

/* ── TEXT INPUT ── */
[data-testid="stTextInput"] input {
    background: rgba(10,20,45,0.95) !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
    border-radius: 10px !important;
    color: #c8deff !important;
    font-family: 'Share Tech Mono', monospace !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 10px rgba(0,212,255,0.2) !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(0,212,255,0.15) !important;
    border-radius: 12px !important;
    overflow: hidden;
}

/* ── TEXT AREA ── */
textarea {
    background: rgba(5,10,25,0.95) !important;
    border: 1px solid rgba(0,212,255,0.2) !important;
    border-radius: 10px !important;
    color: #a8c0e8 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.78rem !important;
}

/* ── DIVIDER ── */
hr {
    border-color: rgba(0,212,255,0.15) !important;
}

/* ── WARNING / INFO ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: 1px solid rgba(255,200,0,0.3) !important;
    background: rgba(255,200,0,0.06) !important;
}

/* ── DASHBOARD VARIANT CARD ── */
.variant-card {
    background: linear-gradient(135deg, rgba(15,25,55,0.9) 0%, rgba(8,15,35,0.95) 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 12px;
    transition: all 0.25s;
    position: relative;
    overflow: hidden;
}
.variant-card:hover {
    border-color: rgba(0,212,255,0.35);
    transform: translateX(4px);
}
.variant-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}
.variant-card-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #e8f0ff;
    letter-spacing: 0.06em;
}
.variant-card-icon {
    font-size: 1.4rem;
}
.variant-profile-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: rgba(0,212,255,0.7);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── COMPARISON DUEL ── */
.duel-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    padding: 16px;
    background: linear-gradient(135deg, rgba(0,212,255,0.05), rgba(191,0,255,0.05));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    margin-bottom: 16px;
}
.duel-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: 0.08em;
}
.duel-vs {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: rgba(255,255,255,0.3);
    letter-spacing: 0.2em;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.5); }

/* ── MOBILE RESPONSIVE ── */
@media (max-width: 768px) {
    .opp-grid { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)) !important; gap: 8px !important; }
    .opp-card { padding: 10px 8px !important; }
    .hero-title { font-size: 1.6rem !important; }
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ────────────────────────────────────────────────────────────────────

VARIANT_ICONS = {
    "Hold'em Limit": "🃏",
    "Hold'em No Limit": "⚡",
    "Omaha Hi/Lo Limit": "🌗",
    "Omaha Pot Limit": "💣",
    "7 Card Stud Hi/Lo Limit": "✨",
    "7 Card Stud Limit": "🎴",
    "Razz Limit": "🔻",
    "Triple Draw 2-7 Lowball Limit": "🔄",
}
VARIANT_COLORS = {
    "Hold'em Limit":               ("135deg, #00aaff, #0055ff"),
    "Hold'em No Limit":            ("135deg, #ff6b35, #ff0060"),
    "Omaha Hi/Lo Limit":           ("135deg, #00ffaa, #00aaff"),
    "Omaha Pot Limit":             ("135deg, #bf00ff, #6600ff"),
    "7 Card Stud Hi/Lo Limit":     ("135deg, #ffcc00, #ff8800"),
    "7 Card Stud Limit":           ("135deg, #ff9500, #ff4500"),
    "Razz Limit":                  ("135deg, #ff0080, #aa00ff"),
    "Triple Draw 2-7 Lowball Limit": ("135deg, #00ffdd, #00aa88"),
}

# Deterministic avatar palette: each nick gets a consistent color from a set
AVATAR_PALETTES = [
    ("rgba(0,212,255,0.25)", "#00d4ff", "🎯"),
    ("rgba(191,0,255,0.25)", "#bf00ff", "🦁"),
    ("rgba(255,107,53,0.25)", "#ff6b35", "🔥"),
    ("rgba(0,255,160,0.25)", "#00ffa0", "🐍"),
    ("rgba(255,200,0,0.25)",  "#ffc800", "⚡"),
    ("rgba(255,0,128,0.25)",  "#ff0080", "🌪️"),
    ("rgba(100,200,255,0.25)","#64c8ff", "🌊"),
    ("rgba(255,160,0,0.25)",  "#ffa000", "🦊"),
    ("rgba(180,255,100,0.25)","#b4ff64", "🐉"),
    ("rgba(255,80,200,0.25)", "#ff50c8", "💎"),
]

def get_avatar(name):
    idx = sum(ord(c) for c in name) % len(AVATAR_PALETTES)
    return AVATAR_PALETTES[idx]

def conf_badge(conf):
    badge_cls = {"alta": "badge-alta", "média": "badge-media", "baixa": "badge-baixa"}.get(conf, "badge-media")
    return f'<span class="opp-badge {badge_cls}">{conf}</span>'

def stat_bar(label, value, max_val=100, color="#00d4ff"):
    pct = min(value / max_val * 100, 100)
    return f"""
    <div class="stat-bar-wrap">
        <div class="stat-bar-label"><span>{label}</span><span>{value}%</span></div>
        <div class="stat-bar-track">
            <div class="stat-bar-fill" style="width:{pct}%; background: linear-gradient(90deg, {color}, {color}88);"></div>
        </div>
    </div>"""

def variant_gradient(v):
    return VARIANT_COLORS.get(v, "135deg, #00d4ff, #bf00ff")

# ─── PROMPTS ────────────────────────────────────────────────────────────────────

def variant_prompt(v):
    return f"""Analise o perfil da jogadora {hero} na modalidade "{v['variant']}" usando estes dados:
- mãos: {v['hands']}
- torneios: {v['tournaments']}
- VPIP: {v['vpip_pct']}%
- agressão inicial: {v['first_aggr_pct']}%
- taxa de agressão: {v['agg_rate_pct']}%
- showdown: {v['showdown_pct']}%
- vitória em showdown: {v['showdown_win_pct']}%
- vitória total: {v['win_pct']}%
- vitórias sem showdown: {v['unshown_win_pct']}%
- fold rate: {v['fold_pct']}%

Quero:
1. pontos fortes prováveis
2. leaks prováveis
3. ajustes práticos de estratégia
4. o que observar na próxima amostra
5. conclusão curta sobre o estilo da jogadora nessa modalidade
"""

def opponent_prompt(o):
    mix = "; ".join([f"{k}: {v} mãos" for k, v in o["variant_mix"].items()])
    return f"""Monte um scouting report do oponente "{o['name']}" no contexto de 8-Game com estes dados:
- mãos observadas: {o['hands']}
- torneios compartilhados: {o['tournaments']}
- confiança da amostra: {o['confidence']}
- variantes vistas: {o['variants_seen']}/8
- variante dominante: {o['top_variant']} ({o['top_share_pct']}%)
- VPIP: {o['vpip_pct']}%
- agressão inicial: {o['first_aggr_pct']}%
- taxa de agressão: {o['agg_rate_pct']}%
- showdown: {o['showdown_pct']}%
- vitória em showdown: {o['showdown_win_pct']}%
- vitória total: {o['win_pct']}%
- vitórias sem showdown: {o['unshown_win_pct']}%
- fold rate: {o['fold_pct']}%
- mix por modalidade: {mix}

Quero:
1. tipo provável de jogador
2. como explorar esse perfil
3. em quais modalidades ele parece mais confortável
4. o que esses dados ainda não permitem afirmar
5. plano curto de adaptação contra esse nick
"""

def compare_prompt(c):
    o = c["opponent_overall"]
    rows = []
    for r in c["variant_comparison"]:
        rows.append(
            f"- {r['variant']}: hero VPIP {r['hero_vpip_pct']}% vs vilão {r['opp_vpip_pct']}%, "
            f"hero 1ª agressão {r['hero_first_aggr_pct']}% vs vilão {r['opp_first_aggr_pct']}%, "
            f"hero showdown {r['hero_showdown_pct']}% vs vilão {r['opp_showdown_pct']}%, "
            f"hero win {r['hero_win_pct']}% vs vilão {r['opp_win_pct']}%"
        )
    variant_text = "\n".join(rows)
    return f"""Compare a jogadora {hero} com o oponente "{c['name']}" no 8-Game.

Hero overall:
- mãos: {c['hero_overall']['hands']}
- VPIP: {c['hero_overall']['vpip_pct']}%
- agressão inicial: {c['hero_overall']['first_aggr_pct']}%
- agg rate: {c['hero_overall']['agg_rate_pct']}%
- showdown: {c['hero_overall']['showdown_pct']}%
- showdown win: {c['hero_overall']['showdown_win_pct']}%
- win total: {c['hero_overall']['win_pct']}%
- fold: {c['hero_overall']['fold_pct']}%

Vilão overall:
- mãos: {o['hands']}
- VPIP: {o['vpip_pct']}%
- agressão inicial: {o['first_aggr_pct']}%
- agg rate: {o['agg_rate_pct']}%
- showdown: {o['showdown_pct']}%
- showdown win: {o['showdown_win_pct']}%
- win total: {o['win_pct']}%
- fold: {o['fold_pct']}%

Comparação por modalidades compartilhadas:
{variant_text}

Quero:
1. diferenças de estilo
2. onde a hero parece mais sólida
3. onde o vilão parece mais perigoso
4. ajustes táticos da hero contra esse vilão
5. conclusão curta
"""

# ─── LOCAL ANALYSIS ────────────────────────────────────────────────────────────

def local_analysis_variant(v):
    notes = []
    if v["vpip_pct"] < 20:
        notes.append("Participação bem contida. O perfil parece mais seletivo do que expansivo.")
    elif v["vpip_pct"] < 30:
        notes.append("Participação moderada. A entrada em potes parece controlada.")
    else:
        notes.append("Participação relativamente alta. Vale observar se essa abertura está sendo bem sustentada.")
    if v["first_aggr_pct"] < 10:
        notes.append("Pouca iniciativa na primeira rodada. Pode existir espaço para pressionar mais spots bons.")
    elif v["first_aggr_pct"] < 18:
        notes.append("Agressão inicial razoável, mas ainda sem cara de perfil muito pressionador.")
    else:
        notes.append("Boa frequência de iniciativa. Há indício de postura mais ativa na abertura das mãos.")
    if v["showdown_pct"] > 25 and v["showdown_win_pct"] < 45:
        notes.append("Vai bastante ao showdown, mas converte pouco. Pode haver calls marginais.")
    elif v["showdown_pct"] < 15 and v["fold_pct"] > 70:
        notes.append("Abandona muita mão cedo. Pode estar deixando EV em spots defendíveis.")
    else:
        notes.append("A relação entre showdown e fold parece relativamente equilibrada.")
    if v["fold_pct"] > 75:
        notes.append("Fold rate alta. Em várias linhas, a jogadora parece encerrar a mão antes do fim.")
    return "\n\n".join([f"• {n}" for n in notes])

def local_analysis_opponent(o):
    notes = []
    if o["vpip_pct"] >= 35:
        notes.append("Oponente relativamente envolvido. Tende a entrar em muitos potes.")
    else:
        notes.append("Oponente mais contido. Não parece perfil de entrada exagerada.")
    if o["first_aggr_pct"] >= 18:
        notes.append("Toma iniciativa com frequência perceptível. Melhor evitar linhas automáticas contra ele.")
    else:
        notes.append("Não mostra tanta iniciativa precoce. Pode ceder mais spots de pressão.")
    if o["showdown_pct"] >= 22 and o["showdown_win_pct"] >= 50:
        notes.append("Quando vai ao showdown, a amostra sugere que costuma chegar relativamente bem.")
    elif o["showdown_pct"] >= 22:
        notes.append("Vai ao showdown com frequência, mas sem taxa de conversão tão forte.")
    if o["variants_seen"] == 8:
        notes.append("Aparece nas 8 modalidades. Indício de regular de mix.")
    elif o["top_share_pct"] >= 45:
        notes.append(f"Tem concentração forte em {o['top_variant']}. Pode estar mais confortável nessa modalidade.")
    return "\n\n".join([f"• {n}" for n in notes])

def local_analysis_compare(c):
    h = c["hero_overall"]; o = c["opponent_overall"]
    notes = []
    if h["vpip_pct"] > o["vpip_pct"]:
        notes.append(f"{hero} entra em mais potes no geral do que {c['name']}.")
    else:
        notes.append(f"{c['name']} entra em mais potes no geral do que {hero}.")
    if h["first_aggr_pct"] > o["first_aggr_pct"]:
        notes.append(f"{hero} toma mais iniciativa inicial.")
    else:
        notes.append(f"{c['name']} tende a iniciar mais a agressão.")
    if h["showdown_win_pct"] > o["showdown_win_pct"]:
        notes.append(f"{hero} converte melhor os showdowns na amostra geral.")
    else:
        notes.append(f"{c['name']} converte melhor os showdowns na amostra geral.")
    dangerous = sorted(c["variant_comparison"], key=lambda r: (r["opp_win_pct"]-r["hero_win_pct"], r["opp_first_aggr_pct"]-r["hero_first_aggr_pct"]), reverse=True)
    if dangerous:
        d = dangerous[0]
        notes.append(f"A modalidade mais sensível aqui parece ser {d['variant']}, onde o vilão mostra melhor combinação relativa de agressão e win%.")
    return "\n\n".join([f"• {n}" for n in notes])

def try_openai(prompt: str):
    key = st.session_state.get("openai_api_key", "").strip()
    if not key:
        return None, "Sem chave de API. A análise local continua disponível."
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        response = client.responses.create(model="gpt-5", input=prompt)
        txt = getattr(response, "output_text", None)
        if txt:
            return txt, None
        return None, "A API respondeu sem texto utilizável."
    except Exception as e:
        return None, f"Falha ao chamar a API: {e}"

# ─── SIDEBAR ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 12px 0 16px 0;">
        <div style="font-family:'Rajdhani',sans-serif; font-size:1.5rem; font-weight:700;
                    background: linear-gradient(135deg, #00d4ff, #bf00ff);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    letter-spacing:0.12em; text-transform:uppercase;">
            8-GAME LAB
        </div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:0.65rem;
                    color:rgba(0,212,255,0.5); letter-spacing:0.2em; margin-top:2px;">
            PROFILE ANALYSIS SYSTEM
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navegação",
        ["🏠  Dashboard", "🎴  Modalidades", "👥  Oponentes", "⚔️  Comparação"],
        index=0,
        label_visibility="collapsed"
    )
    page = page.split("  ", 1)[1]  # strip icon prefix

    st.divider()
    st.markdown('<div style="font-family:Rajdhani,sans-serif; font-size:0.85rem; font-weight:700; color:rgba(0,212,255,0.8); letter-spacing:0.1em; text-transform:uppercase; margin-bottom:6px;">⚙ IA (OpenAI)</div>', unsafe_allow_html=True)
    st.text_input("OpenAI API Key", key="openai_api_key", type="password", label_visibility="collapsed", placeholder="sk-...")
    st.caption("Sem chave, o app usa a leitura local heurística. Menos mágica, mais confiável.")

# ─── GLOBAL HEADER ──────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="hero-title">8-Game Poker Analysis Lab</div>
<div class="hero-sub">♠ ♥ ♦ ♣ &nbsp;·&nbsp; Hero: {hero.upper()} &nbsp;·&nbsp; Session Active</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("🃏  Mãos únicas",   summary_data["unique_hands"])
c2.metric("📂  Arquivos",       summary_data["files_used"])
c3.metric("👥  Oponentes",      summary_data["unique_opponents"])
c4.metric("🎴  Modalidades",    len(hero_profiles))

st.markdown("<hr style='margin:1.2rem 0 1.5rem 0;'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":

    st.markdown('<div class="section-header">📊 Visão geral — ' + hero + '</div>', unsafe_allow_html=True)

    # Variant cards grid
    cols = st.columns(2)
    for i, v in enumerate(hero_profiles):
        grad = variant_gradient(v["variant"])
        icon = VARIANT_ICONS.get(v["variant"], "🎴")
        with cols[i % 2]:
            st.markdown(f"""
            <div class="variant-card">
                <div class="variant-card-top">
                    <div class="variant-card-name">{icon} {v['variant']}</div>
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:rgba(255,255,255,0.4);">{v['hands']}m / {v['tournaments']}t</div>
                </div>
                <div class="variant-profile-tag">{v['profile']}</div>
                {stat_bar('VPIP', v['vpip_pct'], color='#00d4ff')}
                {stat_bar('1ª Agressão', v['first_aggr_pct'], color='#bf00ff')}
                {stat_bar('Win %', v['win_pct'], color='#00ffa0')}
                {stat_bar('Fold %', v['fold_pct'], color='#ff6b35')}
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">🏆 Top oponentes por volume</div>', unsafe_allow_html=True)

    opp_df = pd.DataFrame(opponent_profiles).sort_values(["hands","tournaments"], ascending=False).head(25)
    st.dataframe(
        opp_df[["name","hands","tournaments","variants_seen","top_variant","vpip_pct","first_aggr_pct","showdown_pct","showdown_win_pct","confidence"]],
        use_container_width=True, hide_index=True
    )

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: MODALIDADES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Modalidades":

    st.markdown('<div class="section-header">🎴 Modalidades da Hero</div>', unsafe_allow_html=True)

    variants = [x["variant"] for x in hero_profiles]
    icons_list = [VARIANT_ICONS.get(v, "🎴") for v in variants]
    pill_html = "".join([
        f'<span class="variant-pill" id="pill_{i}">{icons_list[i]} {v}</span>'
        for i, v in enumerate(variants)
    ])

    selected = st.selectbox(
        "Escolha a modalidade",
        variants,
        format_func=lambda v: f"{VARIANT_ICONS.get(v, '🎴')}  {v}"
    )

    v = next(x for x in hero_profiles if x["variant"] == selected)
    grad = variant_gradient(v["variant"])
    icon = VARIANT_ICONS.get(v["variant"], "🎴")

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(15,25,55,0.9), rgba(8,15,35,0.95));
                    border: 1px solid rgba(0,212,255,0.25); border-radius:18px; padding:20px; margin-bottom:12px;">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:14px;">
                <div style="width:52px;height:52px;border-radius:12px;background:linear-gradient({grad});
                            display:flex;align-items:center;justify-content:center;font-size:1.6rem;
                            box-shadow:0 4px 20px rgba(0,0,0,0.4);">{icon}</div>
                <div>
                    <div style="font-family:'Rajdhani',sans-serif;font-size:1.2rem;font-weight:700;
                                color:#ffffff;letter-spacing:0.06em;">{v['variant']}</div>
                    <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;
                                color:rgba(0,212,255,0.7);">{v['profile']}</div>
                </div>
            </div>
            {stat_bar('VPIP', v['vpip_pct'], color='#00d4ff')}
            {stat_bar('1ª Agressão', v['first_aggr_pct'], color='#bf00ff')}
            {stat_bar('Agg Rate', v['agg_rate_pct'], color='#ff6b35')}
            {stat_bar('Showdown', v['showdown_pct'], color='#ffc800')}
            {stat_bar('Showdown Win', v['showdown_win_pct'], color='#00ffa0')}
            {stat_bar('Win Total', v['win_pct'], color='#00ffa0')}
            {stat_bar('Vitórias sem Showdown', v['unshown_win_pct'], color='#64c8ff')}
            {stat_bar('Fold %', v['fold_pct'], color='#ff5050')}
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Mãos", v["hands"])
        m2.metric("Torneios", v["tournaments"])
        m3.metric("VPIP", f"{v['vpip_pct']}%")
        m4.metric("1ª Agressão", f"{v['first_aggr_pct']}%")

        metrics_df = pd.DataFrame([
            {"Métrica": "VPIP",                  "Valor": v["vpip_pct"]},
            {"Métrica": "1ª agressão",            "Valor": v["first_aggr_pct"]},
            {"Métrica": "Agg rate",               "Valor": v["agg_rate_pct"]},
            {"Métrica": "Showdown",               "Valor": v["showdown_pct"]},
            {"Métrica": "Showdown win",           "Valor": v["showdown_win_pct"]},
            {"Métrica": "Win total",              "Valor": v["win_pct"]},
            {"Métrica": "Vitórias sem showdown",  "Valor": v["unshown_win_pct"]},
            {"Métrica": "Fold",                   "Valor": v["fold_pct"]},
        ])
        st.bar_chart(metrics_df.set_index("Métrica"))

    with right:
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:0.85rem;font-weight:700;color:rgba(0,212,255,0.8);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">Prompt para IA</div>', unsafe_allow_html=True)
        prompt = st.text_area("Prompt para IA", value=variant_prompt(v), height=260, key=f"var_{selected}", label_visibility="collapsed")
        a, b = st.columns(2)
        if a.button("📊 Análise local", use_container_width=True):
            st.session_state["variant_analysis"] = local_analysis_variant(v)
        if b.button("🤖 Analisar com IA", use_container_width=True):
            txt, err = try_openai(prompt)
            st.session_state["variant_analysis"] = txt or err

        st.markdown('<div class="section-header" style="font-size:1rem;">Saída</div>', unsafe_allow_html=True)
        analysis = st.session_state.get("variant_analysis", "")
        if analysis:
            st.markdown(f'<div class="analysis-box">{analysis}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:rgba(160,200,255,0.4);font-family:Share Tech Mono,monospace;font-size:0.8rem;">Nenhuma análise gerada ainda.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: OPONENTES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Oponentes":

    st.markdown('<div class="section-header">👥 Scouting de Oponentes</div>', unsafe_allow_html=True)

    col_search, col_conf = st.columns([2, 1])
    with col_search:
        search = st.text_input("🔍  Buscar nick", placeholder="Digite para filtrar...", label_visibility="collapsed")
    with col_conf:
        conf = st.selectbox("Confiança", ["todas", "alta", "média", "baixa"], index=0, label_visibility="collapsed")

    filtered = opponent_profiles
    if search.strip():
        q = search.strip().lower()
        filtered = [o for o in filtered if q in o["name"].lower()]
    if conf != "todas":
        filtered = [o for o in filtered if o["confidence"] == conf]

    if not filtered:
        st.warning("Nenhum oponente encontrado.")
    else:
        # ── Card grid ──
        selected_opp = st.session_state.get("selected_opp", filtered[0]["name"])
        # Make sure selected is still in filtered
        if not any(o["name"] == selected_opp for o in filtered):
            selected_opp = filtered[0]["name"]

        # Build card grid HTML
        cards_html = '<div class="opp-grid">'
        for o in filtered:
            bg_col, accent_col, emoji = get_avatar(o["name"])
            badge = conf_badge(o["confidence"])
            is_sel = "selected" if o["name"] == selected_opp else ""
            initials = o["name"][:2].upper()
            cards_html += f"""
            <div class="opp-card {is_sel}" onclick="
                window.parent.document.querySelectorAll('.opp-card').forEach(c=>c.classList.remove('selected'));
                this.classList.add('selected');
            " style="border-color: {'rgba(0,212,255,0.6)' if is_sel else 'rgba(255,255,255,0.08)'}">
                <div class="opp-card-accent" style="background:linear-gradient({variant_gradient(o['top_variant'])})"></div>
                <div class="opp-avatar" style="background:{bg_col}; color:{accent_col};">{emoji}</div>
                <div class="opp-name">{o['name']}</div>
                <div class="opp-stats-mini">
                    VPIP {o['vpip_pct']}% · W {o['win_pct']}%<br>
                    {o['variants_seen']}/8 vars · {o['hands']}m
                </div>
                {badge}
            </div>"""
        cards_html += "</div>"
        st.markdown(cards_html, unsafe_allow_html=True)

        # Selectbox as the real state controller (hidden visually with the cards above)
        name = st.selectbox(
            "Escolha o oponente",
            [o["name"] for o in filtered],
            index=next((i for i, o in enumerate(filtered) if o["name"] == selected_opp), 0),
            key="opp_selectbox"
        )
        st.session_state["selected_opp"] = name
        o = next(x for x in filtered if x["name"] == name)

        # ── Detail panel ──
        bg_col, accent_col, emoji = get_avatar(o["name"])
        st.markdown(f"""
        <div class="player-panel">
            <div class="player-panel-header">
                <div class="player-panel-avatar" style="background:{bg_col}; color:{accent_col};">{emoji}</div>
                <div>
                    <div class="player-panel-name">{o['name']}</div>
                    <div class="player-panel-label">{o['label']}</div>
                    <div style="margin-top:4px;">{conf_badge(o['confidence'])}
                        <span style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                            color:rgba(160,200,255,0.6);margin-left:8px;">
                            {o['variants_seen']}/8 vars · {o['hands']} mãos · {o['tournaments']} torneios
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        left, right = st.columns([1.1, 1])

        with left:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("VPIP",         f"{o['vpip_pct']}%")
            m2.metric("1ª Agressão",  f"{o['first_aggr_pct']}%")
            m3.metric("Showdown",     f"{o['showdown_pct']}%")
            m4.metric("SD Win",       f"{o['showdown_win_pct']}%")

            st.markdown(f"""
            <div style="background:rgba(0,5,20,0.6);border:1px solid rgba(0,212,255,0.12);
                        border-radius:12px;padding:14px;margin:10px 0;">
                {stat_bar('VPIP', o['vpip_pct'], color='#00d4ff')}
                {stat_bar('1ª Agressão', o['first_aggr_pct'], color='#bf00ff')}
                {stat_bar('Agg Rate', o['agg_rate_pct'], color='#ff6b35')}
                {stat_bar('Showdown', o['showdown_pct'], color='#ffc800')}
                {stat_bar('Showdown Win', o['showdown_win_pct'], color='#00ffa0')}
                {stat_bar('Win Total', o['win_pct'], color='#00ffa0')}
                {stat_bar('Vitórias sem Showdown', o['unshown_win_pct'], color='#64c8ff')}
                {stat_bar('Fold %', o['fold_pct'], color='#ff5050')}
            </div>
            """, unsafe_allow_html=True)

            metrics_df = pd.DataFrame([
                {"Métrica": "VPIP",                 "Valor": o["vpip_pct"]},
                {"Métrica": "1ª agressão",           "Valor": o["first_aggr_pct"]},
                {"Métrica": "Agg rate",              "Valor": o["agg_rate_pct"]},
                {"Métrica": "Showdown",              "Valor": o["showdown_pct"]},
                {"Métrica": "Showdown win",          "Valor": o["showdown_win_pct"]},
                {"Métrica": "Win total",             "Valor": o["win_pct"]},
                {"Métrica": "Vitórias sem showdown", "Valor": o["unshown_win_pct"]},
                {"Métrica": "Fold",                  "Valor": o["fold_pct"]},
            ])
            st.bar_chart(metrics_df.set_index("Métrica"))

            st.markdown('<div class="section-header" style="font-size:0.9rem;">Mix por Modalidade</div>', unsafe_allow_html=True)
            mix_df = pd.DataFrame([{"Modalidade": k, "Mãos": v} for k, v in o["variant_mix"].items()])
            st.dataframe(mix_df, use_container_width=True, hide_index=True)

        with right:
            st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:0.85rem;font-weight:700;color:rgba(0,212,255,0.8);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">Prompt para IA</div>', unsafe_allow_html=True)
            prompt = st.text_area("Prompt para IA", value=opponent_prompt(o), height=300, key=f"opp_{name}", label_visibility="collapsed")
            a, b = st.columns(2)
            if a.button("📊 Análise local", use_container_width=True, key="opp_local"):
                st.session_state["opp_analysis"] = local_analysis_opponent(o)
            if b.button("🤖 Analisar com IA", use_container_width=True, key="opp_ai"):
                txt, err = try_openai(prompt)
                st.session_state["opp_analysis"] = txt or err

            st.markdown('<div class="section-header" style="font-size:1rem;">Saída</div>', unsafe_allow_html=True)
            analysis = st.session_state.get("opp_analysis", "")
            if analysis:
                st.markdown(f'<div class="analysis-box">{analysis}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:rgba(160,200,255,0.4);font-family:Share Tech Mono,monospace;font-size:0.8rem;">Nenhuma análise gerada ainda.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: COMPARAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Comparação":

    st.markdown('<div class="section-header">⚔️ Comparação: Hero vs Vilão</div>', unsafe_allow_html=True)

    search = st.text_input("🔍  Buscar nick para comparar", placeholder="Digite para filtrar...", label_visibility="collapsed")
    filtered = comparison_profiles
    if search.strip():
        q = search.strip().lower()
        filtered = [c for c in filtered if q in c["name"].lower()]

    if not filtered:
        st.warning("Nenhum jogador encontrado.")
    else:
        name = st.selectbox(
            "Escolha o jogador",
            [c["name"] for c in filtered],
            format_func=lambda n: f"{''.join(get_avatar(n)[2])}  {n}"
        )
        c = next(x for x in filtered if x["name"] == name)
        h = c["hero_overall"]
        o = c["opponent_overall"]

        # Duel header
        hero_bg, hero_accent, hero_emoji = get_avatar(hero)
        opp_bg, opp_accent, opp_emoji = get_avatar(name)

        st.markdown(f"""
        <div class="duel-header">
            <div style="text-align:center;">
                <div style="width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#00d4ff,#0055ff);
                            display:flex;align-items:center;justify-content:center;font-size:1.4rem;
                            margin:0 auto 6px auto;border:2px solid rgba(0,212,255,0.5);">♠</div>
                <div class="duel-name" style="color:#00d4ff;">{hero.upper()}</div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:rgba(0,212,255,0.6);">HERO</div>
            </div>
            <div class="duel-vs">VS</div>
            <div style="text-align:center;">
                <div style="width:52px;height:52px;border-radius:50%;background:{opp_bg};
                            display:flex;align-items:center;justify-content:center;font-size:1.4rem;
                            margin:0 auto 6px auto;border:2px solid {opp_accent}88;">{opp_emoji}</div>
                <div class="duel-name" style="color:{opp_accent};">{name}</div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:rgba(160,200,255,0.5);">VILÃO</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f'<div class="section-header" style="font-size:1rem;color:#00d4ff;">♠ {hero}</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.15);
                        border-radius:12px;padding:14px;">
                {stat_bar('VPIP', h['vpip_pct'], color='#00d4ff')}
                {stat_bar('1ª Agressão', h['first_aggr_pct'], color='#bf00ff')}
                {stat_bar('Agg Rate', h['agg_rate_pct'], color='#ff6b35')}
                {stat_bar('Showdown', h['showdown_pct'], color='#ffc800')}
                {stat_bar('Showdown Win', h['showdown_win_pct'], color='#00ffa0')}
                {stat_bar('Win Total', h['win_pct'], color='#00ffa0')}
                {stat_bar('Fold %', h['fold_pct'], color='#ff5050')}
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(pd.DataFrame([
                ["Mãos",        h["hands"]],
                ["Torneios",    h["tournaments"]],
                ["VPIP",        f'{h["vpip_pct"]}%'],
                ["1ª agressão", f'{h["first_aggr_pct"]}%'],
                ["Agg rate",    f'{h["agg_rate_pct"]}%'],
                ["Showdown",    f'{h["showdown_pct"]}%'],
                ["Showdown win",f'{h["showdown_win_pct"]}%'],
                ["Win total",   f'{h["win_pct"]}%'],
                ["Fold",        f'{h["fold_pct"]}%'],
            ], columns=["Métrica","Valor"]), use_container_width=True, hide_index=True)

        with col2:
            st.markdown(f'<div class="section-header" style="font-size:1rem;color:{opp_accent};">{opp_emoji} {name}</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:{opp_bg.replace('0.25','0.04')};border:1px solid {opp_accent}33;
                        border-radius:12px;padding:14px;">
                {stat_bar('VPIP', o['vpip_pct'], color=opp_accent)}
                {stat_bar('1ª Agressão', o['first_aggr_pct'], color=opp_accent)}
                {stat_bar('Agg Rate', o['agg_rate_pct'], color=opp_accent)}
                {stat_bar('Showdown', o['showdown_pct'], color=opp_accent)}
                {stat_bar('Showdown Win', o['showdown_win_pct'], color='#00ffa0')}
                {stat_bar('Win Total', o['win_pct'], color='#00ffa0')}
                {stat_bar('Fold %', o['fold_pct'], color='#ff5050')}
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(pd.DataFrame([
                ["Mãos",        o["hands"]],
                ["Torneios",    o["tournaments"]],
                ["VPIP",        f'{o["vpip_pct"]}%'],
                ["1ª agressão", f'{o["first_aggr_pct"]}%'],
                ["Agg rate",    f'{o["agg_rate_pct"]}%'],
                ["Showdown",    f'{o["showdown_pct"]}%'],
                ["Showdown win",f'{o["showdown_win_pct"]}%'],
                ["Win total",   f'{o["win_pct"]}%'],
                ["Fold",        f'{o["fold_pct"]}%'],
            ], columns=["Métrica","Valor"]), use_container_width=True, hide_index=True)

        st.markdown('<div class="section-header">📊 Comparação por modalidade compartilhada</div>', unsafe_allow_html=True)
        if c["variant_comparison"]:
            st.dataframe(pd.DataFrame(c["variant_comparison"]), use_container_width=True, hide_index=True)
        else:
            st.info("Sem comparação por modalidade disponível.")

        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:0.85rem;font-weight:700;color:rgba(0,212,255,0.8);letter-spacing:0.1em;text-transform:uppercase;margin:12px 0 6px 0;">Prompt para IA</div>', unsafe_allow_html=True)
        prompt = st.text_area("Prompt para IA", value=compare_prompt(c), height=260, key=f"cmp_{name}", label_visibility="collapsed")
        a, b = st.columns(2)
        if a.button("📊 Análise local", use_container_width=True, key="cmp_local"):
            st.session_state["cmp_analysis"] = local_analysis_compare(c)
        if b.button("🤖 Analisar com IA", use_container_width=True, key="cmp_ai"):
            txt, err = try_openai(prompt)
            st.session_state["cmp_analysis"] = txt or err

        st.markdown('<div class="section-header" style="font-size:1rem;">Saída</div>', unsafe_allow_html=True)
        analysis = st.session_state.get("cmp_analysis", "")
        if analysis:
            st.markdown(f'<div class="analysis-box">{analysis}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:rgba(160,200,255,0.4);font-family:Share Tech Mono,monospace;font-size:0.8rem;">Nenhuma análise gerada ainda.</div>', unsafe_allow_html=True)
