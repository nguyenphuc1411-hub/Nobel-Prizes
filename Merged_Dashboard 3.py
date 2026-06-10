"""
Nobel Laureates Dashboard — MERGED
Gộp Web.py (Plotly, giao diện tabs) + Gần_Final.py (matplotlib/seaborn charts nâng cao)

Run: streamlit run Merged_Dashboard.py
Cần file dữ liệu SDnobel.csv / SDnobel.xls / SDnobel.xlsx đặt cạnh script.
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

# ── CSS (từ Web.py) ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], * { font-family: 'Inter', sans-serif !important; }
    /* Đừng ép font lên icon — giữ nguyên Material Symbols, nếu không mũi tên expander hiện ra dạng chữ "keyboard_arrow_right" */
    [class*="material-icons"], [class*="material-symbols"],
    [data-testid="stExpanderToggleIcon"], .stExpander [data-testid="stIconMaterial"],
    span[data-testid="stIconMaterial"], .material-symbols-outlined, .material-symbols-rounded {
        font-family: 'Material Symbols Rounded','Material Symbols Outlined','Material Icons' !important;
    }
    .stApp { background: #f4f6fb; color: #111827; }
    [data-testid="stSidebar"] { background:#ffffff; border-right:1px solid #e2e8f0; }
    [data-testid="stSidebar"] * { color:#111827 !important; }
    [data-testid="metric-container"] {
        background:#ffffff; border:1px solid #e2e8f0; border-radius:12px;
        padding:16px 20px; box-shadow:0 2px 8px rgba(37,99,235,0.07);
    }
    [data-testid="stMetricValue"]  { color:#2563eb !important; font-size:2rem !important; font-weight:700 !important; }
    [data-testid="stMetricLabel"]  { color:#111827 !important; font-size:0.85rem !important; font-weight:600 !important; }
    .main-header {
        background:linear-gradient(135deg,#1e3a8a,#2563eb);
        border-radius:14px; padding:24px 32px; margin-bottom:24px;
    }
    .main-header h1 { color:#fff; margin:0; font-size:2rem; font-weight:700; }
    .main-header p  { color:#bfdbfe; margin:6px 0 0; font-size:0.95rem; }
    hr { border-color:#e2e8f0 !important; }
    .stTabs [data-baseweb="tab-list"] { background:#ffffff; border-radius:10px; padding:4px; }
    .stTabs [data-baseweb="tab"]      { color:#374151; border-radius:8px; font-weight:500; }
    .stTabs [aria-selected="true"]    { background:#2563eb !important; color:#ffffff !important; }
    .stPlotlyChart {
        background:#ffffff; border-radius:12px; padding:8px;
        border:1px solid #e2e8f0; box-shadow:0 2px 8px rgba(0,0,0,0.04);
    }
    .section-label {
        color:#111827; font-size:0.75rem; text-transform:uppercase;
        letter-spacing:0.1em; margin:12px 0 4px; font-weight:700;
    }

    /* ── Ép màu chữ đậm cho mọi widget trong vùng main (fix chữ chìm) ── */
    .stApp .main p, .stApp .main span:not([data-testid="stIconMaterial"]), .stApp .main label,
    .stApp .main li, .stApp .main div[data-baseweb] { color:#111827 !important; }

    /* Nhãn widget (Select Chart, Include categories, ...) */
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p,
    .stRadio > label, .stCheckbox > label,
    .stMultiSelect label, .stSelectbox label,
    .stSlider label, .stTextInput label {
        color:#111827 !important; font-weight:600 !important; opacity:1 !important;
    }

    /* Các lựa chọn radio / checkbox */
    .stRadio div[role="radiogroup"] label,
    .stRadio div[role="radiogroup"] label p,
    .stCheckbox label p {
        color:#111827 !important; opacity:1 !important;
    }

    /* Multiselect: tag đã chọn + ô chọn */
    .stMultiSelect [data-baseweb="tag"] { background:#2563eb !important; }
    .stMultiSelect [data-baseweb="tag"] span { color:#ffffff !important; }
    .stMultiSelect [data-baseweb="select"] * { color:#111827 !important; }

    /* Subheader / caption trong main */
    .stApp .main h1, .stApp .main h2, .stApp .main h3,
    .stApp .main h4, .stApp .main h5 { color:#111827 !important; }
    .stApp .main [data-testid="stCaptionContainer"],
    .stApp .main [data-testid="stCaptionContainer"] * { color:#475569 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING  (gộp: hỗ trợ csv/xls/xlsx như Gần_Final + chuẩn hoá tên cột)
# ══════════════════════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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
    candidates = ["SDnobel.xlsx", "SDnobel.xls", "SDnobel.csv",
                  "SDnobel.XLSX", "SDnobel.XLS", "SDnobel.CSV"]
    found = next((os.path.join(SCRIPT_DIR, f)
                 for f in candidates if os.path.exists(os.path.join(SCRIPT_DIR, f))), None)
    if found:
        return _normalize(_read_any(found, name=found)), os.path.basename(found)
    return None, None

st.markdown("""
<div class="main-header">
    <h1>🏆 Nobel Laureates Dashboard</h1>
    <p>Explore Nobel Prize data — 1901 to present.</p>
</div>""", unsafe_allow_html=True)

with st.spinner("Loading data..."):
    df, src_name = load_data()

if df is None:
    st.sidebar.warning("No SDnobel data file found in script folder.")
    uploaded = st.sidebar.file_uploader("Upload SDnobel (CSV or Excel)", type=["csv", "xls", "xlsx"])
    if uploaded is not None:
        df = _normalize(_read_any(uploaded, name=uploaded.name))
        src_name = uploaded.name
    else:
        st.info("Đặt `SDnobel.csv` (hoặc `.xls`/`.xlsx`) cạnh script rồi chạy lại, hoặc upload qua sidebar.")
        st.stop()

if df.empty:
    st.error("No data available."); st.stop()

st.sidebar.success(f"Loaded {src_name} — {len(df):,} rows")

# Helper: age dùng chung (Web.py dùng age_at_award, Gần_Final dùng age)
if "age_at_award" in df.columns and "age" not in df.columns:
    df["age"] = pd.to_numeric(df["age_at_award"], errors="coerce")

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — FILTER CHUNG
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
# METRICS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### 📊 Overview")
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Total Awards",     f"{len(filtered_df):,}")
c2.metric("Individuals",      f"{(filtered_df.get('laureate_type','')=='Individual').sum():,}")
c3.metric("Organizations",    f"{(filtered_df.get('laureate_type','')=='Organization').sum():,}")
c4.metric("Female Laureates", f"{(filtered_df['sex']=='Female').sum():,}")
c5.metric("Countries",        f"{filtered_df['birth_country'].nunique():,}")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# THEME (Plotly helpers từ Web.py)
# ══════════════════════════════════════════════════════════════════════════════
LIGHT_BG   = "#ffffff"
PLOT_BG    = "#f8fafc"
GRID_COL   = "#e2e8f0"
TEXT_COL   = "#111827"
BAR_BORDER = dict(color="#ffffff", width=1.5)
BLUE_MAIN  = "#2563eb"
AMBER      = "#f59e0b"
PINK       = "#ec4899"
CAT_PALETTE = ["#2563eb","#10b981","#f59e0b","#ef4444","#8b5cf6","#06b6d4"]
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
# TABS — thêm tab "Advanced" để chứa toàn bộ chart của Gần_Final
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Overview","🌍 Geography","👤 Demographics","🧪 Advanced","🔎 Raw Data"]
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
                                color="count", color_continuous_scale="Viridis",
                                projection="natural earth", labels={"count":"Awards"},
                                custom_data=["hover"])
        fig_map.update_traces(hovertemplate="%{customdata[0]}<extra></extra>")
        fig_map.update_layout(
            paper_bgcolor=LIGHT_BG,
            geo=dict(bgcolor="#dbeafe", showframe=False, showcoastlines=True, coastlinecolor="#93c5fd",
                     landcolor="#eff6ff", oceancolor="#bfdbfe", showocean=True, showlakes=True, lakecolor="#93c5fd"),
            title=dict(text="🗺 Laureates' Birth Countries", font=dict(color=TEXT_COL, size=14, family="Inter")),
            coloraxis_colorbar=dict(title=dict(text="Awards", font=dict(color=TEXT_COL, family="Inter")),
                                    tickfont=dict(color=TEXT_COL, family="Inter")),
            font=dict(color=TEXT_COL, family="Inter"), margin=dict(t=50,b=0,l=0,r=0))
        st.plotly_chart(fig_map, use_container_width=True)

    with col_r:
        top_countries = country_counts.head(top_n).sort_values("count")
        n = len(top_countries)
        bar_colors = pc.sample_colorscale("Viridis", [i/max(n-1,1) for i in range(n)])
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
        sex_data = (filtered_df[filtered_df["sex"].isin(["Male","Female"])]
                    ["sex"].value_counts().reset_index())
        sex_data.columns = ["sex","count"]
        slice_colors = [BLUE_MAIN if s=="Male" else PINK for s in sex_data["sex"]]
        fig_sex = go.Figure(go.Pie(
            labels=sex_data["sex"], values=sex_data["count"], hole=0.48,
            marker=dict(colors=slice_colors, line=dict(color="#ffffff", width=2)),
            textinfo="label+percent+value", textposition="inside", insidetextorientation="auto",
            textfont=dict(color="#ffffff", family="Inter"), pull=[0.03, 0.03]))
        fig_sex.update_layout(
            paper_bgcolor=LIGHT_BG, font=dict(color=TEXT_COL, family="Inter"),
            title=dict(text="⚧ Gender Distribution", font=dict(color=TEXT_COL, size=14, family="Inter")),
            showlegend=True,
            legend=dict(font=dict(color=TEXT_COL, family="Inter"), orientation="v",
                        x=1.05, y=0.5, xanchor="left", yanchor="middle"),
            margin=dict(t=50, b=20, l=20, r=100))
        st.plotly_chart(fig_sex, use_container_width=True)

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
# TAB 4 — ADVANCED  (toàn bộ 6 chart của Gần_Final.py, dùng filtered_df)
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
        st.caption("Heatmap theo quốc gia sinh · hover để xem chi tiết")
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
    cols_show = ["year","category","full_name","laureate_type","sex",
                 "birth_country","age_at_award","age_group","motivation"]
    cols_show = [c for c in cols_show if c in display_df.columns]
    st.dataframe(display_df[cols_show].sort_values("year", ascending=False),
                 use_container_width=True, height=500)
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download as CSV", csv, "nobel_laureates_filtered.csv", "text/csv")

st.markdown("---")
st.markdown(
    f"<p style='color:#6b7280;text-align:center;font-size:0.8rem;font-family:Inter,sans-serif'>"
    f"Data source: {src_name} · Last loaded: {datetime.now().strftime('%B %d, %Y')}</p>",
    unsafe_allow_html=True)
