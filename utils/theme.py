import streamlit as st
import pandas as pd


PAN_RED = "#FA582D"
PAN_DARK = "#07131F"
PAN_NAVY = "#0E2235"
PAN_TEXT = "#17202A"
PAN_MUTED = "#607083"
PAN_BORDER = "#D8E0EA"
PAN_BG = "#F4F7FB"


def apply_theme():
    st.markdown(
        f"""
        <style>
        :root {{
            --pan-red: {PAN_RED};
            --pan-dark: {PAN_DARK};
            --pan-navy: {PAN_NAVY};
            --pan-text: #17202A;
            --pan-muted: #607083;
            --pan-border: #D8E0EA;
            --pan-bg: #F4F7FB;
            --pan-surface: #FFFFFF;
            --pan-sidebar: #FFFFFF;
            --pan-sidebar-text: #17202A;
            --pan-shadow: rgba(14,34,53,0.06);
            --pan-soft-blue: #EAF3FF;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --pan-text: #EAF0F7;
                --pan-muted: #AAB7C6;
                --pan-border: #26384A;
                --pan-bg: #07131F;
                --pan-surface: #0E2235;
                --pan-sidebar: #07131F;
                --pan-sidebar-text: #EAF0F7;
                --pan-shadow: rgba(0,0,0,0.25);
                --pan-soft-blue: #102A44;
            }}
        }}

        .stApp {{
            background: var(--pan-bg);
            color: var(--pan-text);
        }}

        [data-testid="stSidebar"] {{
            background: var(--pan-sidebar);
            border-right: 1px solid var(--pan-border);
        }}

        [data-testid="stSidebar"] * {{
            color: var(--pan-sidebar-text) !important;
        }}

        [data-testid="stSidebar"] hr {{
            border-color: var(--pan-border);
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label {{
            color: var(--pan-muted) !important;
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1420px;
        }}

        h1, h2, h3 {{
            color: var(--pan-text);
            letter-spacing: 0;
        }}

        h1 {{
            font-size: 2.05rem !important;
            font-weight: 760 !important;
        }}

        h2, h3 {{
            font-weight: 720 !important;
        }}

        div[data-testid="stMetric"] {{
            background: var(--pan-surface);
            border: 1px solid var(--pan-border);
            border-left: 4px solid var(--pan-red);
            border-radius: 8px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 24px var(--pan-shadow);
        }}

        div[data-testid="stMetricLabel"] p {{
            color: var(--pan-muted);
            font-size: 0.83rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }}

        div[data-testid="stMetricValue"] {{
            color: var(--pan-text);
            font-weight: 760;
        }}

        div[data-testid="stPlotlyChart"] {{
            background: var(--pan-surface);
            border: 1px solid var(--pan-border);
            border-radius: 8px;
            padding: 0.75rem;
            box-shadow: 0 10px 24px var(--pan-shadow);
        }}

        .pan-hero {{
            background: linear-gradient(135deg, #07131F 0%, #0E2235 58%, #173650 100%);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 8px;
            color: #FFFFFF;
            padding: 2rem 2.1rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 18px 42px rgba(7,19,31,0.18);
        }}

        .pan-hero h1 {{
            color: #FFFFFF;
            margin: 0.2rem 0 0.65rem 0;
            font-size: 2.45rem !important;
        }}

        .pan-hero p {{
            color: #C7D2DE;
            max-width: 900px;
            line-height: 1.6;
            margin: 0;
        }}

        .pan-eyebrow {{
            color: #FFB29B;
            font-weight: 760;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-size: 0.78rem;
        }}

        .pan-page-head {{
            background: var(--pan-surface);
            border: 1px solid var(--pan-border);
            border-radius: 8px;
            padding: 1.25rem 1.35rem;
            margin-bottom: 1rem;
            box-shadow: 0 10px 24px var(--pan-shadow);
        }}

        .pan-page-head h1 {{
            margin: 0.15rem 0 0.35rem 0;
        }}

        .pan-page-head p {{
            margin: 0;
            color: var(--pan-muted);
            line-height: 1.55;
        }}

        .pan-chip-row {{
            display: flex;
            gap: 0.55rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }}

        .pan-chip {{
            border: 1px solid rgba(250,88,45,0.24);
            background: rgba(250,88,45,0.08);
            color: var(--pan-text);
            border-radius: 999px;
            padding: 0.34rem 0.68rem;
            font-size: 0.78rem;
            font-weight: 700;
        }}

        .pan-panel {{
            background: var(--pan-surface);
            border: 1px solid var(--pan-border);
            border-radius: 8px;
            padding: 1.15rem 1.25rem;
            box-shadow: 0 10px 24px var(--pan-shadow);
            height: 100%;
        }}

        .pan-panel h3 {{
            margin-top: 0;
            font-size: 1.02rem !important;
        }}

        .pan-panel p, .pan-panel li {{
            color: var(--pan-muted);
            line-height: 1.55;
        }}

        .pan-module {{
            background: var(--pan-surface);
            border: 1px solid var(--pan-border);
            border-top: 3px solid var(--pan-red);
            border-radius: 8px;
            padding: 1rem;
            min-height: 132px;
            box-shadow: 0 10px 24px var(--pan-shadow);
        }}

        .pan-module strong {{
            color: var(--pan-text);
            display: block;
            margin-bottom: 0.35rem;
        }}

        .pan-module span {{
            color: var(--pan-muted);
            font-size: 0.9rem;
            line-height: 1.45;
        }}

        .pan-sidebar-brand {{
            border: 1px solid var(--pan-border);
            border-radius: 8px;
            padding: 0.95rem;
            background: var(--pan-surface);
            margin-bottom: 0.8rem;
        }}

        .pan-sidebar-brand strong {{
            color: var(--pan-sidebar-text);
        }}

        .pan-sidebar-brand span {{
            color: var(--pan-muted);
            font-size: 0.86rem;
        }}

        .pan-sidebar-kicker {{
            color: var(--pan-red) !important;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .pan-sidebar-title {{
            color: var(--pan-sidebar-text) !important;
            font-size: 1rem;
            font-weight: 760;
            line-height: 1.25;
            margin-top: 0.2rem;
        }}

        .pan-insight {{
            background: var(--pan-soft-blue);
            border: 1px solid #B8D7F5;
            border-left: 4px solid #335C81;
            border-radius: 8px;
            padding: 1rem 1.1rem;
            margin: 0.5rem 0 1rem 0;
            color: var(--pan-text);
        }}

        .pan-risk-badge {{
            border-radius: 999px;
            color: #FFFFFF;
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 760;
            padding: 0.2rem 0.55rem;
            text-align: center;
            white-space: nowrap;
        }}

        .pan-divider {{
            border-top: 1px solid var(--pan-border);
            margin: 1.5rem 0 0.9rem 0;
            position: relative;
        }}

        .pan-divider span {{
            background: var(--pan-bg);
            color: var(--pan-muted);
            font-size: 0.78rem;
            font-weight: 760;
            letter-spacing: 0.08em;
            padding-right: 0.75rem;
            position: relative;
            text-transform: uppercase;
            top: -0.7rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    st.sidebar.markdown(
        """
        <div class="pan-sidebar-brand">
            <div class="pan-sidebar-kicker">Palo Alto Networks</div>
            <div class="pan-sidebar-title">Workforce Intelligence</div>
            <span>Attrition patterns, risk hotspots, and retention signals for HR leadership.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.page_link("app.py", label="Command Center")
    st.sidebar.page_link("pages/01_Overview.py", label="Overview")
    st.sidebar.page_link("pages/02_Department_Role.py", label="Department & Role")
    st.sidebar.page_link("pages/03_Demographics.py", label="Demographics")
    st.sidebar.page_link("pages/04_Tenure_Workload.py", label="Tenure & Workload")
    st.sidebar.page_link("pages/05_Risk_Score.py", label="Risk Score")
    st.sidebar.page_link("pages/06_Compensation.py", label="Compensation")
    st.sidebar.markdown("---")


def page_header(eyebrow: str, title: str, subtitle: str, chips: list[str] | None = None):
    chips_html = ""
    if chips:
        chips_html = '<div class="pan-chip-row">' + "".join(f'<span class="pan-chip">{chip}</span>' for chip in chips) + "</div>"
    st.markdown(
        f"""
        <div class="pan-page-head">
            <div class="pan-eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
            {chips_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, eyebrow: str = "Palo Alto Networks"):
    st.markdown(
        f"""
        <section class="pan-hero">
            <div class="pan-eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def insight_card(title: str, body: str, icon: str = "Insight"):
    st.markdown(
        f"""
        <div class="pan-insight">
            <strong>{icon} | {title}</strong><br>
            <span>{body}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(rate: float, baseline: float) -> str:
    if rate > baseline * 1.5:
        color = "#D83A22"
        label = "HIGH RISK"
    elif rate > baseline * 1.1:
        color = "#F29D38"
        label = "ELEVATED"
    else:
        color = "#1A9A74"
        label = "BELOW BASE"
    return f'<span class="pan-risk-badge" style="background:{color};">{label}</span>'


def data_quality_banner(df: pd.DataFrame):
    nulls = int(df.isna().sum().sum())
    duplicate_count = 0
    if "EmployeeNumber" in df.columns:
        duplicate_count = int(df["EmployeeNumber"].duplicated().sum())
    attrition_ok = pd.api.types.is_integer_dtype(df["Attrition"])
    if nulls == 0 and duplicate_count == 0 and attrition_ok:
        st.success(f"Data health check passed: {len(df):,} records, {len(df.columns)} fields, no missing values detected.")
    else:
        st.warning(
            f"Data health check: {nulls:,} missing values, {duplicate_count:,} duplicate employee IDs, "
            f"Attrition integer type: {attrition_ok}."
        )


def section_divider(label: str):
    st.markdown(
        f'<div class="pan-divider"><span>{label}</span></div>',
        unsafe_allow_html=True,
    )


def chart_caption(n: int):
    st.caption(f"Source: Palo Alto Networks HR Dataset | n = {n:,}")


def download_filtered_data(df: pd.DataFrame, filename: str):
    with st.expander("Download Filtered Data"):
        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=filename,
            mime="text/csv",
            use_container_width=True,
        )
