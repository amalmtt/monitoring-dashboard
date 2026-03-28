import streamlit as st

from constants import INITIAL_LIFETIME_LABEL
from helpers import (
    build_remarks_text,
    component_status,
    format_date,
    format_days,
    format_hours,
    format_number,
    status_badge,
    system_status,
)


def _readonly_box(label, value):
    st.markdown(
        f"""
        <div class="readonly-box">
            <div class="readonly-label">{label}</div>
            <div class="readonly-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_editor_panel(selected_system):
    panel_status = system_status(selected_system)

    st.markdown(
        f'<div class="editor-title">System details</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="editor-subtitle">{selected_system.get("location") or "N/A"} • {panel_status}</div>',
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns([5, 1])

    with top_left:
        st.markdown(
            f'<div class="helper-text"><b>Remaining:</b> {format_days(selected_system.get("remaining_days"))} • {format_hours(selected_system.get("remaining_hours"))}</div>',
            unsafe_allow_html=True,
        )

    with top_right:
        if st.button("✕", key="close_editor_panel"):
            st.session_state.selected_system_id = None
            st.rerun()

    st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        _readonly_box("Building", selected_system.get("building") or "N/A")
    with r2:
        _readonly_box("Location", selected_system.get("location") or "N/A")

    r3, r4 = st.columns(2)
    with r3:
        _readonly_box("Model", selected_system.get("model") or "N/A")
    with r4:
        _readonly_box("Electrical Power kW/Lamp", selected_system.get("power_rating_label") or "N/A")

    st.markdown('<div class="section-title">System values</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        _readonly_box("Actual Flow Rate (m3/hr)", f'{format_number(selected_system.get("actual_flow_rate"))} m³/h')
        _readonly_box("CURRENT DOSING (mJ/cm2)", f'{format_number(selected_system.get("current_dosing"))} mJ/cm²')
        _readonly_box("UPGRADE DOSING (mJ/cm2)", f'{format_number(selected_system.get("upgrade_dosing"))} mJ/cm²')
        _readonly_box("Connection Size (mm)", f'{format_number(selected_system.get("connection_size_mm"))} mm')

    with c2:
        _readonly_box("NUMBER OF LAMPS", format_number(selected_system.get("number_of_lamps")))
        _readonly_box("DESIGN FLOW RATE M3/H", f'{format_number(selected_system.get("design_flow_rate"))} m³/h')
        _readonly_box("Start Date", format_date(selected_system.get("start_date")))
        _readonly_box("End Date", format_date(selected_system.get("end_date")))

    st.markdown('<div class="section-title">Remarks</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="remarks-box">{build_remarks_text(selected_system)}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Components</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="helper-text">Initial lifetime for lamp and ballast: <b>{INITIAL_LIFETIME_LABEL}</b></div>',
        unsafe_allow_html=True,
    )

    components = selected_system.get("components", [])
    for comp_index in range(0, len(components), 2):
        comp_row = components[comp_index:comp_index + 2]
        comp_cols = st.columns(2)

        for row_idx, component in enumerate(comp_row):
            with comp_cols[row_idx]:
                component_html = (
                    f'<div class="item-box">'
                    f'<div class="item-name">{component.get("component_name")}</div>'
                    f'<div style="margin-bottom:0.45rem;">{status_badge(component_status(component))}</div>'
                    f'<div><b>Lifetime:</b> {component.get("lifetime_label")}</div>'
                    f'<div><b>Start:</b> {format_date(component.get("start_date"))}</div>'
                    f'<div><b>End:</b> {format_date(component.get("end_date"))}</div>'
                    f'<div><b>Remaining:</b> {format_days(component.get("remaining_days"))} • {format_hours(component.get("remaining_hours"))}</div>'
                    f'<div><b>Replacement:</b> {component.get("replacement_note") or "Initial installation"}</div>'
                    f'</div>'
                )
                st.markdown(component_html, unsafe_allow_html=True)