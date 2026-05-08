import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


DEEP_NAVY = "#313A55"
STEEL_BLUE = "#82A9C7"
CALM_CYAN = "#ACCCD8"
MINT = "#F0E2CD"
IVORY = "#F0F1DF"
STONE = "#C9BDAE"
AMBER = "#8A6F52"
RATE_SCALE = [IVORY, MINT, CALM_CYAN, STEEL_BLUE, DEEP_NAVY]
EXIT_SCALE = [IVORY, MINT, CALM_CYAN, STEEL_BLUE, DEEP_NAVY]

STATUS_COLORS = {"Left": DEEP_NAVY, "Stayed": MINT}
RISK_COLORS = {"High": DEEP_NAVY, "Medium": STEEL_BLUE, "Low": MINT}

pio.templates["pan_professional"] = {
    "layout": {
        "font": {"family": "DM Sans, Segoe UI, Arial, sans-serif"},
        "paper_bgcolor": "#FFFFFF",
        "plot_bgcolor": "#FFFFFF",
        "colorway": [DEEP_NAVY, STEEL_BLUE, CALM_CYAN, MINT, STONE, "#66728E"],
        "margin": {"l": 64, "r": 34, "t": 28, "b": 78},
        "font_color": "#1D2638",
        "xaxis": {
            "gridcolor": "rgba(130, 169, 199, 0.22)",
            "linecolor": "rgba(49, 58, 85, 0.22)",
            "zerolinecolor": "rgba(130, 169, 199, 0.22)",
        },
        "yaxis": {
            "gridcolor": "rgba(130, 169, 199, 0.22)",
            "linecolor": "rgba(49, 58, 85, 0.22)",
            "zerolinecolor": "rgba(130, 169, 199, 0.22)",
        },
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        "coloraxis": {"colorbar": {"outlinewidth": 0}},
    }
}
pio.templates.default = "pan_professional"


def add_baseline(fig: go.Figure, baseline_rate: float, label: str | None = None) -> go.Figure:
    """Add an attrition baseline line to a Plotly figure."""
    label = label or f"Baseline {baseline_rate:.1f}%"
    fig.add_hline(y=baseline_rate, line_dash="dash", line_color=DEEP_NAVY, annotation_text=label)
    return fig


def sankey(labels: list, sources: list, targets: list, values: list, title: str = "Flow") -> go.Figure:
    """Create a styled Sankey flow chart."""
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(label=labels, pad=16, thickness=16, color=CALM_CYAN),
                link=dict(source=sources, target=targets, value=values, color="rgba(130,169,199,0.38)"),
            )
        ]
    )
    return polish(fig, 420, title=title)


def waterfall(labels: list, values: list, title: str = "Waterfall") -> go.Figure:
    """Create a styled waterfall chart."""
    fig = go.Figure(
        go.Waterfall(
            x=labels,
            y=values,
            measure=["relative"] * len(values),
            connector={"line": {"color": "#C9D2D6"}},
            increasing={"marker": {"color": DEEP_NAVY}},
            decreasing={"marker": {"color": MINT}},
        )
    )
    return polish(fig, 360, title=title)


def rate_bar(
    data: pd.DataFrame,
    x: str,
    y: str = "Rate",
    text: str = "Rate",
    color: str = "Rate",
    height: int = 360,
    scale: list[str] | None = None,
    title: str | None = None,
) -> go.Figure:
    """Create a standard attrition-rate bar chart."""
    scale = scale or RATE_SCALE
    fig = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        color_continuous_scale=scale,
        text=text,
        labels={"Rate": "Attrition Rate (%)"},
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, height, title=title)
    fig.update_layout(coloraxis_showscale=False)
    return fig


def grouped_rate_bar(data: pd.DataFrame, x: str, group_col: str, height: int = 380, title: str | None = None) -> go.Figure:
    """Create a grouped bar chart comparing attrition rates across two dimensions."""
    fig = px.bar(
        data,
        x=x,
        y="Rate",
        color=group_col,
        barmode="group",
        text="Rate",
        labels={"Rate": "Attrition Rate (%)"},
        color_discrete_sequence=[DEEP_NAVY, STEEL_BLUE, CALM_CYAN, MINT],
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    return polish(fig, height, title=title)


def annotated_scatter(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: str,
    hover_name: str,
    size: str | None = None,
    title: str | None = None,
    height: int = 460,
) -> go.Figure:
    """Create a labeled scatter plot with median quadrant reference lines."""
    fig = px.scatter(
        data,
        x=x,
        y=y,
        color=color,
        hover_name=hover_name,
        size=size,
        text=hover_name,
        color_discrete_sequence=[DEEP_NAVY, STEEL_BLUE, CALM_CYAN, STONE],
        labels={x: x.replace("_", " "), y: y.replace("_", " ")},
    )
    fig.update_traces(textposition="top center", marker=dict(opacity=0.8))
    fig.add_vline(x=data[x].median(), line_dash="dot", line_color=STONE, opacity=0.6)
    fig.add_hline(y=data[y].median(), line_dash="dot", line_color=STONE, opacity=0.6)
    return polish(fig, height, title=title)


def stacked_100_bar(data: pd.DataFrame, x: str, color_col: str, title: str | None = None, height: int = 360) -> go.Figure:
    """Create a 100 percent stacked bar showing composition per group."""
    totals = data.groupby(x, observed=False)[color_col].transform("sum")
    chart_data = data.copy()
    chart_data["Share"] = (chart_data[color_col] / totals * 100).round(1)
    fig = px.bar(
        chart_data,
        x=x,
        y="Share",
        color="Attrition_Label" if "Attrition_Label" in chart_data.columns else color_col,
        barmode="stack",
        text="Share",
        color_discrete_map=STATUS_COLORS,
        labels={"Share": "Share (%)"},
    )
    fig.update_traces(texttemplate="%{text:.0f}%", textposition="inside")
    return polish(fig, height, title=title)


def polish(fig: go.Figure, height: int = 400, title: str | None = None) -> go.Figure:
    """Apply the pan_professional theme and standard sizing to any Plotly figure."""
    fig.update_layout(template="pan_professional")
    axis_title_map = {
        "Rate": "Attrition Rate (%)",
        "AgeGroup": "Age Group",
        "EducationLabel": "Education Level",
        "Attrition_Label": "Employee Status",
        "YearsAtCompany": "Years at Company",
        "TotalWorkingYears": "Total Working Years",
        "MonthlyIncome": "Monthly Income",
        "PercentSalaryHike": "Salary Hike (%)",
        "RiskScore": "Risk Score",
        "RiskTier": "Risk Tier",
        "JobRole": "Job Role",
        "JobLevelLabel": "Job Level",
        "DistanceBand": "Distance from Home Band",
        "IncomeBand": "Income Band",
        "OverTime": "Overtime",
        "BusinessTravel": "Business Travel",
        "MaritalStatus": "Marital Status",
        "EducationField": "Education Field",
        "StockOptionLevel": "Stock Option Level",
    }
    x_title = fig.layout.xaxis.title.text
    y_title = fig.layout.yaxis.title.text
    if x_title in axis_title_map:
        fig.update_xaxes(title_text=axis_title_map[x_title])
    if y_title in axis_title_map:
        fig.update_yaxes(title_text=axis_title_map[y_title])
    updates: dict = {
        "height": height,
        "template": "pan_professional",
        "paper_bgcolor": "#FFFFFF",
        "plot_bgcolor": "#FFFFFF",
        "font": {"family": "DM Sans, Segoe UI, Arial, sans-serif", "size": 13, "color": "#1D2638"},
        "margin": {"l": 60, "r": 30, "t": 44 if title else 22, "b": 64},
        "hoverlabel": {
            "bgcolor": "#313A55",
            "font_color": "#FFFFFF",
            "font_size": 12,
            "font_family": "DM Sans, Segoe UI, Arial, sans-serif",
            "bordercolor": "#313A55",
        },
        "legend": {
            "bgcolor": "rgba(255,255,255,0)",
            "font": {"color": "#1D2638", "size": 12},
            "title_font": {"color": "#1D2638", "size": 12},
        },
    }
    if title:
        updates["title"] = {
            "text": title,
            "font": {"size": 15, "color": "#1D2638", "family": "DM Sans, Segoe UI, Arial, sans-serif"},
            "x": 0.02,
            "xanchor": "left",
            "y": 0.97,
            "yanchor": "top",
        }
    else:
        updates["title"] = {"text": ""}
    fig.update_layout(**updates)
    fig.update_xaxes(
        gridcolor="rgba(130, 169, 199, 0.22)",
        linecolor="rgba(49, 58, 85, 0.22)",
        zerolinecolor="rgba(130, 169, 199, 0.22)",
        tickfont=dict(color="#1D2638"),
        title_font=dict(color="#1D2638"),
        automargin=True,
    )
    fig.update_yaxes(
        gridcolor="rgba(130, 169, 199, 0.22)",
        linecolor="rgba(49, 58, 85, 0.22)",
        zerolinecolor="rgba(130, 169, 199, 0.22)",
        tickfont=dict(color="#1D2638"),
        title_font=dict(color="#1D2638"),
        automargin=True,
    )
    return fig


def gauge_chart(
    value: float,
    title: str = "Risk Score",
    low_threshold: float = 30,
    high_threshold: float = 60,
) -> go.Figure:
    """Create a Plotly gauge chart for risk scores."""
    if value >= high_threshold:
        bar_color = DEEP_NAVY
    elif value >= low_threshold:
        bar_color = STEEL_BLUE
    else:
        bar_color = "#476F67"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            delta={"reference": 50, "suffix": " vs mid"},
            title={"text": title, "font": {"size": 16, "family": "DM Sans"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": bar_color, "thickness": 0.25},
                "steps": [
                    {"range": [0, low_threshold], "color": IVORY},
                    {"range": [low_threshold, high_threshold], "color": CALM_CYAN},
                    {"range": [high_threshold, 100], "color": STONE},
                ],
                "threshold": {
                    "line": {"color": DEEP_NAVY, "width": 4},
                    "thickness": 0.75,
                    "value": value,
                },
            },
        )
    )
    return polish(fig, 300)


def km_curve_chart(
    km_df: pd.DataFrame,
    ci_df: pd.DataFrame | None,
    group_col: str | None = None,
    title: str = "Survival Curve",
) -> go.Figure:
    """Build a Plotly Kaplan-Meier survival curve with CI bands."""
    colors = [DEEP_NAVY, STEEL_BLUE, CALM_CYAN, "#476F67", STONE, AMBER]
    fig = go.Figure()
    groups = km_df[group_col].dropna().unique() if group_col and group_col in km_df.columns else [None]
    for i, group in enumerate(groups):
        if group is None:
            subset = km_df
            ci_sub = ci_df
            name = "All Employees"
        else:
            subset = km_df[km_df[group_col] == group]
            ci_sub = ci_df[ci_df[group_col] == group] if ci_df is not None and group_col in ci_df.columns else None
            name = str(group)
        color = colors[i % len(colors)]
        fig.add_trace(
            go.Scatter(
                x=subset["timeline"],
                y=subset["KM_estimate"],
                mode="lines",
                name=name,
                line=dict(color=color, width=2.6),
            )
        )
        if ci_sub is not None and not ci_sub.empty:
            fig.add_trace(
                go.Scatter(
                    x=list(ci_sub["timeline"]) + list(ci_sub["timeline"].iloc[::-1]),
                    y=list(ci_sub["KM_estimate_upper_0.95"]) + list(ci_sub["KM_estimate_lower_0.95"].iloc[::-1]),
                    fill="toself",
                    fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.12)",
                    line=dict(width=0),
                    showlegend=False,
                    name=f"{name} CI",
                )
            )
    fig.update_yaxes(range=[0, 1.05], title_text="Survival Probability")
    fig.update_xaxes(title_text="Years at Company")
    return polish(fig, 450, title=title)
