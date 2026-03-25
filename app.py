import streamlit as st

from components.editor_panel import render_editor_panel
from components.main_area import render_main_area
from constants import PAGE_TITLE
from data_store import load_rooms
from helpers import find_room_by_id
from styles import render_global_styles


st.set_page_config(
    page_title=PAGE_TITLE,
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "selected_room_id" not in st.session_state:
    st.session_state.selected_room_id = None

if "selected_item_id" not in st.session_state:
    st.session_state.selected_item_id = None

rooms = load_rooms()
selected_room = find_room_by_id(rooms, st.session_state.selected_room_id)

render_global_styles()

st.title(PAGE_TITLE)

if selected_room:
    main_col, editor_col = st.columns([4.7, 2.0], gap="large")
else:
    main_col = st.container()
    editor_col = None

with main_col:
    render_main_area(rooms)

if selected_room and editor_col is not None:
    with editor_col:
        render_editor_panel(selected_room)