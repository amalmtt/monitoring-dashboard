import streamlit as st

from components.editor_panel import render_editor_panel
from components.main_area import render_main_area
from constants import HEADER_LOGO_FILE, PAGE_TITLE
from data_store import load_monitoring_data
from helpers import find_system_by_id
from styles import render_global_styles


st.set_page_config(
    page_title=PAGE_TITLE,
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "selected_system_id" not in st.session_state:
    st.session_state.selected_system_id = None

render_global_styles()

data = load_monitoring_data()
selected_system = find_system_by_id(data["systems"], st.session_state.selected_system_id)

header_left, header_right = st.columns([5, 2], gap="large")

with header_left:
    st.markdown(f'<div class="page-title">{PAGE_TITLE}</div>', unsafe_allow_html=True)

with header_right:
    if HEADER_LOGO_FILE.exists():
        st.image(str(HEADER_LOGO_FILE), width=320)

if selected_system:
    main_col, editor_col = st.columns([4.9, 2.1], gap="large")
else:
    main_col = st.container()
    editor_col = None

with main_col:
    render_main_area(data)

if selected_system and editor_col is not None:
    with editor_col:
        render_editor_panel(selected_system)