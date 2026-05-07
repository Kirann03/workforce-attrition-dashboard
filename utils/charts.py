import plotly.express as px
import plotly.io as pio


STATUS_COLORS = {"Left": "#D83A22", "Stayed": "#1A9A74"}
RISK_COLORS = {"High": "#D83A22", "Medium": "#F29D38", "Low": "#1A9A74"}

pio.templates["pan_professional"] = {
    "layout": {
        "font": {"family": "Inter, Segoe UI, Arial, sans-serif", "color": "#17202A"},
        "paper_bgcolor": "#FFFFFF",
        "plot_bgcolor": "#FFFFFF",
        "colorway": ["#FA582D", "#1A9A74", "#335C81", "#F2B134", "#6C5CE7", "#657786"],
        "margin": {"l": 48, "r": 28, "t": 52, "b": 46},
        "xaxis": {"gridcolor": "#E6ECF2", "linecolor": "#CAD4DF", "zerolinecolor": "#E6ECF2"},
        "yaxis": {"gridcolor": "#E6ECF2", "linecolor": "#CAD4DF", "zerolinecolor": "#E6ECF2"},
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    }
}
pio.templates.default = "pan_professional"


def rate_bar(data, x, y="Rate", text="Rate", color="Rate", height=360, scale="RdYlGn_r"):
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
    fig.update_layout(height=height, coloraxis_showscale=False, template="pan_professional")
    return fig


def polish(fig, height=None):
    fig.update_layout(template="pan_professional")
    if height:
        fig.update_layout(height=height)
    return fig
