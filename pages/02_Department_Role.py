import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.charts import STATUS_COLORS, polish
from utils.data_loader import load_data
from utils.kpis import attrition_rate
from utils.theme import apply_theme, chart_caption, data_quality_banner, download_filtered_data, page_header, render_sidebar


st.set_page_config(page_title="Department & Role Analysis", page_icon="📊", layout="wide")
apply_theme()
render_sidebar()

df = load_data()
data_quality_banner(df)

page_header(
    "Functional Hotspots",
    "Department & Role Attrition Analysis",
    "Compare attrition rates against the company baseline, separate rate hotspots from exit-volume hotspots, and prioritize specific role interventions.",
    ["Department selector", "Job role filter", "Benchmark line", "Hotspot callout"],
)

st.sidebar.header("Workforce Filters")
departments = sorted(df["Department"].dropna().unique().tolist())
selected_depts = st.sidebar.multiselect("Select Departments", departments, default=departments)
roles = sorted(df[df["Department"].isin(selected_depts)]["JobRole"].dropna().unique().tolist())
selected_roles = st.sidebar.multiselect("Select Job Roles", roles, default=roles)
tenure_range = st.sidebar.slider(
    "Years at Company",
    int(df["YearsAtCompany"].min()),
    int(df["YearsAtCompany"].max()),
    (int(df["YearsAtCompany"].min()), int(df["YearsAtCompany"].max())),
)
overtime = st.sidebar.multiselect("OverTime", ["Yes", "No"], default=["Yes", "No"])
travel = sorted(df["BusinessTravel"].dropna().unique().tolist())
selected_travel = st.sidebar.multiselect("Business Travel", travel, default=travel)
df_filtered = df[
    df["Department"].isin(selected_depts)
    & df["JobRole"].isin(selected_roles)
    & df["YearsAtCompany"].between(tenure_range[0], tenure_range[1])
    & df["OverTime"].isin(overtime)
    & df["BusinessTravel"].isin(selected_travel)
]
st.sidebar.metric("Filtered Records", len(df_filtered))

if df_filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

baseline = df["Attrition"].mean() * 100

col1, col2 = st.columns([1, 1.1])
with col1:
    st.subheader("Attrition Count by Department")
    dept_att = df_filtered.groupby(["Department", "Attrition_Label"], observed=False).size().reset_index(name="Count")
    fig = px.bar(dept_att, x="Department", y="Count", color="Attrition_Label", barmode="group", color_discrete_map=STATUS_COLORS)
    polish(fig, 380)
    fig.update_layout(legend_title="Status")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df_filtered))

with col2:
    st.subheader("Department Attrition vs Company Baseline")
    dept_rate = attrition_rate(df_filtered, "Department").sort_values("Rate")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=dept_rate["Rate"], y=dept_rate["Department"], orientation="h", text=dept_rate["Rate"], marker_color="#FA582D"))
    fig.add_vline(x=baseline, line_dash="dash", line_color="#D83A22", annotation_text=f"Baseline {baseline:.1f}%")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    polish(fig, 380)
    fig.update_layout(xaxis_title="Attrition Rate (%)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df_filtered))

st.markdown("---")
st.subheader("Job Role Attrition Heatmaps")
role_dept = df_filtered.groupby(["JobRole", "Department"], observed=False).agg(
    Total=("Attrition", "count"),
    Left=("Attrition", "sum"),
).reset_index()
role_dept["Rate"] = (role_dept["Left"] / role_dept["Total"] * 100).fillna(0).round(1)

tab_rate, tab_count = st.tabs(["Attrition Rate", "Exit Count"])
with tab_rate:
    pivot = role_dept.pivot(index="JobRole", columns="Department", values="Rate").fillna(0)
    fig = px.imshow(pivot, color_continuous_scale="RdYlGn_r", text_auto=True, aspect="auto", labels=dict(color="Attrition %"))
    polish(fig, 430)
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df_filtered))
with tab_count:
    pivot_count = role_dept.pivot(index="JobRole", columns="Department", values="Left").fillna(0)
    fig = px.imshow(pivot_count, color_continuous_scale="Reds", text_auto=True, aspect="auto", labels=dict(color="Exits"))
    polish(fig, 430)
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df_filtered))

hotspot = role_dept[role_dept["Total"] >= 10].sort_values("Rate", ascending=False).head(1)
if not hotspot.empty:
    row = hotspot.iloc[0]
    st.markdown(
        f"""
        <div class="pan-panel">
            <h3>Hotspot Callout</h3>
            <p><strong>{row['JobRole']}</strong> in <strong>{row['Department']}</strong> has the highest eligible attrition rate at <strong>{row['Rate']:.1f}%</strong> across <strong>{int(row['Total'])}</strong> employees. Prioritize retention action here.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.subheader("Role Comparison: Volume vs Attrition Rate")
fig = px.scatter(
    role_dept,
    x="Total",
    y="Rate",
    size="Left",
    color="Department",
    hover_name="JobRole",
    text="JobRole",
    labels={"Total": "Total Employees", "Rate": "Attrition Rate (%)", "Left": "Employees Left"},
)
fig.update_traces(textposition="top center")
polish(fig, 480)
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df_filtered))

download_filtered_data(df_filtered, "department_role_filtered_data.csv")
