from textwrap import dedent

import streamlit as st

from constants import ROOM_TYPE_MAP, ROOM_TYPE_SUMMARY
from helpers import (
    calculate_remaining_hours,
    calculate_used_hours,
    category_summary,
    export_csv_bytes,
    format_hours,
    get_room_item_count,
    get_room_last_updated,
    get_room_overdue_count,
    get_room_remaining_hours,
    get_room_start_date,
    get_room_state,
    get_room_status_counts,
    get_room_used_hours,
    iter_room_items,
    overdue_badge,
    room_colors,
    room_sort_key,
    short_date,
    status_badge,
)


def render_main_area(rooms):
    search_col, type_col, status_col, tech_col, sort_col = st.columns([1.8, 1.1, 1.0, 1.2, 1.1])

    with search_col:
        search_text = st.text_input("Search", value="", placeholder="Room, technician, id...")

    selected_group_label = st.radio(
        "Room group",
        options=list(ROOM_TYPE_MAP.keys()),
        horizontal=True,
        label_visibility="collapsed",
    )

    with type_col:
        selected_state = st.selectbox("Status", ["All", "OK", "Warning", "Critical"], index=0)

    technician_options = ["All"] + sorted({room.get("technician", "N/A") for room in rooms})
    with status_col:
        selected_technician = st.selectbox("Technician", technician_options, index=0)

    with tech_col:
        selected_sort = st.selectbox(
            "Sort by",
            ["Urgency", "Remaining time", "Last updated", "Room name"],
            index=0,
        )

    with sort_col:
        csv_bytes = export_csv_bytes(rooms)
        st.download_button(
            label="Export CSV",
            data=csv_bytes,
            file_name="uv_dashboard_export.csv",
            mime="text/csv",
            use_container_width=True,
        )

    selected_group_value = ROOM_TYPE_MAP[selected_group_label]

    filtered_rooms = []
    for room in rooms:
        room_state = get_room_state(room)
        room_name = str(room.get("room_name", ""))
        technician = str(room.get("technician", "N/A"))
        room_type = str(room.get("room_type", ""))

        matches_search = (
            not search_text
            or search_text.lower() in room_name.lower()
            or search_text.lower() in technician.lower()
            or search_text.lower() in str(room.get("room_id", "")).lower()
        )
        matches_type = selected_group_value == "All" or room_type == selected_group_value
        matches_state = selected_state == "All" or room_state == selected_state
        matches_technician = selected_technician == "All" or technician == selected_technician

        if matches_search and matches_type and matches_state and matches_technician:
            filtered_rooms.append(room)

    filtered_rooms = sorted(filtered_rooms, key=lambda r: room_sort_key(r, selected_sort))

    total_rooms = len(filtered_rooms)
    total_items = sum(get_room_item_count(room) for room in filtered_rooms)
    warning_rooms = sum(1 for room in filtered_rooms if get_room_state(room) == "Warning")
    critical_rooms = sum(1 for room in filtered_rooms if get_room_state(room) == "Critical")
    overdue_items = sum(get_room_overdue_count(room) for room in filtered_rooms)

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.markdown(
            f'<div class="mini-box"><div class="mini-label">Rooms</div><div class="mini-value">{total_rooms}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="mini-box"><div class="mini-label">Tracked items</div><div class="mini-value">{total_items}</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="mini-box"><div class="mini-label">Warning rooms</div><div class="mini-value">{warning_rooms}</div></div>',
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f'<div class="mini-box"><div class="mini-label">Critical rooms</div><div class="mini-value">{critical_rooms}</div></div>',
            unsafe_allow_html=True,
        )
    with m5:
        st.markdown(
            f'<div class="mini-box"><div class="mini-label">Overdue items</div><div class="mini-value">{overdue_items}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")

    summary_columns = st.columns(4)
    for col, (label, key) in zip(summary_columns, ROOM_TYPE_SUMMARY):
        total, critical, warning, overdue = category_summary(filtered_rooms, key)
        with col:
            box_html = (
                f'<div class="category-box">'
                f'<div class="category-title">{label}</div>'
                f'<div class="category-line">{total} rooms</div>'
                f'<div class="category-line">{critical} critical • {warning} warning</div>'
                f'<div class="category-line">{overdue} overdue items</div>'
                f'</div>'
            )
            st.markdown(box_html, unsafe_allow_html=True)

    st.write("")

    cards_per_row = 5
    rows = [filtered_rooms[i:i + cards_per_row] for i in range(0, len(filtered_rooms), cards_per_row)]

    for row in rows:
        cols = st.columns(cards_per_row)

        for i, room in enumerate(row):
            room_state = get_room_state(room)
            colors = room_colors(room_state)
            room_used_num = get_room_used_hours(room)
            room_remaining_num = get_room_remaining_hours(room)
            room_used = format_hours(room_used_num)
            room_remaining = format_hours(room_remaining_num)
            room_last_updated = get_room_last_updated(room)
            room_last_updated_short = short_date(room_last_updated)
            ok_count, warning_count, critical_count = get_room_status_counts(room)

            card_key = f"card_{room['room_id']}".replace("-", "_")
            open_key = f"open_{room['room_id']}".replace("-", "_")
            details_key = f"details_{room['room_id']}".replace("-", "_")

            with cols[i]:
                st.markdown(
                    dedent(
                        f"""
                        <style>
                            .st-key-{card_key} {{
                                background: {colors["background"]};
                                border: 1px solid {colors["border"]};
                                border-radius: 18px;
                                padding: 16px 14px 22px 16px;
                                height: 350px;
                                margin-bottom: 14px;
                                box-sizing: border-box;
                                display: flex;
                                flex-direction: column;
                                align-items: flex-start;
                                justify-content: flex-start;
                                gap: 0.14rem;
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
                                font-size: 1.02rem !important;
                                font-weight: 700 !important;
                                color: {colors["title"]} !important;
                                opacity: 1 !important;
                            }}

                            .st-key-{open_key} button:hover {{
                                border: none !important;
                                background: transparent !important;
                                box-shadow: none !important;
                                text-align: left !important;
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
                    title_col, info_col = st.columns([5, 1])

                    with title_col:
                        if st.button(room["room_name"], key=open_key):
                            st.session_state.selected_room_id = room["room_id"]
                            items = list(iter_room_items(room))
                            st.session_state.selected_item_id = items[0]["item_id"] if items else None
                            st.rerun()

                    with info_col:
                        with st.popover("ⓘ", key=details_key, type="tertiary"):
                            st.markdown(status_badge(room_state), unsafe_allow_html=True)

                            p1, p2, p3, p4, p5, p6 = st.columns(6)

                            p1.markdown(
                                f'<div class="mini-box"><div class="mini-label">Type</div><div class="mini-value">{room.get("room_type", "")}</div></div>',
                                unsafe_allow_html=True,
                            )
                            p2.markdown(
                                f'<div class="mini-box"><div class="mini-label">Technician</div><div class="mini-value">{room.get("technician", "N/A")}</div></div>',
                                unsafe_allow_html=True,
                            )
                            p3.markdown(
                                f'<div class="mini-box"><div class="mini-label">Start date</div><div class="mini-value">{get_room_start_date(room)}</div></div>',
                                unsafe_allow_html=True,
                            )
                            p4.markdown(
                                f'<div class="mini-box"><div class="mini-label">Used</div><div class="mini-value">{room_used}</div></div>',
                                unsafe_allow_html=True,
                            )
                            p5.markdown(
                                f'<div class="mini-box"><div class="mini-label">Remaining</div><div class="mini-value">{room_remaining}</div></div>',
                                unsafe_allow_html=True,
                            )
                            p6.markdown(
                                f'<div class="mini-box"><div class="mini-label">Last updated</div><div class="mini-value">{room_last_updated}</div></div>',
                                unsafe_allow_html=True,
                            )

                            st.write("")

                            grouped = {}
                            for item in iter_room_items(room):
                                group = item["group_name"]
                                grouped.setdefault(group, []).append(item)

                            for group_name, items in grouped.items():
                                st.markdown(f'<div class="group-title">{group_name}</div>', unsafe_allow_html=True)
                                for item in items:
                                    used = format_hours(calculate_used_hours(item["start_date"]))
                                    remaining_num = calculate_remaining_hours(item["start_date"], item["lifetime_hours"])
                                    remaining = format_hours(remaining_num)

                                    item_html = (
                                        f'<div class="item-box">'
                                        f'<div class="item-name">{item["short_name"]}</div>'
                                        f'<div style="margin-bottom: 0.45rem;">{status_badge(item["status"])}</div>'
                                        f'{overdue_badge(remaining_num)}'
                                        f'<div><b>Start date:</b> {item["start_date"]}</div>'
                                        f'<div><b>Used:</b> {used}</div>'
                                        f'<div><b>Remaining:</b> {remaining}</div>'
                                        f'<div><b>Technician:</b> {item["technician"]}</div>'
                                        f'<div><b>Last updated:</b> {item["last_updated"]}</div>'
                                        f'<div><b>Notes:</b> {item["notes"]}</div>'
                                        f'</div>'
                                    )
                                    st.markdown(item_html, unsafe_allow_html=True)

                    counts_html = (
                        f'<div class="counter-row">'
                        f'<span class="counter-pill">OK {ok_count}</span>'
                        f'<span class="counter-pill">WARN {warning_count}</span>'
                        f'<span class="counter-pill">CRIT {critical_count}</span>'
                        f'</div>'
                    )

                    details_html = (
                        f'<div class="card-details">'
                        f'<div>{colors["badge"]} {overdue_badge(room_remaining_num)}</div>'
                        f'{counts_html}'
                        f'<div class="card-line"><b>Type:</b> {room.get("room_type", "")}</div>'
                        f'<div class="card-line"><b>Technician:</b> {room.get("technician", "N/A")}</div>'
                        f'<div class="card-line"><b>Used:</b> {room_used}</div>'
                        f'<div class="card-line"><b>Remaining:</b> {room_remaining}</div>'
                        f'<div class="card-line"><b>Last updated:</b> {room_last_updated_short}</div>'
                        f'</div>'
                    )
                    st.markdown(details_html, unsafe_allow_html=True)

    if not filtered_rooms:
        st.info("No rooms match the current filters.")