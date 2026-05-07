import streamlit as st


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
            --pan-text: {PAN_TEXT};
            --pan-muted: {PAN_MUTED};
            --pan-border: {PAN_BORDER};
            --pan-bg: {PAN_BG};
        }}

        .stApp {{
            background:
                linear-gradient(180deg, rgba(244,247,251,0.98), rgba(244,247,251,1) 380px),
                radial-gradient(circle at top left, rgba(250,88,45,0.12), transparent 32rem);
            color: var(--pan-text);
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #07131F 0%, #0E2235 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }}

        [data-testid="stSidebar"] * {{
            color: #EAF0F7 !important;
        }}

        [data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,0.16);
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label {{
            color: #C7D2DE !important;
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
            background: #FFFFFF;
            border: 1px solid var(--pan-border);
            border-left: 4px solid var(--pan-red);
            border-radius: 8px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 24px rgba(14,34,53,0.06);
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
            background: #FFFFFF;
            border: 1px solid var(--pan-border);
            border-radius: 8px;
            padding: 0.75rem;
            box-shadow: 0 10px 24px rgba(14,34,53,0.05);
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
            background: #FFFFFF;
            border: 1px solid var(--pan-border);
            border-radius: 8px;
            padding: 1.25rem 1.35rem;
            margin-bottom: 1rem;
            box-shadow: 0 10px 24px rgba(14,34,53,0.05);
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
            color: #7A2B18;
            border-radius: 999px;
            padding: 0.34rem 0.68rem;
            font-size: 0.78rem;
            font-weight: 700;
        }}

        .pan-panel {{
            background: #FFFFFF;
            border: 1px solid var(--pan-border);
            border-radius: 8px;
            padding: 1.15rem 1.25rem;
            box-shadow: 0 10px 24px rgba(14,34,53,0.05);
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
            background: #FFFFFF;
            border: 1px solid var(--pan-border);
            border-top: 3px solid var(--pan-red);
            border-radius: 8px;
            padding: 1rem;
            min-height: 132px;
            box-shadow: 0 10px 24px rgba(14,34,53,0.05);
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
            border: 1px solid rgba(255,255,255,0.16);
            border-radius: 8px;
            padding: 0.85rem;
            background: rgba(255,255,255,0.06);
        }}

        .pan-sidebar-brand strong {{
            color: #FFFFFF;
        }}

        .pan-sidebar-brand span {{
            color: #C7D2DE;
            font-size: 0.86rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Palo_Alto_Networks_2020_logo.svg/320px-Palo_Alto_Networks_2020_logo.svg.png",
        width=210,
    )
    st.sidebar.markdown(
        """
        <div class="pan-sidebar-brand">
            <strong>Workforce Intelligence</strong><br>
            <span>Attrition patterns, risk hotspots, and retention signals for HR leadership.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
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
