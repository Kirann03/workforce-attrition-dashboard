import streamlit as st

from utils.theme import apply_theme, render_sidebar


st.set_page_config(
    page_title="PAN Workforce Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_sidebar()

st.switch_page("pages/01_Overview.py")
