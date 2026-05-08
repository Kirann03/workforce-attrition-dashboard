import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.charts import DEEP_NAVY, EXIT_SCALE, RATE_SCALE, STATUS_COLORS, polish, sankey
from utils.config import ATTRITION_HIGH_THRESHOLD
from utils.data_loader import load_data
from utils.kpis import attrition_rate
from utils.theme import apply_theme, chart_caption, data_quality_banner, download_filtered_data, page_header, render_global_filters, render_sidebar, risk_badge, section_divider


st.set_page_config(page_title="Department & Role Analysis", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")
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

dept_rates_all = attrition_rate(df, "Department").sort_values("Rate", ascending=False)
role_rates_all = attrition_rate(df, "JobRole").sort_values("Rate", ascending=False)
baseline_all = df["Attrition"].mean() * 100

alerts = []
for _, row in dept_rates_all.iterrows():
    if row["Rate"] / 100 > ATTRITION_HIGH_THRESHOLD:
        alerts.append(
            f"**{row['Department']}** department exceeds the 30% high-risk threshold "
            f"at **{row['Rate']:.1f}%** attrition."
        )
for _, row in role_rates_all.iterrows():
    if row["Rate"] / 100 > ATTRITION_HIGH_THRESHOLD:
        alerts.append(
            f"**{row['JobRole']}** role exceeds the 30% high-risk threshold "
            f"at **{row['Rate']:.1f}%** attrition."
        )

st.markdown("#### Critical Risk Alerts")
if alerts:
    for alert in alerts[:5]:
        st.warning(alert)
else:
    st.success("No department or role exceeds the 30% high-risk attrition threshold.")

st.markdown("#### Organisation-Wide Department Summary")
top_role_by_dept = (
    df.groupby(["Department", "JobRole"], observed=False)
    .agg(Total=("Attrition", "count"), Left=("Attrition", "sum"))
    .reset_index()
)
top_role_by_dept["Rate"] = (top_role_by_dept["Left"] / top_role_by_dept["Total"] * 100).fillna(0)
top_role_by_dept = top_role_by_dept.sort_values(["Department", "Rate"], ascending=[True, False])
top_role_by_dept = top_role_by_dept.drop_duplicates("Department").set_index("Department")["JobRole"]

summary_table = dept_rates_all.rename(columns={"Rate": "Attrition %", "Total": "Total Employees"}).copy()
summary_table["Risk Level"] = summary_table["Attrition %"].apply(lambda rate: risk_badge(rate, baseline_all))
summary_table["Top Exit Role"] = summary_table["Department"].map(top_role_by_dept)
summary_table = summary_table[["Department", "Total Employees", "Attrition %", "Risk Level", "Top Exit Role"]]
st.write(summary_table.to_html(escape=False, index=False), unsafe_allow_html=True)
st.markdown('<div style="margin-bottom:1.5rem"></div>', unsafe_allow_html=True)

df_filtered = render_global_filters(df)

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
    fig.add_trace(go.Bar(x=dept_rate["Rate"], y=dept_rate["Department"], orientation="h", text=dept_rate["Rate"], marker_color=DEEP_NAVY))
    fig.add_vline(x=baseline, line_dash="dash", line_color=DEEP_NAVY, annotation_text=f"Baseline {baseline:.1f}%")
    fig.add_vline(x=13, line_dash="dot", line_color="#8A6F52", annotation_text="Industry 13.0%")
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    polish(fig, 380)
    fig.update_layout(xaxis_title="Attrition Rate (%)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df_filtered))

section_divider("Heatmaps")
st.subheader("Job Role Attrition Heatmaps")
role_dept = df_filtered.groupby(["JobRole", "Department"], observed=False).agg(
    Total=("Attrition", "count"),
    Left=("Attrition", "sum"),
).reset_index()
role_dept["Rate"] = (role_dept["Left"] / role_dept["Total"] * 100).fillna(0).round(1)

tab_rate, tab_count = st.tabs(["Attrition Rate", "Exit Count"])
with tab_rate:
    pivot = role_dept.pivot(index="JobRole", columns="Department", values="Rate").fillna(0)
    fig = px.imshow(pivot, color_continuous_scale=RATE_SCALE, text_auto=True, aspect="auto", labels=dict(color="Attrition %"))
    polish(fig, 430)
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df_filtered))
with tab_count:
    pivot_count = role_dept.pivot(index="JobRole", columns="Department", values="Left").fillna(0)
    fig = px.imshow(pivot_count, color_continuous_scale=EXIT_SCALE, text_auto=True, aspect="auto", labels=dict(color="Exits"))
    polish(fig, 430)
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df_filtered))

st.subheader("Department and Role Risk Treemap")
fig = px.treemap(
    role_dept,
    path=["Department", "JobRole"],
    values="Total",
    color="Rate",
    color_continuous_scale=RATE_SCALE,
    hover_data={"Left": True, "Rate": ":.1f"},
)
polish(fig, 430, title="Exit Volume and Attrition Rate by Department and Role")
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df_filtered))

section_divider("Exit Flow")
st.subheader("Department to Role to Outcome Flow")
status_flow = df_filtered.groupby(["Department", "JobRole", "Attrition_Label"], observed=False).size().reset_index(name="Count")
status_flow = status_flow[status_flow["Count"] > 0]
dept_nodes = status_flow["Department"].drop_duplicates().tolist()
role_nodes = status_flow["JobRole"].drop_duplicates().tolist()
status_nodes = ["Left", "Stayed"]
labels = dept_nodes + role_nodes + status_nodes
node_map = {name: idx for idx, name in enumerate(labels)}
dept_role = status_flow.groupby(["Department", "JobRole"], observed=False)["Count"].sum().reset_index()
sources = dept_role["Department"].map(node_map).tolist()
targets = dept_role["JobRole"].map(node_map).tolist()
values = dept_role["Count"].tolist()
sources += status_flow["JobRole"].map(node_map).tolist()
targets += status_flow["Attrition_Label"].map(node_map).tolist()
values += status_flow["Count"].tolist()
fig = sankey(labels, sources, targets, values, title="Department to Role to Outcome Flow")
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

section_divider("Role Comparison")
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
polish(fig, 480, title="Role Comparison: Volume vs Attrition Rate")
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df_filtered))

download_filtered_data(df_filtered, "department_role_filtered_data.csv")
