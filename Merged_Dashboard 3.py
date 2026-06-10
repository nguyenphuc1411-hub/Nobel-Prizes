"""
Nobel Laureates Dashboard — MERGED
Merges Web.py (Plotly, tabbed UI) + Gan_Final.py (advanced matplotlib/seaborn charts)

Run: streamlit run Merged_Dashboard.py
The SDnobel dataset is embedded directly in this file — no external data file is required.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Nobel Laureates Dashboard", page_icon="🏆",
                   layout="wide", initial_sidebar_state="expanded")

plt.rcParams.update({
    "figure.facecolor":  "none",
    "axes.facecolor":    "none",
    "savefig.facecolor": "none",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         False,
})

# ── CSS — VIBRANT THEME (purple → pink → orange) ────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"], * { font-family: 'Inter', sans-serif !important; }
    /* Don't force the font onto icons — keep Material Symbols, otherwise the expander arrow renders as the text "keyboard_arrow_right" */
    [class*="material-icons"], [class*="material-symbols"],
    [data-testid="stExpanderToggleIcon"], .stExpander [data-testid="stIconMaterial"],
    span[data-testid="stIconMaterial"], .material-symbols-outlined, .material-symbols-rounded {
        font-family: 'Material Symbols Rounded','Material Symbols Outlined','Material Icons' !important;
    }
    .stApp { background: #f3f1fe; color: #111827; }
    [data-testid="stSidebar"] {
        background:#ffffff; border-right:1px solid #ece8fd;
        box-shadow: 4px 0 24px rgba(139,92,246,0.06);
    }
    [data-testid="stSidebar"] * { color:#111827 !important; }

    /* ── HEADER: vivid purple → pink → orange gradient ── */
    .main-header {
        background: linear-gradient(110deg,#7c3aed 0%,#c026d3 25%,#ec4899 45%,#f43f5e 65%,#fb923c 85%,#f59e0b 100%);
        border-radius:20px; padding:32px 40px; margin-bottom:28px;
        box-shadow: 0 20px 45px -12px rgba(192,38,211,0.45),
                    0 8px 20px -8px rgba(244,63,94,0.35);
    }
    .main-header h1 {
        color:#fff; margin:0; font-size:2.6rem; font-weight:800;
        letter-spacing:-0.02em; text-shadow:0 2px 12px rgba(0,0,0,0.15);
    }
    .main-header p  { color:rgba(255,255,255,0.92); margin:10px 0 0; font-size:1rem; }
    .header-badge {
        display:inline-block; background:rgba(255,255,255,0.22);
        border:1px solid rgba(255,255,255,0.45); border-radius:999px;
        color:#fff; font-size:0.72rem; font-weight:700; letter-spacing:0.08em;
        text-transform:uppercase; padding:6px 16px; margin:0 8px 14px 0;
        backdrop-filter: blur(4px);
    }

    /* ── METRIC CARDS: one bright gradient per card, white text ── */
    [data-testid="metric-container"], div[data-testid="stMetric"] {
        border:none; border-radius:16px; padding:18px 22px;
        box-shadow:0 12px 28px -10px rgba(99,102,241,0.45);
        background:linear-gradient(135deg,#6366f1,#8b5cf6);
    }
    div[data-testid="stColumn"]:nth-of-type(1) div[data-testid="stMetric"],
    div[data-testid="column"]:nth-of-type(1)   div[data-testid="stMetric"] {
        background:linear-gradient(135deg,#7c3aed,#a78bfa);
        box-shadow:0 12px 28px -10px rgba(124,58,237,0.55);
    }
    div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stMetric"],
    div[data-testid="column"]:nth-of-type(2)   div[data-testid="stMetric"] {
        background:linear-gradient(135deg,#059669,#2dd4bf);
        box-shadow:0 12px 28px -10px rgba(16,185,129,0.55);
    }
    div[data-testid="stColumn"]:nth-of-type(3) div[data-testid="stMetric"],
    div[data-testid="column"]:nth-of-type(3)   div[data-testid="stMetric"] {
        background:linear-gradient(135deg,#f59e0b,#fbbf24);
        box-shadow:0 12px 28px -10px rgba(245,158,11,0.55);
    }
    div[data-testid="stColumn"]:nth-of-type(4) div[data-testid="stMetric"],
    div[data-testid="column"]:nth-of-type(4)   div[data-testid="stMetric"] {
        background:linear-gradient(135deg,#ec4899,#fb7185);
        box-shadow:0 12px 28px -10px rgba(236,72,153,0.55);
    }
    div[data-testid="stColumn"]:nth-of-type(5) div[data-testid="stMetric"],
    div[data-testid="column"]:nth-of-type(5)   div[data-testid="stMetric"] {
        background:linear-gradient(135deg,#0ea5e9,#22d3ee);
        box-shadow:0 12px 28px -10px rgba(14,165,233,0.55);
    }
    [data-testid="stMetricValue"]  { color:#ffffff !important; font-size:2.2rem !important; font-weight:800 !important; }
    [data-testid="stMetricLabel"]  { color:rgba(255,255,255,0.95) !important; font-size:0.8rem !important;
                                     font-weight:700 !important; text-transform:uppercase; letter-spacing:0.08em; }

    hr { border-color:#e6e1fb !important; }

    /* ── TABS: gradient pill for the active tab ── */
    .stTabs [data-baseweb="tab-list"] {
        background:#ffffff; border-radius:12px; padding:5px;
        box-shadow:0 4px 16px rgba(139,92,246,0.10);
    }
    .stTabs [data-baseweb="tab"]      { color:#4b5563; border-radius:9px; font-weight:600; }
    .stTabs [aria-selected="true"]    {
        background:linear-gradient(110deg,#8b5cf6,#ec4899,#f97316) !important;
        color:#ffffff !important;
        box-shadow:0 4px 14px rgba(236,72,153,0.45);
    }
    .stTabs [aria-selected="true"] p  { color:#ffffff !important; }

    .stPlotlyChart {
        background:#ffffff; border-radius:16px; padding:10px;
        border:1px solid #ece8fd; box-shadow:0 8px 24px rgba(139,92,246,0.10);
    }
    .section-label {
        color:#111827; font-size:0.75rem; text-transform:uppercase;
        letter-spacing:0.1em; margin:12px 0 4px; font-weight:700;
    }

    /* ── Buttons (Show more, Download): gradient ── */
    .stButton > button, .stDownloadButton > button {
        background:linear-gradient(110deg,#8b5cf6,#ec4899,#f97316) !important;
        color:#ffffff !important; border:none !important; border-radius:12px !important;
        font-weight:700 !important; padding:10px 22px !important;
        box-shadow:0 8px 20px -6px rgba(236,72,153,0.5) !important;
        transition: transform .12s ease, box-shadow .12s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow:0 12px 26px -6px rgba(236,72,153,0.6) !important;
    }
    .stButton > button p, .stDownloadButton > button p { color:#ffffff !important; }

    /* ── Force dark text color on every widget in the main area (fixes faded text) ── */
    .stApp .main p, .stApp .main span:not([data-testid="stIconMaterial"]), .stApp .main label,
    .stApp .main li, .stApp .main div[data-baseweb] { color:#111827 !important; }

    /* Widget labels (Select Chart, Include categories, ...) */
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p,
    .stRadio > label, .stCheckbox > label,
    .stMultiSelect label, .stSelectbox label,
    .stSlider label, .stTextInput label {
        color:#111827 !important; font-weight:600 !important; opacity:1 !important;
    }

    /* Radio / checkbox options */
    .stRadio div[role="radiogroup"] label,
    .stRadio div[role="radiogroup"] label p,
    .stCheckbox label p {
        color:#111827 !important; opacity:1 !important;
    }

    /* Multiselect: selected tags + select box */
    .stMultiSelect [data-baseweb="tag"] {
        background:linear-gradient(110deg,#8b5cf6,#ec4899) !important;
        border-radius:999px !important;
    }
    .stMultiSelect [data-baseweb="tag"] span { color:#ffffff !important; }
    .stMultiSelect [data-baseweb="select"] * { color:#111827 !important; }

    /* Subheader / caption trong main */
    .stApp .main h1, .stApp .main h2, .stApp .main h3,
    .stApp .main h4, .stApp .main h5 { color:#111827 !important; }
    .stApp .main [data-testid="stCaptionContainer"],
    .stApp .main [data-testid="stCaptionContainer"] * { color:#475569 !important; }

    /* ── Keep metric-card text white (must come AFTER the forced-dark rules) ── */
    .stApp [data-testid="stMetric"] p, .stApp [data-testid="stMetric"] span,
    .stApp [data-testid="stMetric"] div, .stApp [data-testid="stMetric"] label,
    .stApp [data-testid="metric-container"] p, .stApp [data-testid="metric-container"] span,
    .stApp [data-testid="metric-container"] div, .stApp [data-testid="metric-container"] label {
        color:#ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING — the SDnobel dataset is EMBEDDED in this file (gzip + base64)
# No external SDnobel.xls/.csv file is needed. If a data file is placed next to
# the script anyway, the external file takes priority (handy for future updates).
# ══════════════════════════════════════════════════════════════════════════════
import gzip, base64, io

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

_EMBEDDED_SDNOBEL_B64 = """\
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
K58EAA=="""

def _read_any(path_or_buf, name=""):
    n = name.lower()
    if n.endswith((".xls", ".xlsx")):
        return pd.read_excel(path_or_buf)
    return pd.read_csv(path_or_buf)

def _normalize(d):
    d = d.copy()
    d.columns = [str(c).strip().lower() for c in d.columns]
    if "age" in d.columns and "age_at_award" not in d.columns:
        d = d.rename(columns={"age": "age_at_award"})
    return d

@st.cache_data(show_spinner=False)
def load_data():
    # 1) Prefer an external file if present (makes swapping data easy)
    candidates = ["SDnobel.xlsx", "SDnobel.xls", "SDnobel.csv",
                  "SDnobel.XLSX", "SDnobel.XLS", "SDnobel.CSV"]
    found = next((os.path.join(SCRIPT_DIR, f)
                 for f in candidates if os.path.exists(os.path.join(SCRIPT_DIR, f))), None)
    if found:
        return _normalize(_read_any(found, name=found)), os.path.basename(found)
    # 2) Default: use the data embedded in this file
    raw = gzip.decompress(base64.b64decode(_EMBEDDED_SDNOBEL_B64))
    return _normalize(pd.read_csv(io.BytesIO(raw))), "embedded SDnobel data"

st.markdown("""
<div class="main-header">
    <span class="header-badge">Python · Data Science</span>
    <span class="header-badge">Plotly Interactive</span>
    <h1>🏆 Nobel Laureates Dashboard</h1>
    <p>Explore Nobel Prize data — 1901 to present. Tune the filters — every chart updates live.</p>
</div>""", unsafe_allow_html=True)

with st.spinner("Loading data..."):
    df, src_name = load_data()

if df is None or df.empty:
    st.error("No data available."); st.stop()

st.sidebar.success(f"Loaded {src_name} — {len(df):,} rows")

# Helper: shared age column (Web.py uses age_at_award, Gan_Final uses age)
if "age_at_award" in df.columns and "age" not in df.columns:
    df["age"] = pd.to_numeric(df["age_at_award"], errors="coerce")

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — GLOBAL FILTERS
# ══════════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("## ⚙️ Filters")
min_year, max_year = int(df["year"].min()), int(df["year"].max())
selected_years      = st.sidebar.slider("📅 Year Range:", min_year, max_year, (min_year, max_year))
categories          = sorted(df["category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect("🎯 Category:", categories, default=categories)
laureate_types      = df["laureate_type"].dropna().unique().tolist() if "laureate_type" in df.columns else []
selected_types      = st.sidebar.multiselect("👤 Laureate Type:", laureate_types, default=laureate_types) if laureate_types else laureate_types
genders             = df["sex"].dropna().unique().tolist()
selected_genders    = st.sidebar.multiselect("⚧ Gender:", genders, default=genders)
top_n               = st.sidebar.slider("🌍 Top N Countries:", 5, 30, 15)

mask = (
    (df["year"] >= selected_years[0]) & (df["year"] <= selected_years[1]) &
    (df["category"].isin(selected_categories)) &
    (df["sex"].isin(selected_genders))
)
if laureate_types:
    mask &= df["laureate_type"].isin(selected_types)
filtered_df = df[mask].copy()

# ══════════════════════════════════════════════════════════════════════════════
# THEME (Plotly helpers from Web.py)
# ══════════════════════════════════════════════════════════════════════════════
LIGHT_BG   = "#ffffff"
PLOT_BG    = "#faf9ff"
GRID_COL   = "#ece8fd"
TEXT_COL   = "#111827"
BAR_BORDER = dict(color="#ffffff", width=1.5)
BLUE_MAIN  = "#8b5cf6"
AMBER      = "#f59e0b"
PINK       = "#ec4899"
CAT_PALETTE = ["#8b5cf6","#ec4899","#f97316","#10b981","#06b6d4","#f43f5e"]
AXIS_FONT  = dict(color=TEXT_COL, family="Inter", size=12)
TICK_FONT  = dict(color=TEXT_COL, family="Inter", size=11)

def base_layout(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(color=TEXT_COL, size=14, family="Inter"), x=0),
        paper_bgcolor=LIGHT_BG, plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT_COL, family="Inter"),
        xaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL, linecolor=GRID_COL,
                   tickfont=TICK_FONT, title_font=AXIS_FONT),
        yaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL, linecolor=GRID_COL,
                   tickfont=TICK_FONT, title_font=AXIS_FONT),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_COL, family="Inter")),
        margin=dict(t=50, b=40, l=40, r=20),
    )
    fig.update_xaxes(title_font=dict(color="#111827", family="Inter", size=12),
                     tickfont=dict(color="#111827", family="Inter", size=11))
    fig.update_yaxes(title_font=dict(color="#111827", family="Inter", size=12),
                     tickfont=dict(color="#111827", family="Inter", size=11))
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# TABS — an "Advanced" tab holds all of Gan_Final's charts
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(
    ["📈 Overview","🌍 Geography","👤 Demographics"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW  (Web.py)
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    trend = filtered_df.groupby(["year","category"]).size().reset_index(name="Number of Awards")
    fig_area = px.area(trend, x="year", y="Number of Awards", color="category",
                       labels={"year":"Year","category":"Category"},
                       color_discrete_sequence=CAT_PALETTE)
    fig_area.update_traces(line=dict(width=1.5),
        hovertemplate="Category: %{fullData.name}<br>Year: %{x}<br>Number of Awards: %{y}<extra></extra>")
    base_layout(fig_area, "📈 Awards Trend by Year")
    fig_area.update_layout(legend_title_text="Category", xaxis_title="Year",
                           yaxis_title="Number of Awards",
                           xaxis=dict(gridcolor=GRID_COL, tickmode="linear", dtick=10))
    fig_area.update_xaxes(title_font_color="#111827", tickfont_color="#111827")
    fig_area.update_yaxes(title_font_color="#111827", tickfont_color="#111827")
    st.plotly_chart(fig_area, use_container_width=True)

    st.markdown("<p class='section-label'>Breakdown by category &amp; laureate type</p>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 1])

    with col_a:
        cat_data = filtered_df["category"].value_counts().reset_index()
        cat_data.columns = ["Category","Count"]
        cat_data = cat_data.sort_values("Count")
        n_cat = len(cat_data)
        cat_colors = CAT_PALETTE[:n_cat] if n_cat <= len(CAT_PALETTE) \
                     else pc.sample_colorscale("Turbo", [i/max(n_cat-1,1) for i in range(n_cat)])
        fig_cat = go.Figure(go.Bar(
            x=cat_data["Count"], y=cat_data["Category"], orientation="h",
            text=cat_data["Count"], textposition="outside",
            textfont=dict(color=TEXT_COL, size=12, family="Inter"),
            marker=dict(color=cat_colors, line=BAR_BORDER)))
        base_layout(fig_cat, "📚 Awards by Category")
        fig_cat.update_layout(xaxis_title="Number of Awards", yaxis_title="",
                              xaxis=dict(range=[0, cat_data["Count"].max()*1.2], gridcolor=GRID_COL))
        fig_cat.update_xaxes(title_font_color="#111827", tickfont_color="#111827")
        fig_cat.update_yaxes(title_font_color="#111827", tickfont_color="#111827")
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_b:
        if "laureate_type" in filtered_df.columns:
            type_data = filtered_df.groupby("laureate_type").size().reset_index(name="Count")
            fig_type = go.Figure(go.Bar(
                x=type_data["laureate_type"], y=type_data["Count"],
                text=type_data["Count"], textposition="outside",
                textfont=dict(color=TEXT_COL, size=13, family="Inter"),
                marker=dict(color=[BLUE_MAIN if t=="Individual" else AMBER for t in type_data["laureate_type"]],
                            line=BAR_BORDER)))
            base_layout(fig_type, "👥 Type")
            fig_type.update_layout(xaxis_title="", yaxis_title="Number of Laureates",
                                   yaxis=dict(gridcolor=GRID_COL, range=[0, type_data["Count"].max()*1.2]),
                                   showlegend=False)
            fig_type.update_xaxes(title_font_color="#111827", tickfont_color="#111827")
            fig_type.update_yaxes(title_font_color="#111827", tickfont_color="#111827")
            st.plotly_chart(fig_type, use_container_width=True)

    st.markdown("<p class='section-label'>Awards distribution over time</p>", unsafe_allow_html=True)
    decade_df = filtered_df.copy()
    decade_df["decade"] = (decade_df["year"] // 10 * 10)
    decade_cat = decade_df.groupby(["decade","category"]).size().reset_index(name="Number of Awards")
    fig_dec = px.bar(decade_cat, x="decade", y="Number of Awards", color="category",
                     barmode="stack", color_discrete_sequence=CAT_PALETTE,
                     labels={"decade":"Year","category":"Category"})
    fig_dec.update_traces(marker_line_color="#ffffff", marker_line_width=0.8,
        hovertemplate="Category: %{fullData.name}<br>Year: %{x}<br>Number of Awards: %{y}<extra></extra>")
    base_layout(fig_dec, "📊 Awards by Decade & Category")
    fig_dec.update_layout(xaxis_title="Year", yaxis_title="Number of Awards", legend_title_text="Category",
                          xaxis=dict(tickmode="linear", dtick=10, tickangle=45, tickformat="d", gridcolor=GRID_COL),
                          yaxis=dict(gridcolor=GRID_COL), margin=dict(t=50, b=80, l=40, r=20))
    fig_dec.update_xaxes(title_font_color="#111827", tickfont_color="#111827")
    fig_dec.update_yaxes(title_font_color="#111827", tickfont_color="#111827")
    st.plotly_chart(fig_dec, use_container_width=True)

    # ── KEY METRICS (moved from the top of the page into the Overview tab) ──
    st.markdown("---")
    st.markdown("### 📊 Key Numbers")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Awards",     f"{len(filtered_df):,}")
    c2.metric("Individuals",      f"{(filtered_df.get('laureate_type','')=='Individual').sum():,}")
    c3.metric("Organizations",    f"{(filtered_df.get('laureate_type','')=='Organization').sum():,}")
    c4.metric("Female Laureates", f"{(filtered_df['sex']=='Female').sum():,}")
    c5.metric("Countries",        f"{filtered_df['birth_country'].nunique():,}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — GEOGRAPHY  (Web.py)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    country_counts = (filtered_df[filtered_df["birth_country"].notna() &
                                  (filtered_df["birth_country"] != "Unknown")]
                      ["birth_country"].value_counts().reset_index())
    country_counts.columns = ["country","count"]
    country_counts["hover"] = country_counts.apply(
        lambda r: f"Country: {r['country']}<br>{'Award' if r['count']==1 else 'Awards'}: {int(r['count'])}",
        axis=1)
    col_l, col_r = st.columns([3,2])

    with col_l:
        fig_map = px.choropleth(country_counts, locations="country", locationmode="country names",
                                color="count", color_continuous_scale="Plasma",
                                projection="natural earth", labels={"count":"Awards"},
                                custom_data=["hover"])
        fig_map.update_traces(hovertemplate="%{customdata[0]}<extra></extra>")
        fig_map.update_layout(
            paper_bgcolor=LIGHT_BG,
            geo=dict(bgcolor="#ede9fe", showframe=False, showcoastlines=True, coastlinecolor="#c4b5fd",
                     landcolor="#f5f3ff", oceancolor="#ddd6fe", showocean=True, showlakes=True, lakecolor="#c4b5fd"),
            title=dict(text="🗺 Laureates' Birth Countries", font=dict(color=TEXT_COL, size=14, family="Inter")),
            coloraxis_colorbar=dict(title=dict(text="Awards", font=dict(color=TEXT_COL, family="Inter")),
                                    tickfont=dict(color=TEXT_COL, family="Inter")),
            font=dict(color=TEXT_COL, family="Inter"), margin=dict(t=50,b=0,l=0,r=0))
        st.plotly_chart(fig_map, use_container_width=True)

    with col_r:
        top_countries = country_counts.head(top_n).sort_values("count")
        n = len(top_countries)
        bar_colors = pc.sample_colorscale("Plasma", [i/max(n-1,1) for i in range(n)])
        fig_ctry = go.Figure(go.Bar(
            x=top_countries["count"], y=top_countries["country"], orientation="h",
            text=top_countries["count"], textposition="outside",
            textfont=dict(color=TEXT_COL, size=11, family="Inter"),
            customdata=top_countries["hover"],
            hovertemplate="%{customdata}<extra></extra>",
            marker=dict(color=bar_colors, line=BAR_BORDER)))
        base_layout(fig_ctry, f"🏅 Top {top_n} Countries")
        fig_ctry.update_layout(xaxis_title="Number of Awards", yaxis_title="",
                               xaxis=dict(gridcolor=GRID_COL, range=[0, top_countries["count"].max()*1.22]))
        fig_ctry.update_xaxes(title_font_color="#111827", tickfont_color="#111827")
        fig_ctry.update_yaxes(title_font_color="#111827", tickfont_color="#111827")
        st.plotly_chart(fig_ctry, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — DEMOGRAPHICS  (Web.py)
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    col_l, col_r = st.columns(2)

    with col_l:
        # Donut: % share of Nobel prizes by category (replaces the old gender chart)
        prize_data = filtered_df["category"].value_counts().reset_index()
        prize_data.columns = ["category", "count"]
        n_slices = len(prize_data)
        donut_colors = CAT_PALETTE[:n_slices] if n_slices <= len(CAT_PALETTE) \
                       else pc.sample_colorscale("Turbo", [i/max(n_slices-1,1) for i in range(n_slices)])
        fig_prize = go.Figure(go.Pie(
            labels=prize_data["category"], values=prize_data["count"], hole=0.52,
            marker=dict(colors=donut_colors, line=dict(color="#ffffff", width=2)),
            textinfo="label+percent", textposition="inside", insidetextorientation="auto",
            textfont=dict(color="#ffffff", family="Inter", size=12),
            hovertemplate="Category: %{label}<br>Awards: %{value}<br>Share: %{percent}<extra></extra>"))
        fig_prize.add_annotation(
            text=f"<b>{int(prize_data['count'].sum()):,}</b><br><span style='font-size:11px'>prizes</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=TEXT_COL, size=20, family="Inter"))
        fig_prize.update_layout(
            paper_bgcolor=LIGHT_BG, font=dict(color=TEXT_COL, family="Inter"),
            title=dict(text="🏆 Nobel Prize Share by Category (%)", font=dict(color=TEXT_COL, size=14, family="Inter")),
            showlegend=True,
            legend=dict(font=dict(color=TEXT_COL, family="Inter"), orientation="v",
                        x=1.05, y=0.5, xanchor="left", yanchor="middle"),
            margin=dict(t=50, b=20, l=20, r=100))
        st.plotly_chart(fig_prize, use_container_width=True)

        sex_cat = (filtered_df[filtered_df["sex"].isin(["Male","Female"])]
                   .groupby(["category","sex"]).size().reset_index(name="count"))
        fig_sc = go.Figure()
        for gender, color in [("Male", BLUE_MAIN), ("Female", PINK)]:
            sub = sex_cat[sex_cat["sex"] == gender]
            fig_sc.add_trace(go.Bar(
                name=gender, x=sub["category"], y=sub["count"],
                text=sub["count"], textposition="outside",
                textfont=dict(color=TEXT_COL, size=10, family="Inter"),
                marker=dict(color=color, line=BAR_BORDER)))
        base_layout(fig_sc, "⚧ Gender by Category")
        fig_sc.update_layout(barmode="group",
                             xaxis=dict(tickangle=-30, title="Category", gridcolor=GRID_COL),
                             yaxis=dict(gridcolor=GRID_COL, title="Number of Laureates"))
        fig_sc.update_xaxes(title_font_color="#111827", tickfont_color="#111827")
        fig_sc.update_yaxes(title_font_color="#111827", tickfont_color="#111827")
        st.plotly_chart(fig_sc, use_container_width=True)

    with col_r:
        age_col = "age_at_award" if "age_at_award" in filtered_df.columns else ("age" if "age" in filtered_df.columns else None)
        if age_col:
            age_df = filtered_df.dropna(subset=[age_col])
            if not age_df.empty:
                fig_age = go.Figure(go.Histogram(
                    x=age_df[age_col], nbinsx=25,
                    marker=dict(color=BLUE_MAIN, line=dict(color="#ffffff", width=1)),
                    name="Age at Award"))
                base_layout(fig_age, "🎂 Age Distribution at Time of Award")
                fig_age.update_layout(xaxis_title="Age at Award", yaxis_title="Number of Laureates",
                                      bargap=0.05, showlegend=False,
                                      xaxis=dict(gridcolor=GRID_COL), yaxis=dict(gridcolor=GRID_COL))
                fig_age.update_xaxes(title_font_color="#111827", tickfont_color="#111827")
                fig_age.update_yaxes(title_font_color="#111827", tickfont_color="#111827")
                st.plotly_chart(fig_age, use_container_width=True)

        if "age_group" in filtered_df.columns:
            age_grp_order = ["Youth","Adult","Senior"]
            age_grp = (filtered_df["age_group"].value_counts().reindex(age_grp_order).dropna().reset_index())
            age_grp.columns = ["age_group","count"]
            grp_colors = {"Youth": BLUE_MAIN, "Adult": AMBER, "Senior": PINK}
            fig_ag = go.Figure(go.Bar(
                x=age_grp["age_group"], y=age_grp["count"],
                text=age_grp["count"], textposition="outside",
                textfont=dict(color=TEXT_COL, size=13, family="Inter"),
                marker=dict(color=[grp_colors[g] for g in age_grp["age_group"]], line=BAR_BORDER)))
            base_layout(fig_ag, "📊 Age Groups at Time of Award")
            fig_ag.update_layout(xaxis_title="Age Group", yaxis_title="Number of Laureates",
                                 yaxis=dict(gridcolor=GRID_COL, range=[0, age_grp["count"].max()*1.15]),
                                 xaxis=dict(gridcolor=GRID_COL), showlegend=False)
            fig_ag.update_xaxes(title_font_color="#111827", tickfont_color="#111827")
            fig_ag.update_yaxes(title_font_color="#111827", tickfont_color="#111827")
            st.plotly_chart(fig_ag, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SHOW MORE — Advanced & Raw Data are hidden by default behind this toggle
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
if "show_extra_sections" not in st.session_state:
    st.session_state.show_extra_sections = False

extra_label = "🔼 Hide extra sections" if st.session_state.show_extra_sections \
              else "🔽 Show more (Advanced & Raw Data)"
if st.button(extra_label, key="toggle_extra_sections"):
    st.session_state.show_extra_sections = not st.session_state.show_extra_sections
    st.rerun()

if st.session_state.show_extra_sections:
    tab4, tab5 = st.tabs(["🧪 Advanced", "🔎 Raw Data"])


    # ══════════════════════════════════════════════════════════════════════════════
    # TAB 4 — ADVANCED  (all 6 charts from Gan_Final.py, using filtered_df)
    # ══════════════════════════════════════════════════════════════════════════════
    with tab4:
        CATEGORIES = ["Chemistry", "Economics", "Literature", "Medicine", "Peace", "Physics"]
        adv = filtered_df.copy()

        chart_choice = st.radio(
            "Select Chart",
            ["Nobel Prizes by Category and Gender",
             "Jewish Nobel Prize Winners by Category",
             "Top Countries by Number of Nobel Laureates",
             "Nobel Peace Prize: Individuals vs Organizations",
             "Individual Laureates: Category & Age Analysis",
             "Global Distribution Map (detailed)"],
            horizontal=False,
        )

        # ── CHART 1 — HEATMAP ────────────────────────────────────────────────────
        if chart_choice == "Nobel Prizes by Category and Gender":
            st.subheader("Nobel Prizes by Category and Gender")
            c1c, c2c, c3c = st.columns(3)
            avail_cats = [c for c in CATEGORIES if c in adv["category"].unique()]
            sel_cats = c1c.multiselect("Prize categories", avail_cats, default=avail_cats)
            avail_sex = adv["sex"].dropna().unique().tolist()
            sel_sex   = c2c.multiselect("Gender", avail_sex, default=avail_sex)
            show_pct  = c3c.checkbox("Show as % of row total", value=False)

            if not sel_sex or not sel_cats:
                st.warning("Select at least one gender and one category.")
            else:
                filt = adv[adv["sex"].isin(sel_sex) & adv["category"].isin(sel_cats)]
                heat = filt.pivot_table(index="sex", columns="category", aggfunc="size", fill_value=0)
                cols_present = [c for c in sel_cats if c in heat.columns]
                heat = heat[cols_present]
                if show_pct:
                    heat = heat.div(heat.sum(axis=1), axis=0) * 100
                    fmt, label = ".1f", "% of gender total"
                else:
                    fmt, label = "d", "Count"
                fig, ax = plt.subplots(figsize=(10, max(2, len(sel_sex) * 1.2 + 1)))
                sns.heatmap(heat, annot=True, fmt=fmt, cmap="Blues", ax=ax,
                            linewidths=0, linecolor="none", cbar_kws={"label": label}, alpha=0.88)
                ax.set_title("Nobel Prizes by Category and Gender", fontsize=14, pad=12)
                ax.set_xlabel("Category"); ax.set_ylabel("Gender")
                plt.tight_layout()
                st.pyplot(fig, transparent=True)
                with st.expander("View raw data"):
                    st.dataframe(heat)

        # ── CHART 2 — DONUT ──────────────────────────────────────────────────────
        elif chart_choice == "Jewish Nobel Prize Winners by Category":
            st.subheader("Winners by Category")
            cat_counts = adv["category"].value_counts().reset_index()
            cat_counts.columns = ["category", "winners"]
            all_cats = cat_counts["category"].tolist()
            sel_cats = st.multiselect("Include categories", all_cats, default=all_cats)
            active = cat_counts[cat_counts["category"].isin(sel_cats)].copy()

            if active.empty:
                st.warning("Select at least one category.")
            else:
                HOLE = 0.45
                col_chart, col_table = st.columns([1, 1])
                with col_chart:
                    fig, ax = plt.subplots(figsize=(3, 3))
                    fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
                    wedges, texts, autotexts = ax.pie(
                        active["winners"], labels=active["category"], autopct="%1.0f%%",
                        startangle=90, wedgeprops=dict(width=1 - HOLE, alpha=0.84, linewidth=0.8, edgecolor="white"),
                        pctdistance=0.78, textprops={"fontsize": 7})
                    for t in autotexts:
                        t.set_fontsize(7)
                    total = int(active["winners"].sum())
                    ax.text(0, 0, f"{total}\ntotal", ha="center", va="center",
                            fontsize=8, fontweight="bold", alpha=0.75)
                    ax.set_title("Winners by Category", fontsize=9, pad=8)
                    plt.tight_layout()
                    st.pyplot(fig, transparent=True)
                with col_table:
                    st.caption(f"**{len(active)} categories · {int(active['winners'].sum())} total**")
                    st.dataframe(active.sort_values("winners", ascending=False).reset_index(drop=True),
                                 use_container_width=True, height=200)

        # ── CHART 3 — COUNTRY LOLLIPOP ───────────────────────────────────────────
        elif chart_choice == "Top Countries by Number of Nobel Laureates":
            st.subheader("Top Countries by Number of Nobel Laureates")
            c1c, c2c = st.columns([1, 2])
            n_ctry = c1c.slider("Number of countries", 5, 30, 10)
            avail_cats = [c for c in CATEGORIES if c in adv["category"].unique()]
            cat_filter = c2c.multiselect("Filter by prize category", avail_cats, default=avail_cats)

            df_c = adv.copy()
            if cat_filter:
                df_c = df_c[df_c["category"].isin(cat_filter)]
            df_c["clean_country"] = df_c["birth_country"].str.extract(r"\((.*?)\)")
            df_c["clean_country"] = df_c["clean_country"].fillna(df_c["birth_country"])
            df_c["clean_country"] = df_c["clean_country"].replace({
                "United States of America": "USA", "United Kingdom": "UK",
                "Union of Soviet Socialist Republics": "Russia",
                "West Germany": "Germany", "East Germany": "Germany"})

            if df_c.empty:
                st.warning("No data for the selected filters.")
            else:
                cc = df_c["clean_country"].value_counts().head(n_ctry)
                cc_plot = cc.iloc[::-1]
                chart_h = min(6.0, max(3.5, n_ctry * 0.38))
                fig, ax = plt.subplots(figsize=(9, chart_h))
                fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
                DOT = "#2563EB"
                ax.hlines(y=cc_plot.index, xmin=0, xmax=cc_plot.values, color=DOT, alpha=0.45, linewidth=1.8, zorder=1)
                ax.scatter(x=cc_plot.values, y=cc_plot.index, s=100, color=DOT, alpha=0.88,
                           zorder=2, edgecolors="white", linewidths=0.8)
                for country, val in zip(cc_plot.index, cc_plot.values):
                    ax.text(val + max(cc_plot.values) * 0.012, country, str(val), va="center", fontsize=8.5, alpha=0.8)
                cat_label = ", ".join(cat_filter) if len(cat_filter) < 6 else "All categories"
                ax.set_xlim(left=0)
                ax.axvline(0, color="grey", linewidth=0.5, alpha=0.3)
                ax.spines["left"].set_alpha(0.25); ax.spines["bottom"].set_alpha(0.25)
                ax.set_xlabel("Number of Laureates", labelpad=8)
                ax.set_title(f"Top {n_ctry} Countries — {cat_label}", fontsize=14, pad=14)
                ax.set_ylabel("")
                plt.tight_layout()
                st.pyplot(fig, transparent=True)
                with st.expander("View data table"):
                    st.dataframe(cc.reset_index().rename(columns={"clean_country": "Country", "count": "Laureates"}),
                                 use_container_width=True)

        # ── CHART 4 — PEACE PRIZE ────────────────────────────────────────────────
        elif chart_choice == "Nobel Peace Prize: Individuals vs Organizations":
            st.subheader("Nobel Peace Prize: Individuals vs. Organizations")
            st.caption("Number of Laureates per Decade")
            df_peace = adv[(adv["category"] == "Peace") & (adv["year"].notna())].copy()

            if df_peace.empty:
                st.warning("No Peace Prize data in the selected year range.")
            else:
                if "laureate_type" in df_peace.columns:
                    norm = df_peace["laureate_type"].astype(str).str.strip().str.lower()
                    df_peace["Type"] = np.where(norm.str.startswith("org"), "Organization", "Individual")
                elif "type" in df_peace.columns:
                    norm = df_peace["type"].astype(str).str.strip().str.lower()
                    df_peace["Type"] = np.where(norm.str.startswith("org"), "Organization", "Individual")
                else:
                    sex_norm = df_peace["sex"].astype(str).str.strip().str.lower()
                    is_org = df_peace["sex"].isna() | sex_norm.isin(["", "nan", "none", "na"])
                    df_peace["Type"] = np.where(is_org, "Organization", "Individual")
                df_peace["Decade"] = (np.floor(df_peace["year"] / 10) * 10).astype(int).astype(str) + "s"
                df_bar = df_peace.groupby(["Decade", "Type"]).size().reset_index(name="Count")

                tt = df_peace["Type"].value_counts()
                st.caption(f"Detected: **{int(tt.get('Individual',0))}** individuals · **{int(tt.get('Organization',0))}** organizations")

                palette = {"Individual": "#0077B6", "Organization": "#E11D48"}
                fig, ax = plt.subplots(figsize=(12, 6))
                fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
                sns.barplot(data=df_bar, x="Decade", y="Count", hue="Type",
                            hue_order=["Individual", "Organization"], palette=palette,
                            edgecolor="white", linewidth=0.8, ax=ax)
                for container in ax.containers:
                    ax.bar_label(container, padding=3, weight="bold", size=9)
                ax.set_xlabel("Decade", fontsize=13, fontweight="bold", labelpad=10)
                ax.set_ylabel("Number of Laureates", fontsize=13, fontweight="bold", labelpad=10)
                ax.set_ylim(0, df_bar["Count"].max() * 1.12)
                ax.tick_params(axis="x", labelrotation=45)
                for lbl in ax.get_xticklabels():
                    lbl.set_ha("right")
                ax.set_axisbelow(True)
                ax.grid(axis="y", color="grey", linestyle="--", alpha=0.4)
                ax.grid(axis="x", visible=False)
                for spine in ax.spines.values():
                    spine.set_visible(False)
                ax.legend(title="", loc="upper center", bbox_to_anchor=(0.5, -0.18),
                          ncol=2, frameon=False, prop={"size": 12, "weight": "bold"})
                plt.tight_layout()
                st.pyplot(fig, transparent=True)
                with st.expander("View data table"):
                    st.dataframe(df_bar.pivot(index="Decade", columns="Type", values="Count").fillna(0).astype(int),
                                 use_container_width=True)

        # ── CHART 5 — AGE ANALYSIS ───────────────────────────────────────────────
        elif chart_choice == "Individual Laureates: Category & Age Analysis":
            st.subheader("Individual Laureates: Category & Age Analysis")
            ind = adv[adv["laureate_type"] == "Individual"].copy() if "laureate_type" in adv.columns else adv.copy()
            ind["age"] = pd.to_numeric(ind.get("age", ind.get("age_at_award")), errors="coerce")
            ind["decade_num"] = pd.to_numeric(ind.get("decade"), errors="coerce")
            if "decade_num" not in ind or ind["decade_num"].isna().all():
                ind["decade_num"] = (ind["year"] // 10 * 10)

            if ind.empty:
                st.warning("No individual-laureate data in the selected year range.")
            else:
                cats   = ["Chemistry", "Literature", "Medicine", "Peace", "Physics", "Economics"]
                colors = ["#FF4FA7", "#FF4F4F", "#FFA74F", "#4FFFA7", "#1DB21D", "#BA7517"]
                sub = st.radio("View",
                               ["Prizes by category", "Age distribution by category", "Average age over time"],
                               horizontal=True)

                if sub == "Prizes by category":
                    counts = [len(ind[ind["category"] == c]) for c in cats]
                    triples = sorted(zip(counts, cats, colors), reverse=True)
                    counts_s, cats_s, colors_s = zip(*triples)
                    fig, ax = plt.subplots(figsize=(10, 5.5))
                    fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
                    bars = ax.bar(cats_s, counts_s, color=colors_s, edgecolor="none", width=0.6)
                    for bar, count in zip(bars, counts_s):
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts_s)*0.01,
                                str(count), ha="center", va="bottom", fontsize=11)
                    ax.set_title("Distribution of Nobel Prizes by Category", fontsize=14, fontweight="bold", pad=12)
                    ax.set_ylabel("Number of laureates")
                    ax.set_ylim(0, max(counts_s) * 1.15)
                    ax.spines[["top", "right"]].set_visible(False)
                    ax.tick_params(axis="x", labelsize=11)
                    plt.tight_layout()
                    st.pyplot(fig, transparent=True)

                elif sub == "Age distribution by category":
                    data = [ind[ind["category"] == c]["age"].dropna().values for c in cats]
                    if all(len(d) == 0 for d in data):
                        st.warning("No age data available (check the `age` column).")
                    else:
                        fig, ax = plt.subplots(figsize=(10, 5.5))
                        fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
                        bp = ax.boxplot(data, patch_artist=True, widths=0.5,
                                        medianprops=dict(linewidth=2.5),
                                        whiskerprops=dict(linewidth=1.5, color="#aaa"),
                                        capprops=dict(linewidth=1.5, color="#aaa"),
                                        flierprops=dict(marker="o", markersize=4, alpha=0.4))
                        for patch, color, med in zip(bp["boxes"], colors, bp["medians"]):
                            patch.set_facecolor(color + "44"); patch.set_edgecolor(color); patch.set_linewidth(1.5)
                            med.set_color(color)
                        for i, median_line in enumerate(bp["medians"]):
                            mv = median_line.get_ydata()[0]
                            ax.text(i + 1, mv + 1.2, f"{int(mv)}", ha="center", va="bottom", fontsize=9)
                        ax.set_xticklabels(cats, fontsize=11)
                        ax.set_title("Age Distribution by Nobel Prize Category", fontsize=14, fontweight="bold", pad=12)
                        ax.set_ylabel("Age at award")
                        ax.spines[["top", "right"]].set_visible(False)
                        plt.tight_layout()
                        st.pyplot(fig, transparent=True)

                else:
                    avg = ind.groupby("decade_num")["age"].mean().sort_index().dropna()
                    if avg.empty:
                        st.warning("No age/decade data available.")
                    else:
                        fig, ax = plt.subplots(figsize=(10, 5.5))
                        fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
                        ax.plot(avg.index, avg.values, color="#E0331C", linewidth=2.5,
                                marker="o", markersize=6, markerfacecolor="#E0331C")
                        ax.fill_between(avg.index, avg.values, alpha=0.12, color="#7F77DD")
                        ax.set_title("Average Age of Nobel Laureates Over Time", fontsize=14, fontweight="bold", pad=12)
                        ax.set_ylabel("Average age"); ax.set_xlabel("Decade")
                        ax.set_xticks(avg.index)
                        ax.set_xticklabels([f"{int(d)}s" for d in avg.index], fontsize=10, rotation=45)
                        ax.set_ylim(max(0, avg.min() - 5), avg.max() + 5)
                        ax.spines[["top", "right"]].set_visible(False)
                        ax.yaxis.grid(True, color="#e0e0e0", linewidth=0.8)
                        ax.set_axisbelow(True)
                        plt.tight_layout()
                        st.pyplot(fig, transparent=True)

        # ── CHART 6 — DETAILED MAP ───────────────────────────────────────────────
        elif chart_choice == "Global Distribution Map (detailed)":
            st.subheader("Global Distribution of Nobel Laureates")
            st.caption("Heatmap by birth country · hover for details")
            map_df = adv[adv["birth_country"].notna()].copy()
            if map_df.empty:
                st.warning("No data for the selected year range.")
            else:
                bc = map_df["birth_country"].astype(str)
                extracted = bc.str.extract(r"\((.*?)\)")[0]
                bc_clean = extracted.fillna(bc)
                map_df["Country"] = np.select(
                    [bc_clean.str.contains("United States|USA", case=False, na=False),
                     bc_clean.str.contains("United Kingdom|UK", case=False, na=False),
                     bc_clean.str.contains("Germany", case=False, na=False),
                     bc_clean.str.contains("Russia|Soviet", case=False, na=False)],
                    ["United States", "United Kingdom", "Germany", "Russia"],
                    default=bc_clean)
                cc = (map_df.groupby("Country", as_index=False).size().rename(columns={"size": "Laureates"}))
                cc["LogLaureates"] = np.log10(cc["Laureates"] + 1)
                custom_scale = [[0.00, "#fff8e0"], [0.20, "#fcd982"], [0.40, "#f59042"],
                                [0.65, "#d63b1f"], [0.85, "#9b1c2e"], [1.00, "#4a0f1f"]]
                total = cc["Laureates"].sum()
                cc["Rank"] = cc["Laureates"].rank(method="min", ascending=False).astype(int)
                cc["Share"] = cc["Laureates"] / total * 100
                cc["Hover"] = cc.apply(
                    lambda r: (f"<b style='font-size:16px;color:#4a0f1f'>{r['Country']}</b><br>"
                               f"<span style='color:#6b7280;font-size:11px'>Rank #{int(r['Rank'])} worldwide</span><br><br>"
                               f"<b style='font-size:20px;color:#d63b1f'>{int(r['Laureates'])}</b> "
                               f"<span style='color:#374151'>laureates</span><br>"
                               f"<span style='color:#6b7280;font-size:11px'>{r['Share']:.1f}% of total prizes</span>"), axis=1)

                fig = px.choropleth(cc, locations="Country", locationmode="country names",
                                    color="LogLaureates", custom_data=["Hover"],
                                    color_continuous_scale=custom_scale,
                                    range_color=[0, cc["LogLaureates"].max()])
                fig.update_traces(marker_line_color="#111111", marker_line_width=0.7,
                                  hovertemplate="%{customdata[0]}<extra></extra>")
                fig.add_trace(go.Choropleth(
                    locations=["Antarctica", "Greenland"], locationmode="country names", z=[0, 0],
                    colorscale=[[0, "#eef9ff"], [1, "#eef9ff"]], showscale=False,
                    marker_line_color="#9cc4dc", marker_line_width=0.8,
                    customdata=["Permanent ice sheet", "Greenland ice sheet"],
                    hovertemplate="<b>%{location}</b><br><span>%{customdata}</span><extra></extra>"))
                ocean = pd.DataFrame({"name": ["P A C I F I C   O C E A N", "A T L A N T I C   O C E A N",
                                               "I N D I A N   O C E A N", "S O U T H E R N   O C E A N"],
                                      "lon": [-145, -30, 80, 30], "lat": [5, 0, -25, -67]})
                fig.add_trace(go.Scattergeo(lon=ocean["lon"], lat=ocean["lat"], text=ocean["name"], mode="text",
                    textfont=dict(size=10, color="#1e40af", family="Georgia, serif"),
                    hoverinfo="skip", showlegend=False))
                ice = pd.DataFrame({"name": ["G R E E N L A N D", "A N T A R C T I C A"],
                                    "lon": [-42, 0], "lat": [72, -82]})
                fig.add_trace(go.Scattergeo(lon=ice["lon"], lat=ice["lat"], text=ice["name"], mode="text",
                    textfont=dict(size=9, color="#5b8aa6", family="Georgia, serif"),
                    hoverinfo="skip", showlegend=False))
                cont = pd.DataFrame({"name": ["N O R T H   A M E R I C A", "S O U T H   A M E R I C A",
                                              "A F R I C A", "A S I A", "O C E A N I A"],
                                     "lon": [-100, -60, 22, 100, 142], "lat": [50, -12, 3, 50, -28]})
                fig.add_trace(go.Scattergeo(lon=cont["lon"], lat=cont["lat"], text=cont["name"], mode="text",
                    textfont=dict(size=9, color="rgba(31,41,55,0.40)", family="Arial Black"),
                    hoverinfo="skip", showlegend=False))
                fig.update_layout(
                    geo=dict(resolution=50, showframe=False,
                             showcoastlines=True, coastlinecolor="#1e3a8a", coastlinewidth=0.5,
                             showcountries=True, countrycolor="#111111", countrywidth=0.9,
                             showland=True, landcolor="#f5f1e8",
                             showocean=True, oceancolor="#a8d0e6",
                             showlakes=True, lakecolor="#a8d0e6",
                             showrivers=True, rivercolor="#7ab5d1", riverwidth=0.4,
                             projection_type="natural earth",
                             lataxis_range=[-90, 90], lonaxis_range=[-180, 180],
                             bgcolor="rgba(0,0,0,0)"),
                    coloraxis_colorbar=dict(
                        title=dict(text="<b>Number of<br>laureates</b><br>"
                                        "<span style='font-size:9px;color:#6b7280'>(log scale)</span>",
                                   font=dict(color="#1f2937", size=11), side="top"),
                        tickvals=[np.log10(v + 1) for v in [0, 1, 5, 25, 100, 250]],
                        ticktext=["0", "1", "5", "25", "100", "250"],
                        tickfont=dict(color="#1f2937", size=10),
                        orientation="v", x=1.01, xanchor="left", y=0.5, yanchor="middle",
                        len=0.85, thickness=18, outlinecolor="rgba(0,0,0,0.25)", outlinewidth=1,
                        bgcolor="rgba(255,255,255,0.6)"),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    hoverlabel=dict(bgcolor="#fffdf8", bordercolor="#d63b1f",
                        font=dict(family="Inter, system-ui, sans-serif", size=13, color="#1f2937")),
                    font=dict(family="Inter, system-ui, sans-serif"),
                    margin=dict(l=10, r=90, t=20, b=20), height=720)
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"n = {int(total)} laureates · {len(cc)} countries")

    # ══════════════════════════════════════════════════════════════════════════════
    # TAB 5 — RAW DATA  (Web.py)
    # ══════════════════════════════════════════════════════════════════════════════
    with tab5:
        st.markdown("#### 🔎 Search Laureates")
        search = st.text_input("Search by name or country:", placeholder="e.g. Marie Curie, France...")
        display_df = filtered_df.copy()
        if search:
            m = display_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
            display_df = display_df[m]
        st.caption(f"Showing {len(display_df):,} records")

        # ── Show BASIC info only; details are hidden behind a "Show more" button ──
        BASIC_COLS = ["year", "category", "full_name", "sex", "birth_country"]
        EXTRA_COLS = ["laureate_type", "prize", "prize_share", "birth_date", "birth_city",
                      "organization_name", "organization_city", "organization_country",
                      "death_date", "death_city", "death_country",
                      "age_at_award", "age_group", "decade", "motivation"]

        if "show_more_cols" not in st.session_state:
            st.session_state.show_more_cols = False

        btn_label = "🔼 Collapse (basic info only)" if st.session_state.show_more_cols else "🔽 Show more details"
        if st.button(btn_label, key="toggle_more_cols"):
            st.session_state.show_more_cols = not st.session_state.show_more_cols
            st.rerun()

        if st.session_state.show_more_cols:
            cols_show = BASIC_COLS + EXTRA_COLS
            st.caption("Showing **all** columns. Click the button above to collapse.")
        else:
            cols_show = BASIC_COLS
            st.caption("Showing **basic** info only. Click **Show more details** to reveal all columns.")

        cols_show = [c for c in cols_show if c in display_df.columns]
        st.dataframe(display_df[cols_show].sort_values("year", ascending=False),
                     use_container_width=True, height=500)

        # Per-laureate details (hidden inside an expander)
        with st.expander("👤 Show more: laureate details"):
            if display_df.empty:
                st.info("No matching data.")
            else:
                name_col = "full_name" if "full_name" in display_df.columns else display_df.columns[0]
                options = (display_df.sort_values("year", ascending=False)
                           .apply(lambda r: f"{r[name_col]} — {r['category']} ({int(r['year'])})", axis=1).tolist())
                picked = st.selectbox("Select a laureate:", options)
                if picked:
                    idx = options.index(picked)
                    row = display_df.sort_values("year", ascending=False).iloc[idx]
                    all_cols = [c for c in BASIC_COLS + EXTRA_COLS if c in display_df.columns]
                    detail = row[all_cols].rename("Value").to_frame()
                    detail.index.name = "Field"
                    st.table(detail.astype(str))

        csv = display_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download as CSV", csv, "nobel_laureates_filtered.csv", "text/csv")

st.markdown("---")
st.markdown(
    f"<p style='color:#6b7280;text-align:center;font-size:0.8rem;font-family:Inter,sans-serif'>"
    f"Data source: {src_name} · Last loaded: {datetime.now().strftime('%B %d, %Y')}</p>",
    unsafe_allow_html=True)
