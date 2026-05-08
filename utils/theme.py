import pandas as pd
import streamlit as st


PAN_RED = "#C9BDAE"
PAN_DARK = "#313A55"
PAN_NAVY = "#82A9C7"
PAN_TEXT = "#1D2638"
PAN_MUTED = "#5E6B7A"
PAN_BORDER = "#C9D2D6"
PAN_BG = "#F0F1DF"


def apply_theme():
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700;800&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400,0,0&display=swap" rel="stylesheet">
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <style>
        :root {{
            --pan-red: {PAN_RED};
            --pan-accent: {PAN_RED};
            --pan-dark: {PAN_DARK};
            --pan-navy: {PAN_NAVY};
            --pan-blue: #82A9C7;
            --pan-cyan: #ACCCD8;
            --pan-ivory: #F0F1DF;
            --pan-sand: #F0E2CD;
            --pan-stone: #C9BDAE;
            --pan-text: {PAN_TEXT};
            --pan-muted: {PAN_MUTED};
            --pan-border: {PAN_BORDER};
            --pan-bg: {PAN_BG};
            --pan-surface: #FFFFFF;
            --pan-surface-soft: #F7F4EA;
            --pan-sidebar: #F0F1DF;
            --pan-hover: #E4E7DC;
            --pan-chip-bg: #F0E2CD;
            --pan-chip-border: #D8C9B7;
            --pan-chip-text: #313A55;
            --pan-insight-bg: #EEF5F7;
            --pan-alert-bg: #F0E2CD;
            --pan-green: #476F67;
            --pan-amber: #8A6F52;
            --pan-shadow: 0 18px 42px rgba(49, 58, 85, 0.14);
            --pan-soft-shadow: 0 8px 22px rgba(49, 58, 85, 0.09);
        }}

        html, body, .stApp, .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown td,
        .stMarkdown th, .stMetric, label, input, textarea, select, button {{
            font-family: "DM Sans", "Segoe UI", Arial, sans-serif;
            font-feature-settings: "cv01", "cv03", "cv04";
            letter-spacing: 0;
        }}

        [class*="material-symbols"],
        [class*="material-icons"],
        .material-symbols-rounded,
        .material-symbols-outlined,
        .material-icons {{
            font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
        }}

        .stApp {{
            background:
                radial-gradient(circle at 85% -8%, rgba(172, 204, 216, 0.45), transparent 28rem),
                radial-gradient(circle at 9% 12%, rgba(240, 226, 205, 0.42), transparent 24rem),
                linear-gradient(135deg, #F7F4EA 0%, #F0F1DF 44%, #E7ECE8 100%);
            color: var(--pan-text);
        }}

        .block-container {{
            max-width: 1440px;
            padding-top: 1.25rem;
            padding-bottom: 3rem;
        }}

        #MainMenu,
        footer,
        [data-testid="stDecoration"] {{
            display: none !important;
            visibility: hidden !important;
        }}

        header[data-testid="stHeader"] {{
            background: linear-gradient(90deg, rgba(49, 58, 85, 0.98), rgba(130, 169, 199, 0.92)) !important;
            border-bottom: 1px solid rgba(178, 193, 201, 0.35);
            box-shadow: 0 8px 24px rgba(49, 58, 85, 0.12);
        }}

        [data-testid="stToolbar"] {{
            color: #FFFFFF;
        }}

        [data-testid="stToolbar"] * {{
            color: #FFFFFF !important;
        }}

        h1, h2, h3 {{
            color: var(--pan-text);
            font-weight: 700 !important;
        }}

        h1 {{
            font-size: 1.85rem !important;
            line-height: 1.18;
        }}

        h2 {{
            font-size: 1.25rem !important;
            font-weight: 600 !important;
        }}

        h3 {{
            border-left: 4px solid var(--pan-navy);
            color: var(--pan-text);
            font-size: 1.03rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.01em;
            margin: 1.15rem 0 0.85rem 0 !important;
            padding-left: 0.65rem;
            text-transform: none;
        }}

        .pan-panel h3,
        .pan-module h3 {{
            border-left: 0;
            margin-top: 0 !important;
            padding-left: 0;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background:
                linear-gradient(180deg, rgba(172, 204, 216, 0.34), transparent 17rem),
                var(--pan-sidebar);
            border-right: 1px solid var(--pan-border);
            box-shadow: 8px 0 30px rgba(49, 58, 85, 0.08);
        }}

        [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] * {{
            font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
        }}

        [data-testid="stSidebar"] * {{
            color: var(--pan-text) !important;
        }}

        [data-testid="stSidebar"] hr {{
            border-color: var(--pan-border);
            margin: 1rem 0;
        }}

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p {{
            color: var(--pan-muted) !important;
        }}

        [data-testid="stSidebar"] [data-baseweb="select"] > div {{
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid var(--pan-border);
            border-radius: 9px;
            box-shadow: 0 4px 12px rgba(49, 58, 85, 0.06);
            min-height: 2.45rem;
        }}

        [data-testid="stSidebar"] [data-baseweb="select"] input {{
            color: var(--pan-text) !important;
        }}

        [data-testid="stSidebar"] [data-baseweb="tag"] {{
            background: linear-gradient(135deg, var(--pan-dark), #4B5877) !important;
            border-radius: 7px !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            max-width: 238px;
        }}

        [data-testid="stSidebar"] [data-baseweb="tag"] span,
        [data-testid="stSidebar"] [data-baseweb="tag"] p {{
            color: #FFFFFF !important;
        }}

        [data-testid="stSidebar"] [data-baseweb="tag"] svg {{
            fill: #FFFFFF !important;
        }}

        [data-testid="stSidebar"] [data-baseweb="select"] svg {{
            fill: var(--pan-dark) !important;
        }}

        [data-testid="stSidebar"] [data-baseweb="select"] [data-baseweb="tag"] svg {{
            fill: #FFFFFF !important;
        }}

        [data-testid="stSidebar"] [data-baseweb="slider"] div {{
            color: var(--pan-text);
        }}

        [data-testid="stSidebar"] div[data-testid="stMetric"] {{
            background: #FFFFFF;
            border-color: var(--pan-border);
        }}

        [data-testid="stSidebar"] a {{
            border-radius: 8px;
            color: var(--pan-text) !important;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 0.15rem;
        }}

        [data-testid="stSidebar"] a:hover {{
            background: var(--pan-hover);
            color: var(--pan-red) !important;
        }}

        .pan-sidebar-brand {{
            background:
                linear-gradient(135deg, rgba(49, 58, 85, 0.98), rgba(130, 169, 199, 0.88));
            border: 1px solid rgba(240, 226, 205, 0.34);
            border-radius: 10px;
            padding: 0.95rem 1rem;
            margin-bottom: 0.9rem;
            overflow: hidden;
            position: relative;
            box-shadow: var(--pan-soft-shadow);
        }}

        .pan-sidebar-brand::after {{
            animation: shimmer 5.5s ease-in-out infinite;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent);
            content: "";
            height: 100%;
            left: -65%;
            position: absolute;
            top: 0;
            transform: skewX(-18deg);
            width: 38%;
        }}

        .pan-brand-kicker {{
            color: #F0E2CD;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .pan-brand-title {{
            color: #FFFFFF;
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.25;
            margin-top: 0.2rem;
        }}

        .pan-brand-sub {{
            color: #EEF2E4;
            font-size: 0.82rem;
            line-height: 1.45;
            margin-top: 0.35rem;
        }}

        .pan-sidebar-snapshot {{
            background: var(--pan-surface-soft);
            border: 1px solid var(--pan-border);
            border-radius: 10px;
            padding: 0.8rem 0.9rem;
        }}

        .pan-sidebar-snapshot-title {{
            color: var(--pan-muted);
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }}

        .pan-snapshot-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--pan-border);
            padding: 0.32rem 0;
            gap: 0.75rem;
        }}

        .pan-snapshot-row:last-child {{
            border-bottom: 0;
        }}

        .pan-snapshot-label {{
            color: var(--pan-muted);
            font-size: 0.8rem;
        }}

        .pan-snapshot-value {{
            color: var(--pan-text);
            font-size: 0.82rem;
            font-weight: 700;
            text-align: right;
        }}

        .pan-snapshot-value.alert {{
            color: var(--pan-red);
        }}

        .pan-snapshot-value.good {{
            color: var(--pan-green);
        }}

        /* Cards and Streamlit primitives */
        div[data-testid="stMetric"] {{
            background: var(--pan-surface);
            border: 1px solid var(--pan-border);
            border-radius: 10px;
            padding: 0.95rem 1.05rem;
            box-shadow: var(--pan-soft-shadow);
        }}

        div[data-testid="stMetric"]::before {{
            content: "";
            display: block;
            height: 3px;
            width: 38px;
            background: linear-gradient(90deg, var(--pan-dark), var(--pan-accent));
            border-radius: 999px;
            margin-bottom: 0.65rem;
        }}

        .pan-topbar {{
            align-items: center;
            background:
                linear-gradient(135deg, rgba(49, 58, 85, 0.98), rgba(130, 169, 199, 0.92));
            border: 1px solid rgba(178, 193, 201, 0.34);
            border-radius: 12px;
            box-shadow: var(--pan-shadow);
            display: flex;
            gap: 1rem;
            justify-content: space-between;
            margin-bottom: 1rem;
            padding: 0.72rem 1rem;
        }}

        .pan-topbar-title {{
            color: #FFFFFF;
            font-size: 0.94rem;
            font-weight: 700;
        }}

        .pan-topbar-subtitle {{
            color: #F0E2CD;
            font-size: 0.76rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .pan-topbar-meta {{
            align-items: center;
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            justify-content: flex-end;
        }}

        .pan-topbar-pill {{
            background: rgba(240, 241, 223, 0.16);
            border: 1px solid rgba(240, 226, 205, 0.32);
            border-radius: 999px;
            color: #FFFFFF;
            font-size: 0.74rem;
            font-weight: 600;
            padding: 0.25rem 0.62rem;
        }}

        @media (max-width: 900px) {{
            .pan-topbar {{
                align-items: flex-start;
                flex-direction: column;
            }}

            .pan-topbar-meta {{
                justify-content: flex-start;
            }}
        }}

        div[data-testid="stMetricLabel"] p {{
            color: var(--pan-muted);
            font-size: 0.74rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        div[data-testid="stMetricValue"] {{
            color: var(--pan-text);
            font-size: 1.55rem !important;
            font-weight: 700;
        }}

        div[data-testid="stPlotlyChart"],
        [data-testid="stDataFrame"],
        [data-testid="stExpander"] {{
            background: var(--pan-surface);
            border: 1px solid var(--pan-border);
            border-radius: 10px;
            box-shadow: var(--pan-soft-shadow);
            overflow: hidden;
        }}

        div[data-testid="stPlotlyChart"] {{
            padding: 1rem 1.05rem 0.75rem;
        }}

        div[data-testid="stPlotlyChart"] svg {{
            border-radius: 8px;
        }}

        div[data-testid="stPlotlyChart"] .js-plotly-plot,
        div[data-testid="stPlotlyChart"] .plot-container,
        div[data-testid="stPlotlyChart"] .svg-container {{
            background: #FFFFFF !important;
        }}

        [data-testid="stTabs"] button {{
            font-size: 0.86rem;
            font-weight: 600;
        }}

        [data-testid="stAlert"] {{
            border-radius: 10px;
            border: 1px solid var(--pan-border);
            background: var(--pan-alert-bg) !important;
            color: var(--pan-text);
            box-shadow: var(--pan-soft-shadow);
        }}

        [data-testid="stAlert"] p {{
            color: var(--pan-text);
        }}

        div[data-baseweb="notification"] {{
            background: var(--pan-alert-bg) !important;
            border: 1px solid var(--pan-border) !important;
            color: var(--pan-text) !important;
        }}

        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background: var(--pan-surface);
            border: 1px solid var(--pan-border);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: var(--pan-soft-shadow);
        }}

        th {{
            background: rgba(85, 198, 214, 0.12);
            color: var(--pan-text);
            font-weight: 700;
            padding: 0.75rem 0.85rem;
            border-bottom: 1px solid var(--pan-border);
        }}

        td {{
            color: var(--pan-text);
            padding: 0.65rem 0.85rem;
            border-bottom: 1px solid var(--pan-border);
        }}

        tr:last-child td {{
            border-bottom: 0;
        }}

        /* Custom sections */
        .pan-hero {{
            background:
                radial-gradient(circle at 95% 0%, rgba(240, 226, 205, 0.24), transparent 17rem),
                linear-gradient(135deg, rgba(49, 58, 85, 0.98), rgba(69, 89, 118, 0.96) 52%, rgba(130, 169, 199, 0.88)),
                var(--pan-dark);
            border: 1px solid rgba(178, 193, 201, 0.42);
            border-left: 5px solid var(--pan-accent);
            border-radius: 12px;
            padding: 1.55rem 1.75rem;
            margin-bottom: 1.15rem;
            box-shadow: var(--pan-shadow);
        }}

        .pan-hero h1 {{
            color: #FFFFFF !important;
            font-size: 2rem !important;
            margin: 0.28rem 0 0.55rem;
        }}

        .pan-hero p {{
            color: #F5F1E5;
            line-height: 1.6;
            margin: 0;
            max-width: 1120px;
            font-size: 0.96rem;
        }}

        .pan-eyebrow {{
            color: #F0E2CD;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }}

        .pan-page-head {{
            background: var(--pan-surface);
            border: 1px solid var(--pan-border);
            border-left: 4px solid var(--pan-accent);
            border-radius: 10px;
            padding: 1.05rem 1.25rem;
            margin-bottom: 1rem;
            box-shadow: var(--pan-soft-shadow);
        }}

        .pan-page-head h1 {{
            font-size: 1.45rem !important;
            margin: 0.15rem 0 0.3rem;
        }}

        .pan-page-head p {{
            color: var(--pan-muted);
            font-size: 0.91rem;
            line-height: 1.55;
            margin: 0;
        }}

        .pan-chip-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.75rem;
        }}

        .pan-chip {{
            background: var(--pan-chip-bg);
            border: 1px solid var(--pan-chip-border);
            border-radius: 999px;
            color: var(--pan-chip-text);
            font-size: 0.74rem;
            font-weight: 600;
            padding: 0.25rem 0.62rem;
        }}

        .pan-panel,
        .pan-module,
        .pan-insight,
        .pan-alert {{
            background: var(--pan-surface);
            border: 1px solid var(--pan-border);
            border-radius: 10px;
            box-shadow: var(--pan-soft-shadow);
        }}

        .pan-panel {{
            height: 100%;
            padding: 1rem 1.1rem;
        }}

        .pan-panel p,
        .pan-panel li {{
            color: var(--pan-muted);
            line-height: 1.55;
        }}

        .pan-module {{
            min-height: 126px;
            padding: 0.95rem 1rem;
            position: relative;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}

        .pan-module:hover {{
            transform: translateY(-2px);
            box-shadow: var(--pan-shadow);
        }}

        .pan-module strong {{
            color: var(--pan-text);
            display: block;
            font-size: 0.94rem;
            margin-bottom: 0.35rem;
        }}

        .pan-module span {{
            color: var(--pan-muted);
            font-size: 0.86rem;
            line-height: 1.45;
        }}

        .pan-insight {{
            background: var(--pan-insight-bg);
            border-left: 4px solid var(--pan-navy);
            color: var(--pan-text);
            font-size: 0.9rem;
            line-height: 1.55;
            margin: 0.55rem 0 0.9rem;
            padding: 0.85rem 1rem;
        }}

        .pan-alert {{
            background: var(--pan-alert-bg);
            border-left: 4px solid var(--pan-accent);
            color: var(--pan-text);
            font-size: 0.9rem;
            margin: 0.55rem 0 0.9rem;
            padding: 0.85rem 1rem;
        }}

        .pan-risk-badge {{
            border-radius: 999px;
            color: #FFFFFF;
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            padding: 0.18rem 0.55rem;
        }}

        .pan-divider {{
            border-top: 1px solid var(--pan-border);
            margin: 1.35rem 0 0.85rem;
            position: relative;
        }}

        .pan-kpi-divider {{
            border-top: 1px solid var(--pan-border);
            margin: 0.85rem 0 1.05rem;
        }}

        .pan-divider span {{
            background: var(--pan-bg);
            color: var(--pan-muted);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.09em;
            padding-right: 0.7rem;
            position: relative;
            text-transform: uppercase;
            top: -0.65rem;
        }}

        .pan-chart-footer {{
            color: var(--pan-muted);
            font-size: 0.7rem;
            margin-top: 0.3rem;
            padding-left: 0.25rem;
        }}

        .pan-breadcrumb {{
            color: var(--pan-muted);
            font-size: 0.75rem;
            margin-bottom: 0.5rem;
        }}

        .pan-section-pill {{
            background: var(--pan-dark);
            border-radius: 999px;
            color: #FFFFFF;
            display: inline-block;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            margin: 0.25rem 0 0.25rem;
            padding: 0.15rem 0.5rem;
        }}

        .pan-ticker {{
            align-items: center;
            background: var(--pan-dark);
            border-radius: 8px;
            display: flex;
            height: 32px;
            margin: 1rem 0;
            overflow: hidden;
        }}

        .pan-ticker-track {{
            animation: ticker 28s linear infinite;
            color: #F0E2CD;
            display: flex;
            font-size: 0.78rem;
            font-weight: 700;
            gap: 3rem;
            letter-spacing: 0.04em;
            padding-left: 100%;
            white-space: nowrap;
        }}

        .pan-module-number {{
            background: var(--pan-dark);
            border-radius: 999px;
            color: #FFFFFF;
            font-size: 0.68rem;
            font-weight: 700;
            padding: 0.18rem 0.45rem;
            position: absolute;
            right: 0.75rem;
            top: 0.75rem;
        }}

        .pan-module-cta {{
            border-top: 1px solid var(--pan-border);
            color: var(--pan-dark);
            font-size: 0.78rem;
            font-weight: 700;
            margin-top: 0.75rem;
            padding-top: 0.55rem;
        }}

        @keyframes ticker {{
            0% {{ transform: translateX(0); }}
            100% {{ transform: translateX(-50%); }}
        }}

        @keyframes shimmer {{
            0% {{ left: -65%; }}
            100% {{ left: 135%; }}
        }}

        @keyframes fadeSlideUp {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .pan-hero, .pan-page-head, div[data-testid="stMetric"] {{
            animation: fadeSlideUp 0.35s ease;
        }}

        div[data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.88) !important;
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(201, 189, 174, 0.40) !important;
            border-radius: 14px !important;
            padding: 1.1rem 1.25rem 1rem 1.25rem !important;
            box-shadow: 0 4px 24px rgba(49, 58, 85, 0.09), 0 1px 4px rgba(49, 58, 85, 0.05) !important;
            transition: transform 0.18s ease, box-shadow 0.18s ease;
            position: relative;
            overflow: hidden;
        }}

        div[data-testid="stMetric"]::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--pan-dark), var(--pan-navy));
            border-radius: 14px 14px 0 0;
        }}

        div[data-testid="stMetric"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(49, 58, 85, 0.14), 0 2px 8px rgba(49, 58, 85, 0.08) !important;
        }}

        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] p {{
            font-size: 0.68rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.09em !important;
            text-transform: uppercase;
            color: var(--pan-muted) !important;
        }}

        div[data-testid="stMetricValue"] {{
            font-size: 1.85rem !important;
            font-weight: 800 !important;
            color: var(--pan-text) !important;
            letter-spacing: -0.02em;
            line-height: 1.15;
        }}

        div[data-testid="stMetricDelta"] {{
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            border-radius: 20px;
            padding: 2px 8px;
            display: inline-block;
            margin-top: 4px;
        }}

        @keyframes fadeSlideUp {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .pan-hero, .pan-page-head {{
            animation: fadeSlideUp 0.4s ease both;
        }}

        div[data-testid="stMetric"] {{
            animation: fadeSlideUp 0.35s ease both;
        }}

        button[data-baseweb="tab"] {{
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em;
            border-radius: 8px 8px 0 0 !important;
            padding: 0.55rem 1.1rem !important;
            color: var(--pan-muted) !important;
            transition: color 0.15s ease, background 0.15s ease;
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            color: var(--pan-text) !important;
            background: rgba(130, 169, 199, 0.12) !important;
            border-bottom: 2px solid var(--pan-dark) !important;
        }}

        button[data-baseweb="tab"]:hover {{
            color: var(--pan-text) !important;
            background: rgba(201, 189, 174, 0.15) !important;
        }}

        details[data-testid="stExpander"] > summary {{
            background: rgba(255, 255, 255, 0.75) !important;
            border: 1px solid rgba(201, 189, 174, 0.4) !important;
            border-radius: 10px !important;
            padding: 0.75rem 1rem !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            transition: background 0.15s ease;
        }}

        details[data-testid="stExpander"] > summary:hover {{
            background: rgba(240, 226, 205, 0.35) !important;
        }}

        details[data-testid="stExpander"][open] > summary {{
            border-radius: 10px 10px 0 0 !important;
            border-bottom-color: transparent !important;
            background: rgba(130, 169, 199, 0.10) !important;
        }}

        details[data-testid="stExpander"] > div {{
            border: 1px solid rgba(201, 189, 174, 0.4) !important;
            border-top: none !important;
            border-radius: 0 0 10px 10px !important;
            padding: 1rem 1.1rem !important;
            background: rgba(255, 255, 255, 0.6) !important;
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid rgba(201, 189, 174, 0.35) !important;
            border-radius: 10px !important;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(49, 58, 85, 0.06);
        }}

        div[data-baseweb="select"] > div,
        div[data-baseweb="multi-select"] > div {{
            border-color: rgba(130, 169, 199, 0.55) !important;
            border-radius: 8px !important;
            background: rgba(255, 255, 255, 0.85) !important;
            font-size: 0.88rem !important;
            transition: border-color 0.15s ease;
        }}

        div[data-baseweb="select"] > div:hover,
        div[data-baseweb="multi-select"] > div:hover {{
            border-color: var(--pan-navy) !important;
        }}

        div[data-testid="stSlider"] > div > div > div[role="slider"] {{
            background: var(--pan-dark) !important;
            border: 2px solid #FFFFFF !important;
            box-shadow: 0 2px 8px rgba(49, 58, 85, 0.25) !important;
        }}

        div[data-testid="stSlider"] > div > div > div[data-baseweb="slider"] > div:first-child {{
            background: linear-gradient(90deg, var(--pan-dark), var(--pan-navy)) !important;
        }}

        div[data-testid="stPlotlyChart"] {{
            background: #FFFFFF !important;
            border-radius: 12px !important;
            border: 1px solid rgba(201, 189, 174, 0.30) !important;
            box-shadow: 0 3px 16px rgba(49, 58, 85, 0.07) !important;
            padding: 0.5rem !important;
            transition: box-shadow 0.18s ease;
        }}

        div[data-testid="stPlotlyChart"]:hover {{
            box-shadow: 0 6px 28px rgba(49, 58, 85, 0.11) !important;
        }}

        div[data-testid="stAlert"] {{
            border-radius: 10px !important;
            border-left-width: 4px !important;
            font-size: 0.88rem !important;
            font-weight: 500;
        }}

        div[data-testid="stAlert"][data-type="info"] {{
            background: rgba(172, 204, 216, 0.18) !important;
            border-left-color: var(--pan-navy) !important;
        }}

        div[data-testid="stAlert"][data-type="warning"] {{
            background: rgba(240, 226, 205, 0.45) !important;
            border-left-color: var(--pan-amber) !important;
        }}

        div[data-testid="stAlert"][data-type="success"] {{
            background: rgba(71, 111, 103, 0.12) !important;
            border-left-color: var(--pan-green) !important;
        }}

        div[data-testid="stAlert"][data-type="error"] {{
            background: rgba(192, 57, 43, 0.10) !important;
            border-left-color: #C0392B !important;
        }}

        div[data-testid="stSpinner"] > div {{
            border-top-color: var(--pan-dark) !important;
        }}

        div[data-testid="stSpinner"] p {{
            font-size: 0.85rem !important;
            color: var(--pan-muted) !important;
            font-weight: 500;
        }}

        .pan-section-divider {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin: 1.75rem 0 1.25rem 0;
        }}

        .pan-section-divider-line {{
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(130, 169, 199, 0.45), transparent);
        }}

        .pan-section-divider-label {{
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--pan-muted);
            white-space: nowrap;
            padding: 0 0.25rem;
        }}

        .pan-hr {{
            border: none;
            border-top: 1px solid rgba(130, 169, 199, 0.30);
            margin: 1.5rem 0;
        }}

        .pan-insight-card {{
            display: flex;
            gap: 1rem;
            align-items: flex-start;
            background: rgba(172, 204, 216, 0.14);
            border: 1px solid rgba(130, 169, 199, 0.35);
            border-left: 4px solid var(--pan-navy);
            border-radius: 10px;
            padding: 1rem 1.15rem;
            margin: 0.75rem 0;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.55);
        }}

        .pan-insight-icon {{
            font-size: 1.3rem;
            line-height: 1.4;
            flex-shrink: 0;
        }}

        .pan-insight-title {{
            font-size: 0.83rem;
            font-weight: 700;
            color: var(--pan-text);
            margin-bottom: 0.2rem;
            letter-spacing: 0.01em;
        }}

        .pan-insight-body {{
            font-size: 0.87rem;
            color: var(--pan-muted);
            line-height: 1.6;
        }}

        .pan-alert-card {{
            display: flex;
            gap: 0.75rem;
            align-items: flex-start;
            background: rgba(240, 226, 205, 0.55);
            border: 1px solid rgba(138, 111, 82, 0.35);
            border-left: 4px solid var(--pan-amber);
            border-radius: 10px;
            padding: 0.9rem 1.1rem;
            margin: 0.5rem 0;
            font-size: 0.87rem;
            color: var(--pan-text);
        }}

        .pan-alert-icon {{
            font-size: 1.1rem;
            flex-shrink: 0;
            color: var(--pan-amber);
        }}

        .pan-page-head {{
            background:
                repeating-linear-gradient(0deg, rgba(130, 169, 199, 0.04) 0px, rgba(130, 169, 199, 0.04) 1px, transparent 1px, transparent 40px),
                repeating-linear-gradient(90deg, rgba(130, 169, 199, 0.04) 0px, rgba(130, 169, 199, 0.04) 1px, transparent 1px, transparent 40px),
                linear-gradient(135deg, var(--pan-dark) 0%, #455976 100%) !important;
            border-radius: 16px !important;
            padding: 2rem 2.5rem !important;
            margin-bottom: 1.75rem !important;
            position: relative;
            overflow: hidden;
        }}

        .pan-page-head::after {{
            content: "";
            position: absolute;
            top: -30%;
            right: -5%;
            width: 320px;
            height: 320px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(172, 204, 216, 0.18), transparent 70%);
            pointer-events: none;
        }}

        .pan-page-head h1,
        .pan-page-head p {{
            color: #FFFFFF !important;
            position: relative;
            z-index: 1;
        }}

        div[data-testid="stPlotlyChart"] .gauge .arc path {{
            stroke-width: 0;
        }}

        [data-testid="stToggle"] > label {{
            font-weight: 600;
            font-size: 0.88rem;
            color: var(--pan-text);
        }}

        div[data-testid="stNumberInput"] > div > div > input {{
            border: 1px solid rgba(130, 169, 199, 0.55);
            border-radius: 8px;
            font-size: 0.88rem;
        }}

        div[data-testid="stDownloadButton"] button {{
            background: var(--pan-dark);
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.85rem;
            padding: 0.55rem 1.25rem;
            transition: background 0.15s ease;
        }}

        div[data-testid="stDownloadButton"] button:hover {{
            background: var(--pan-navy);
        }}

        .pan-roi-card {{
            background: var(--pan-surface);
            border: 1px solid var(--pan-border);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: var(--pan-soft-shadow);
        }}

        .pan-roi-value {{
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--pan-text);
            letter-spacing: 0;
        }}

        .pan-roi-label {{
            font-size: 0.8rem;
            color: var(--pan-muted);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-top: 0.35rem;
        }}

        .pan-go {{
            background: rgba(71, 111, 103, 0.12);
            border: 1px solid rgba(71, 111, 103, 0.35);
            border-left: 4px solid #476F67;
        }}

        .pan-nogo {{
            background: rgba(192, 57, 43, 0.10);
            border: 1px solid rgba(192, 57, 43, 0.35);
            border-left: 4px solid #C0392B;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    from utils.data_loader import load_data
    from utils.kpis import attrition_rate, attrition_summary, cost_of_attrition

    df = load_data()
    summary = attrition_summary(df)
    cost = cost_of_attrition(df)
    top_dept = attrition_rate(df, "Department").sort_values("Rate", ascending=False).iloc[0]
    ot_rate = df[df["OverTime"] == "Yes"]["Attrition"].mean() * 100
    non_ot_rate = df[df["OverTime"] == "No"]["Attrition"].mean() * 100
    st.markdown(
        f"""
        <div class="pan-topbar">
            <div>
                <div class="pan-topbar-subtitle">Palo Alto Networks | Workforce Analytics</div>
                <div class="pan-topbar-title">Workforce Attrition Intelligence</div>
            </div>
            <div class="pan-topbar-meta">
                <span class="pan-topbar-pill">{summary['total']:,} employees</span>
                <span class="pan-topbar-pill">{summary['rate']}% attrition</span>
                <span class="pan-topbar-pill">Hotspot: {top_dept['Department']}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="pan-ticker">
            <div class="pan-ticker-track">
                <span>Overall Attrition: {summary['rate']}%</span>
                <span>&#8202;</span>
                <span>Dept Hotspot: {top_dept['Department']} - {top_dept['Rate']:.1f}%</span>
                <span>&#8202;</span>
                <span>Overtime Lift: {ot_rate - non_ot_rate:+.1f} pts</span>
                <span>&#8202;</span>
                <span>Retained: {summary['stayed']:,} employees</span>
                <span>&#8202;</span>
                <span>Overall Attrition: {summary['rate']}%</span>
                <span>&#8202;</span>
                <span>Dept Hotspot: {top_dept['Department']} - {top_dept['Rate']:.1f}%</span>
                <span>&#8202;</span>
                <span>Overtime Lift: {ot_rate - non_ot_rate:+.1f} pts</span>
                <span>&#8202;</span>
                <span>Retained: {summary['stayed']:,} employees</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <div class="pan-sidebar-brand">
            <div class="pan-brand-kicker">Palo Alto Networks</div>
            <div class="pan-brand-title">Workforce Intelligence</div>
            <div class="pan-brand-sub">Attrition analytics for HR leadership</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.page_link("pages/01_Overview.py", label="Overview")
    st.sidebar.page_link("pages/02_Department_Role.py", label="Department & Role")
    st.sidebar.page_link("pages/03_Demographics.py", label="Demographics")
    st.sidebar.page_link("pages/04_Tenure_Workload.py", label="Tenure & Workload")
    st.sidebar.page_link("pages/05_Risk_Score.py", label="Risk Score")
    st.sidebar.page_link("pages/06_Compensation.py", label="Compensation")
    st.sidebar.page_link("pages/07_Executive_Summary.py", label="Executive Summary")
    st.sidebar.page_link("pages/08_Cohort_Analysis.py", label="Cohort Analysis")
    st.sidebar.page_link("pages/09_What_If_Simulator.py", label="What-If Simulator")
    st.sidebar.page_link("pages/10_Survival_Analysis.py", label="Survival Analysis")
    st.sidebar.page_link("pages/11_Retention_ROI.py", label="Retention ROI")
    st.sidebar.page_link("pages/12_Recommendations.py", label="Action Plan")
    st.sidebar.markdown("---")
    avg_risk = st.session_state.get("avg_risk_score")
    avg_risk_row = (
        f'<div class="pan-snapshot-row"><span class="pan-snapshot-label">Avg Risk Score</span><span class="pan-snapshot-value">{avg_risk:.1f}</span></div>'
        if avg_risk is not None
        else ""
    )
    snapshot_html = (
        '<div class="pan-sidebar-snapshot">'
        '<div class="pan-sidebar-snapshot-title">Live Snapshot</div>'
        f'<div class="pan-snapshot-row"><span class="pan-snapshot-label">Headcount</span><span class="pan-snapshot-value">{summary["total"]:,}</span></div>'
        f'<div class="pan-snapshot-row"><span class="pan-snapshot-label">Attrition</span><span class="pan-snapshot-value alert">{summary["rate"]}%</span></div>'
        f'<div class="pan-snapshot-row"><span class="pan-snapshot-label">Exited</span><span class="pan-snapshot-value">{summary["left"]:,}</span></div>'
        f'<div class="pan-snapshot-row"><span class="pan-snapshot-label">Retained</span><span class="pan-snapshot-value good">{summary["stayed"]:,}</span></div>'
        f'<div class="pan-snapshot-row"><span class="pan-snapshot-label">Hotspot</span><span class="pan-snapshot-value">{top_dept["Department"]}</span></div>'
        f'{avg_risk_row}'
        f'<div class="pan-snapshot-row"><span class="pan-snapshot-label">Est. Annual Cost</span><span class="pan-snapshot-value">&#36;{cost["total_annual_cost"]:,.0f}</span></div>'
        "</div>"
    )
    st.sidebar.markdown(snapshot_html, unsafe_allow_html=True)
    st.sidebar.markdown("---")


def render_global_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render reusable sidebar filters and store the filtered frame in session state."""
    from utils.config import JOB_LEVEL_LABELS

    st.sidebar.markdown("### Global Workforce Filters")
    filter_keys = [
        "g_depts",
        "g_roles",
        "g_tenure",
        "g_overtime",
        "g_travel",
        "g_gender",
        "g_education_field",
        "g_job_level",
        "g_attrition_only",
    ]
    if st.sidebar.button("Reset All Filters", use_container_width=True):
        for key in filter_keys:
            st.session_state.pop(key, None)
        st.rerun()
    departments = sorted(df["Department"].dropna().unique())
    dept_default = [dept for dept in st.session_state.get("g_depts", departments) if dept in departments] or departments
    selected_depts = st.sidebar.multiselect("Department", departments, default=dept_default, key="g_depts")
    roles = sorted(df[df["Department"].isin(selected_depts)]["JobRole"].dropna().unique())
    role_default = [role for role in st.session_state.get("g_roles", roles) if role in roles] or roles
    selected_roles = st.sidebar.multiselect(
        "Job Role",
        roles,
        default=role_default,
        key="g_roles",
    )
    tenure_min = int(df["YearsAtCompany"].min())
    tenure_max = int(df["YearsAtCompany"].max())
    prior_tenure = st.session_state.get("g_tenure", (tenure_min, tenure_max))
    tenure_default = (max(tenure_min, prior_tenure[0]), min(tenure_max, prior_tenure[1]))
    tenure_range = st.sidebar.slider(
        "Years at Company",
        tenure_min,
        tenure_max,
        value=tenure_default,
        key="g_tenure",
    )
    overtime_options = ["Yes", "No"]
    overtime_default = [item for item in st.session_state.get("g_overtime", overtime_options) if item in overtime_options] or overtime_options
    overtime = st.sidebar.multiselect("OverTime", overtime_options, default=overtime_default, key="g_overtime")
    travel = sorted(df["BusinessTravel"].dropna().unique())
    travel_default = [item for item in st.session_state.get("g_travel", travel) if item in travel] or travel
    selected_travel = st.sidebar.multiselect("Business Travel", travel, default=travel_default, key="g_travel")
    gender = sorted(df["Gender"].dropna().unique())
    gender_default = [item for item in st.session_state.get("g_gender", gender) if item in gender] or gender
    selected_gender = st.sidebar.multiselect("Gender", gender, default=gender_default, key="g_gender")
    edu_fields = sorted(df["EducationField"].dropna().unique())
    edu_default = [item for item in st.session_state.get("g_education_field", edu_fields) if item in edu_fields] or edu_fields
    selected_edu = st.sidebar.multiselect("Education Field", edu_fields, default=edu_default, key="g_education_field")
    job_levels = sorted(df["JobLevel"].dropna().unique())
    level_default = [item for item in st.session_state.get("g_job_level", job_levels) if item in job_levels] or job_levels
    selected_levels = st.sidebar.multiselect(
        "Job Level",
        job_levels,
        default=level_default,
        key="g_job_level",
        format_func=lambda value: JOB_LEVEL_LABELS.get(value, str(value)),
    )
    attrition_only = st.sidebar.toggle("Show Exited Employees Only", key="g_attrition_only")
    filtered = df[
        df["Department"].isin(selected_depts)
        & df["JobRole"].isin(selected_roles)
        & df["YearsAtCompany"].between(tenure_range[0], tenure_range[1])
        & df["OverTime"].isin(overtime)
        & df["BusinessTravel"].isin(selected_travel)
        & df["Gender"].isin(selected_gender)
        & df["EducationField"].isin(selected_edu)
        & df["JobLevel"].isin(selected_levels)
    ]
    if attrition_only:
        filtered = filtered[filtered["Attrition"] == 1]
    st.sidebar.markdown("---")
    pct = len(filtered) / len(df) * 100 if len(df) else 0
    st.sidebar.metric("Filtered Records", f"{len(filtered):,}", delta=f"{pct:.0f}% of workforce")
    baseline = df["Attrition"].mean() * 100
    filtered_rate = filtered["Attrition"].mean() * 100 if len(filtered) else 0
    st.sidebar.metric("Filtered Attrition Rate", f"{filtered_rate:.1f}%", delta=f"{filtered_rate - baseline:+.1f}% vs baseline", delta_color="inverse")
    if len(filtered) < 30:
        st.sidebar.warning("Small sample - statistical results may be unreliable.")
    st.session_state["filtered_df"] = filtered
    return filtered


def breadcrumb(label: str) -> None:
    """Render a page breadcrumb."""
    st.markdown(f'<div class="pan-breadcrumb">Workforce Intelligence &rsaquo; {label}</div>', unsafe_allow_html=True)


def section_badge(number: int) -> None:
    """Render a compact section counter pill."""
    st.markdown(f'<span class="pan-section-pill">{number:02d}</span>', unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, subtitle: str, chips: list[str] | None = None) -> None:
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


def hero(title: str, subtitle: str, eyebrow: str = "Palo Alto Networks") -> None:
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


def insight_card(title: str, body: str, icon: str = "💡") -> None:
    """Styled insight card with icon, title, and body text."""
    st.markdown(
        f"""
        <div class="pan-insight-card">
            <div class="pan-insight-icon">{icon}</div>
            <div>
                <div class="pan-insight-title">{title}</div>
                <div class="pan-insight-body">{body}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_card(body: str) -> None:
    """Styled alert card for high-priority warnings."""
    st.markdown(
        f'<div class="pan-alert-card"><span class="pan-alert-icon">⚠</span>{body}</div>',
        unsafe_allow_html=True,
    )


def roi_card(value: str, label: str, go: bool = True) -> None:
    """Render a compact ROI decision card."""
    cls = "pan-roi-card pan-go" if go else "pan-roi-card pan-nogo"
    st.markdown(
        f'<div class="{cls}"><div class="pan-roi-value">{value}</div><div class="pan-roi-label">{label}</div></div>',
        unsafe_allow_html=True,
    )


def benchmark_table(rows: list[dict]) -> None:
    """Render a benchmark comparison table with status indicators."""
    html = "<table><thead><tr><th>Metric</th><th>Company</th><th>Industry Avg</th><th>Status</th></tr></thead><tbody>"
    for row in rows:
        status_icon = "Good" if row["status"] == "good" else ("Watch" if row["status"] == "warn" else "Risk")
        html += (
            f'<tr><td>{row["metric"]}</td><td><strong>{row["company"]}</strong></td>'
            f'<td>{row["industry"]}</td><td>{status_icon}</td></tr>'
        )
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


def risk_badge(rate: float, baseline: float) -> str:
    if rate > baseline * 1.5:
        color = "#313A55"
        label = "HIGH RISK"
    elif rate > baseline * 1.1:
        color = "#82A9C7"
        label = "ELEVATED"
    else:
        color = "#476F67"
        label = "BELOW BASE"
    return f'<span class="pan-risk-badge" style="background:{color};">{label}</span>'


def data_quality_banner(df: pd.DataFrame) -> None:
    nulls = int(df.isna().sum().sum())
    duplicate_count = int(df["EmployeeNumber"].duplicated().sum()) if "EmployeeNumber" in df.columns else 0
    attrition_ok = pd.api.types.is_integer_dtype(df["Attrition"])
    if nulls == 0 and duplicate_count == 0 and attrition_ok:
        st.success(f"Data validated: {len(df):,} records, {len(df.columns)} fields, no missing values.")
    else:
        st.warning(
            f"Data quality: {nulls:,} missing values, {duplicate_count:,} duplicate employee IDs, "
            f"Attrition integer type: {attrition_ok}."
        )


def section_divider(label: str = "") -> None:
    """Render a styled section divider with optional label."""
    if label:
        st.markdown(
            f"""
            <div class="pan-section-divider">
                <span class="pan-section-divider-line"></span>
                <span class="pan-section-divider-label">{label}</span>
                <span class="pan-section-divider-line"></span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<hr class="pan-hr">', unsafe_allow_html=True)


def chart_caption(n: int, suffix: str = "") -> None:
    caption = f"Source: Palo Alto Networks HR Dataset | n = {n:,}"
    if suffix:
        caption += f" | {suffix}"
    st.markdown(f'<div class="pan-chart-footer">{caption}</div>', unsafe_allow_html=True)


def download_filtered_data(df: pd.DataFrame, filename: str) -> None:
    with st.expander("Download Filtered Data"):
        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=filename,
            mime="text/csv",
            use_container_width=True,
        )
