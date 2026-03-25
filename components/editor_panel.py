from textwrap import dedent

import streamlit as st

from data_store import load_rooms, save_rooms
from helpers import (
    calculate_remaining_hours,
    calculate_used_hours,
    find_room_index_by_id,
    format_hours,
    get_room_last_updated,
    get_room_remaining_hours,
    get_room_state,
    get_room_used_hours,
    iter_room_items,
    normalize_manual_status,
    now_string,
    short_date,
    update_item_in_rooms,
)


def render_editor_panel(selected_room):
    st.markdown(
        dedent(
            """
            <style>
                .st-key-editor_panel {
                    border: 1px solid #dbe4ee;
                    border-radius: 18px;
                    padding: 16px;
                    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
                    position: sticky;
                    top: 1rem;
                    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
                }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )

    editor_panel = st.container(key="editor_panel")

    with editor_panel:
        room_state = get_room_state(selected_room)
        room_used = format_hours(get_room_used_hours(selected_room))
        room_remaining = format_hours(get_room_remaining_hours(selected_room))
        room_last_updated = get_room_last_updated(selected_room)
        room_last_updated_short = short_date(room_last_updated)

        top_left, top_right = st.columns([5, 1])

        with top_left:
            st.markdown(f'<div class="editor-title">Edit {selected_room["room_name"]}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="editor-subtitle">{selected_room["room_id"]} • {room_state}</div>',
                unsafe_allow_html=True,
            )

        with top_right:
            if st.button("✕", key="close_editor"):
                st.session_state.selected_room_id = None
                st.session_state.selected_item_id = None
                st.rerun()

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.markdown(
                f'<div class="mini-box"><div class="mini-label">Type</div><div class="mini-value">{selected_room.get("room_type", "")}</div></div>',
                unsafe_allow_html=True,
            )
        with row1_col2:
            st.markdown(
                f'<div class="mini-box"><div class="mini-label">Used</div><div class="mini-value">{room_used}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.markdown(
                f'<div class="mini-box"><div class="mini-label">Remaining</div><div class="mini-value">{room_remaining}</div></div>',
                unsafe_allow_html=True,
            )
        with row2_col2:
            st.markdown(
                f'<div class="mini-box"><div class="mini-label">Last updated</div><div class="mini-value">{room_last_updated_short}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-title">Room</div>', unsafe_allow_html=True)

        manual_options = ["Auto", "OK", "Warning", "Critical"]
        current_manual = normalize_manual_status(selected_room.get("manual_status", ""))
        current_manual_label = "Auto" if current_manual == "" else current_manual

        with st.form("edit_room_form"):
            edit_room_manual_status = st.selectbox(
                "Room status mode",
                manual_options,
                index=manual_options.index(current_manual_label),
            )
            edit_room_technician = st.text_input(
                "Room technician",
                value=selected_room.get("technician", ""),
            )
            save_room_button = st.form_submit_button("Save room")

        if save_room_button:
            fresh_rooms = load_rooms()
            room_idx = find_room_index_by_id(fresh_rooms, selected_room["room_id"])

            if room_idx is not None:
                fresh_rooms[room_idx]["manual_status"] = "" if edit_room_manual_status == "Auto" else edit_room_manual_status
                fresh_rooms[room_idx]["technician"] = edit_room_technician
                fresh_rooms[room_idx]["last_updated"] = now_string()
                save_rooms(fresh_rooms)
                st.success("Room updated.")
                st.rerun()

        st.markdown('<div class="section-title">Item</div>', unsafe_allow_html=True)

        room_items = list(iter_room_items(selected_room))
        if room_items:
            item_labels = {item["label"]: item["item_id"] for item in room_items}
            label_list = list(item_labels.keys())
            id_list = list(item_labels.values())

            if st.session_state.selected_item_id is None and room_items:
                st.session_state.selected_item_id = room_items[0]["item_id"]

            current_index = 0
            if st.session_state.selected_item_id in id_list:
                current_index = id_list.index(st.session_state.selected_item_id)

            selected_item_label = st.selectbox("Tracked item", label_list, index=current_index)
            st.session_state.selected_item_id = item_labels[selected_item_label]

            selected_item = next(
                (item for item in room_items if str(item["item_id"]) == str(st.session_state.selected_item_id)),
                None,
            )

            if selected_item:
                item_used_num = calculate_used_hours(selected_item["start_date"])
                item_remaining_num = calculate_remaining_hours(selected_item["start_date"], selected_item["lifetime_hours"])
                item_used = format_hours(item_used_num)
                item_remaining = format_hours(item_remaining_num)
                item_last_updated_short = short_date(selected_item["last_updated"])

                st.markdown(
                    '<div class="helper-text">Start date resets only when the item status changes to OK.</div>',
                    unsafe_allow_html=True,
                )

                mrow1_col1, mrow1_col2 = st.columns(2)
                with mrow1_col1:
                    st.markdown(
                        f'<div class="mini-box"><div class="mini-label">Status</div><div class="mini-value">{selected_item["status"]}</div></div>',
                        unsafe_allow_html=True,
                    )
                with mrow1_col2:
                    st.markdown(
                        f'<div class="mini-box"><div class="mini-label">Used</div><div class="mini-value">{item_used}</div></div>',
                        unsafe_allow_html=True,
                    )

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                mrow2_col1, mrow2_col2 = st.columns(2)
                with mrow2_col1:
                    st.markdown(
                        f'<div class="mini-box"><div class="mini-label">Remaining</div><div class="mini-value">{item_remaining}</div></div>',
                        unsafe_allow_html=True,
                    )
                with mrow2_col2:
                    st.markdown(
                        f'<div class="mini-box"><div class="mini-label">Last updated</div><div class="mini-value">{item_last_updated_short}</div></div>',
                        unsafe_allow_html=True,
                    )

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                reset_cols = st.columns([1, 1])

                with reset_cols[0]:
                    if st.button("Reset timer (set OK)", use_container_width=True):
                        fresh_rooms = load_rooms()
                        current_time = now_string()
                        room_idx = find_room_index_by_id(fresh_rooms, selected_room["room_id"])

                        if room_idx is not None:
                            update_data = {
                                "status": "OK",
                                "start_date": current_time,
                                "last_updated": current_time,
                            }
                            updated = update_item_in_rooms(
                                fresh_rooms,
                                selected_room["room_id"],
                                selected_item["item_id"],
                                update_data,
                            )
                            if updated:
                                fresh_rooms[room_idx]["last_updated"] = current_time
                                save_rooms(fresh_rooms)
                                st.success("Timer reset.")
                                st.rerun()

                with st.form("edit_item_form"):
                    edit_item_status = st.selectbox(
                        "Item status",
                        ["OK", "Warning", "Critical"],
                        index=["OK", "Warning", "Critical"].index(selected_item["status"]),
                    )
                    edit_item_lifetime = st.number_input(
                        "Lifetime hours",
                        min_value=1.0,
                        value=float(selected_item["lifetime_hours"]),
                        step=1.0,
                    )
                    edit_item_technician = st.text_input(
                        "Item technician",
                        value=selected_item["technician"],
                    )
                    edit_item_notes = st.text_area(
                        "Notes",
                        value=selected_item["notes"],
                        height=90,
                    )
                    save_item_button = st.form_submit_button("Save item")

                if save_item_button:
                    fresh_rooms = load_rooms()
                    current_time = now_string()

                    room_idx = find_room_index_by_id(fresh_rooms, selected_room["room_id"])

                    if room_idx is not None:
                        old_item = next(
                            (
                                item for item in iter_room_items(fresh_rooms[room_idx])
                                if str(item["item_id"]) == str(selected_item["item_id"])
                            ),
                            None,
                        )
                        old_status = old_item["status"] if old_item else "OK"

                        update_data = {
                            "status": edit_item_status,
                            "lifetime_hours": edit_item_lifetime,
                            "technician": edit_item_technician,
                            "notes": edit_item_notes,
                            "last_updated": current_time,
                        }

                        if edit_item_status == "OK" and old_status != "OK":
                            update_data["start_date"] = current_time

                        updated = update_item_in_rooms(
                            fresh_rooms,
                            selected_room["room_id"],
                            selected_item["item_id"],
                            update_data,
                        )

                        if updated:
                            fresh_rooms[room_idx]["last_updated"] = current_time
                            save_rooms(fresh_rooms)
                            st.success("Item updated.")
                            st.rerun()
        else:
            st.info("No tracked items in this room.")