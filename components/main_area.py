from textwrap import dedent

import streamlit as st

from constants import CARDS_PER_ROW
from helpers import (
    build_remarks_text,
    component_status,
    export_excel_bytes,
    format_date,
    format_days,
    format_hours,
    format_number,
    kpi_summary,
    matches_search,
    room_colors,
    status_badge,
    system_sort_key,
    system_status,
)


def _render_kpi_box(label, value):
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_main_area(data):
    systems = data["systems"]

    search_col, building_col, location_col, status_col, sort_col, export_col = st.columns(
        [1.5, 1.0, 1.2, 1.0, 1.1, 0.9]
    )

    with search_col:
        search_text = st.text_input(
            "Search",
            value="",
            placeholder="Building, location, model, remarks...",
        )

    building_options = ["All"] + sorted(
        {system.get("building", "") for system in systems if system.get("building")}
    )
    with building_col:
        selected_building = st.selectbox("Building", building_options, index=0)

    if selected_building == "All":
        location_pool = systems
    else:
        location_pool = [system for system in systems if system.get("building") == selected_building]

    location_options = ["All"] + sorted(
        {system.get("location", "") for system in location_pool if system.get("location")}
    )
    with location_col:
        selected_location = st.selectbox("Location", location_options, index=0)

    status_options = ["All", "Normal", "Warning", "Out of service"]
    with status_col:
        selected_status = st.selectbox("Status", status_options, index=0)

    with sort_col:
        selected_sort = st.selectbox(
            "Sort by",
            ["Urgency", "Remaining days", "Start date", "Building", "Location"],
            index=0,
        )

    filtered_systems = []
    for system in systems:
        status = system_status(system)

        matches_building = selected_building == "All" or system.get("building") == selected_building
        matches_location = selected_location == "All" or system.get("location") == selected_location
        matches_status = selected_status == "All" or status == selected_status
        matches_text = matches_search(system, search_text)

        if matches_building and matches_location and matches_status and matches_text:
            filtered_systems.append(system)

    filtered_systems = sorted(filtered_systems, key=lambda x: system_sort_key(x, selected_sort))

    with export_col:
        excel_bytes = export_excel_bytes(data, filtered_systems)
        st.download_button(
            label="Export Excel",
            data=excel_bytes,
            file_name="UV Sterilizer System Monitoring.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    kpis = kpi_summary(filtered_systems)

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        _render_kpi_box("Systems", kpis["total_systems"])
    with k2:
        _render_kpi_box("Normal", kpis["normal_systems"])
    with k3:
        _render_kpi_box("Warning", kpis["warning_systems"])
    with k4:
        _render_kpi_box("Out of service", kpis["out_of_service_systems"])
    with k5:
        _render_kpi_box("Total lamps", kpis["total_lamps"])

    st.write("")

    rows = [filtered_systems[i:i + CARDS_PER_ROW] for i in range(0, len(filtered_systems), CARDS_PER_ROW)]

    for row in rows:
        cols = st.columns(CARDS_PER_ROW)

        for idx, system in enumerate(row):
            status = system_status(system)
            colors = room_colors(status)

            building = system.get("building") or "N/A"
            location = system.get("location") or "N/A"
            model = system.get("model") or "N/A"

            remaining_hours = system.get("remaining_hours")
            remaining_days = system.get("remaining_days")
            lamp_count = int(float(system.get("number_of_lamps") or 0))

            card_key = f'card_{system.get("system_id", idx)}'
            open_key = f'open_{system.get("system_id", idx)}'
            details_key = f'details_{system.get("system_id", idx)}'

            with cols[idx]:
                st.markdown(
                    dedent(
                        f"""
                        <style>
                            .st-key-{card_key} {{
                                background: {colors["background"]};
                                border: 1px solid {colors["border"]};
                                border-radius: 18px;
                                padding: 16px 14px 20px 16px;
                                height: 350px;
                                margin-bottom: 18px;
                                box-sizing: border-box;
                                display: flex;
                                flex-direction: column;
                                align-items: stretch;
                                justify-content: flex-start;
                                box-shadow:
                                    inset 6px 0 0 {colors["accent"]},
                                    0 8px 18px rgba(15, 23, 42, 0.06);
                                overflow: hidden;
                            }}

                            .st-key-{open_key} button {{
                                border: none !important;
                                background: transparent !important;
                                padding: 0 !important;
                                min-height: 0 !important;
                                box-shadow: none !important;
                                text-align: left !important;
                                font-size: 1.18rem !important;
                                font-weight: 900 !important;
                                color: {colors["title"]} !important;
                                opacity: 1 !important;
                                line-height: 1.12 !important;
                                white-space: normal !important;
                                word-break: break-word !important;
                            }}

                            .st-key-{open_key} button:hover {{
                                border: none !important;
                                background: transparent !important;
                                box-shadow: none !important;
                                color: {colors["title"]} !important;
                                opacity: 1 !important;
                                text-decoration: none !important;
                            }}

                            .st-key-{details_key} button {{
                                border: none !important;
                                background: transparent !important;
                                box-shadow: none !important;
                                padding: 0 !important;
                                min-height: 0 !important;
                                font-size: 0.92rem !important;
                                color: #64748b !important;
                            }}

                            .st-key-{details_key} button:hover {{
                                background: transparent !important;
                                color: #334155 !important;
                            }}

                            .st-key-{details_key} button svg {{
                                display: none !important;
                            }}
                        </style>
                        """
                    ),
                    unsafe_allow_html=True,
                )

                card = st.container(key=card_key)

                with card:
                    header_left, header_right = st.columns([6.0, 0.8])

                    with header_left:
                        if st.button(location, key=open_key):
                            st.session_state.selected_system_id = system.get("system_id")
                            st.rerun()

                    with header_right:
                        with st.popover("ⓘ", key=details_key, type="tertiary"):
                            d1, d2, d3, d4 = st.columns(4)

                            d1.markdown(
                                f'<div class="mini-box"><div class="mini-label">Building</div><div class="mini-value">{building}</div></div>',
                                unsafe_allow_html=True,
                            )
                            d2.markdown(
                                f'<div class="mini-box"><div class="mini-label">Location</div><div class="mini-value">{location}</div></div>',
                                unsafe_allow_html=True,
                            )
                            d3.markdown(
                                f'<div class="mini-box"><div class="mini-label">Model</div><div class="mini-value">{model}</div></div>',
                                unsafe_allow_html=True,
                            )
                            d4.markdown(
                                f'<div class="mini-box"><div class="mini-label">Power / Lamp</div><div class="mini-value">{system.get("power_rating_label") or "N/A"}</div></div>',
                                unsafe_allow_html=True,
                            )

                            st.write("")

                            d5, d6, d7, d8 = st.columns(4)
                            d5.markdown(
                                f'<div class="mini-box"><div class="mini-label">Actual Flow Rate</div><div class="mini-value">{format_number(system.get("actual_flow_rate"))} m³/h</div></div>',
                                unsafe_allow_html=True,
                            )
                            d6.markdown(
                                f'<div class="mini-box"><div class="mini-label">Current Dosing</div><div class="mini-value">{format_number(system.get("current_dosing"))} mJ/cm²</div></div>',
                                unsafe_allow_html=True,
                            )
                            d7.markdown(
                                f'<div class="mini-box"><div class="mini-label">Upgrade Dosing</div><div class="mini-value">{format_number(system.get("upgrade_dosing"))} mJ/cm²</div></div>',
                                unsafe_allow_html=True,
                            )
                            d8.markdown(
                                f'<div class="mini-box"><div class="mini-label">Connection Size</div><div class="mini-value">{format_number(system.get("connection_size_mm"))} mm</div></div>',
                                unsafe_allow_html=True,
                            )

                            st.write("")

                            d9, d10, d11, d12 = st.columns(4)
                            d9.markdown(
                                f'<div class="mini-box"><div class="mini-label">Number of Lamps</div><div class="mini-value">{lamp_count}</div></div>',
                                unsafe_allow_html=True,
                            )
                            d10.markdown(
                                f'<div class="mini-box"><div class="mini-label">Design Flow Rate</div><div class="mini-value">{format_number(system.get("design_flow_rate"))} m³/h</div></div>',
                                unsafe_allow_html=True,
                            )
                            d11.markdown(
                                f'<div class="mini-box"><div class="mini-label">Start Date</div><div class="mini-value">{format_date(system.get("start_date"))}</div></div>',
                                unsafe_allow_html=True,
                            )
                            d12.markdown(
                                f'<div class="mini-box"><div class="mini-label">End Date</div><div class="mini-value">{format_date(system.get("end_date"))}</div></div>',
                                unsafe_allow_html=True,
                            )

                            st.write("")

                            detail_html = (
                                f'<div class="item-box">'
                                f'<div class="item-name">{location}</div>'
                                f'<div style="margin-bottom:0.45rem;">{status_badge(status)}</div>'
                                f'<div><b>Building:</b> {building}</div>'
                                f'<div><b>Location:</b> {location}</div>'
                                f'<div><b>Remarks:</b> {build_remarks_text(system)}</div>'
                                f'</div>'
                            )
                            st.markdown(detail_html, unsafe_allow_html=True)

                            st.markdown('<div class="section-title">Components</div>', unsafe_allow_html=True)

                            components = system.get("components", [])
                            for comp_index in range(0, len(components), 2):
                                comp_row = components[comp_index:comp_index + 2]
                                comp_cols = st.columns(2)

                                for row_idx, component in enumerate(comp_row):
                                    with comp_cols[row_idx]:
                                        remark_line = ""
                                        if component.get("remark"):
                                            remark_line = f'<div><b>Remark:</b> {component.get("remark")}</div>'

                                        component_html = (
                                            f'<div class="item-box">'
                                            f'<div class="item-name">{component.get("component_name")}</div>'
                                            f'<div style="margin-bottom:0.45rem;">{status_badge(component_status(component))}</div>'
                                            f'<div><b>Lifetime:</b> {component.get("lifetime_label")}</div>'
                                            f'<div><b>Start:</b> {format_date(component.get("start_date"))}</div>'
                                            f'<div><b>End:</b> {format_date(component.get("end_date"))}</div>'
                                            f'<div><b>Remaining:</b> {format_days(component.get("remaining_days"))} • {format_hours(component.get("remaining_hours"))}</div>'
                                            f'<div><b>Replacement:</b> {component.get("replacement_note") or "Initial installation"}</div>'
                                            f'{remark_line}'
                                            f'</div>'
                                        )
                                        st.markdown(component_html, unsafe_allow_html=True)

                    sub_left, sub_right = st.columns([4.5, 2.3])

                    with sub_left:
                        st.markdown(
                            f'<div class="card-subtitle"><b>Building:</b> {building}</div>',
                            unsafe_allow_html=True,
                        )

                    with sub_right:
                        st.markdown(
                            f'<div style="display:flex; justify-content:flex-end; margin-top:0.05rem; margin-bottom:0.10rem;">{status_badge(status)}</div>',
                            unsafe_allow_html=True,
                        )

                    st.markdown(
                        f"""
                        <div class="counter-row">
                            <span class="counter-pill">{system.get("power_rating_label") or "N/A"}</span>
                            <span class="counter-pill">LAMPS {lamp_count}</span>
                            <span class="counter-pill">{format_number(system.get("actual_flow_rate"))} m³/h</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        f"""
                        <div class="card-details">
                            <div class="card-line"><b>Model:</b> {model}</div>
                            <div class="card-line"><b>Remaining:</b> {format_days(remaining_days)} • {format_hours(remaining_hours)}</div>
                            <div class="card-line"><b>Start:</b> {format_date(system.get("start_date"))}</div>
                            <div class="card-line"><b>End:</b> {format_date(system.get("end_date"))}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    if not filtered_systems:
        st.info("No systems match the current filters.")