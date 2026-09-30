"""
ui/pages/attendance_page.py
-----------------------------
Streamlit UI for Attendance Tracking.

Tabs:
  1. Mark Attendance  – select a date, mark status for each employee
  2. View by Date     – see who is present/absent on any given day
  3. Monthly Summary  – attendance % per employee for a chosen month
  4. Employee History – last 90 days attendance for one employee
"""

import streamlit as st
import pandas as pd
from datetime import date

from modules.attendance import (
    mark_attendance,
    get_attendance_by_date,
    get_monthly_summary,
    get_employee_attendance_history,
    bulk_mark_attendance,
)
from modules.employee import get_all_employees
from utils.formatters import status_badge, attendance_pct_color, month_name

ATTENDANCE_STATUSES = ["Present", "Absent", "Half-Day", "WFH", "Holiday"]


def render():
    """Render the Attendance Tracking page."""
    st.markdown("## 📅 Attendance Tracking")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "✏️ Mark Attendance",
        "👁️ View by Date",
        "📊 Monthly Summary",
        "📜 Employee History",
    ])

    with tab1:
        _render_mark()
    with tab2:
        _render_view_by_date()
    with tab3:
        _render_monthly_summary()
    with tab4:
        _render_emp_history()


# ---------------------------------------------------------------------------
# Tab 1 — Mark Attendance
# ---------------------------------------------------------------------------

def _render_mark():
    """Allow HR to mark attendance for multiple employees on a date."""
    st.markdown("### Mark Daily Attendance")

    col1, col2 = st.columns([2, 2])
    with col1:
        att_date = st.date_input("Date", value=date.today(), key="mark_att_date")
    with col2:
        bulk_status = st.selectbox(
            "Bulk set all to", ["— individual —"] + ATTENDANCE_STATUSES, key="bulk_status"
        )

    emp_df = get_all_employees()
    active_emp = emp_df[emp_df["status"].isin(["Active", "Inactive"])] if not emp_df.empty else pd.DataFrame()

    if active_emp.empty:
        st.info("No active employees found.")
        return

    # Existing attendance for this date
    existing_df = get_attendance_by_date(att_date)
    existing_map: dict = {}
    if not existing_df.empty:
        for _, r in existing_df.iterrows():
            existing_map[int(r["employee_id"])] = r["status"]

    if bulk_status != "— individual —":
        if st.button(f"Apply '{bulk_status}' to all employees", type="secondary"):
            emp_ids = active_emp["employee_id"].tolist()
            ok_cnt, fail_cnt = bulk_mark_attendance(emp_ids, att_date, bulk_status)
            st.success(f"✅ Marked {ok_cnt} employees as {bulk_status}. ({fail_cnt} failed)")
            st.rerun()

    st.markdown("---")
    st.markdown("**Individual Marking** — set and save row by row:")

    # Show 20 employees at a time with pagination
    PAGE_SIZE = 20
    page = st.number_input("Page", min_value=1,
                           max_value=max(1, (len(active_emp) - 1) // PAGE_SIZE + 1),
                           value=1, key="att_page")
    start_idx = (page - 1) * PAGE_SIZE
    page_emp  = active_emp.iloc[start_idx: start_idx + PAGE_SIZE]

    for _, emp_row in page_emp.iterrows():
        emp_id  = int(emp_row["employee_id"])
        current = existing_map.get(emp_id, "Present")
        idx     = ATTENDANCE_STATUSES.index(current) if current in ATTENDANCE_STATUSES else 0

        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            st.write(f"**{emp_row['emp_code']}** — {emp_row['full_name']}")
            st.caption(emp_row.get("department_name", ""))
        with c2:
            new_status = st.selectbox(
                f"Status for {emp_id}", ATTENDANCE_STATUSES, index=idx,
                key=f"att_status_{emp_id}",
                label_visibility="collapsed",
            )
        with c3:
            if st.button("Save", key=f"att_save_{emp_id}"):
                ok, msg = mark_attendance(emp_id, att_date, new_status)
                if ok:
                    st.success("Saved ✓")
                    existing_map[emp_id] = new_status
                else:
                    st.error(msg)


# ---------------------------------------------------------------------------
# Tab 2 — View by Date
# ---------------------------------------------------------------------------

def _render_view_by_date():
    """Display attendance records for a selected date."""
    st.markdown("### Attendance for a Specific Date")
    view_date = st.date_input("Select Date", value=date.today(), key="view_att_date")

    df = get_attendance_by_date(view_date)
    if df.empty:
        st.info(f"No attendance records found for {view_date.strftime('%d %b %Y')}.")
        return

    # Summary metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    status_counts = df["status"].value_counts()
    with c1: st.metric("Present",  status_counts.get("Present",  0))
    with c2: st.metric("WFH",      status_counts.get("WFH",      0))
    with c3: st.metric("Absent",   status_counts.get("Absent",   0))
    with c4: st.metric("Half-Day", status_counts.get("Half-Day", 0))
    with c5: st.metric("Holiday",  status_counts.get("Holiday",  0))

    st.markdown("---")

    # Table with colored status
    show_cols = ["emp_code", "full_name", "department_name", "status", "check_in", "check_out", "remarks"]
    show_cols = [c for c in show_cols if c in df.columns]
    rename    = {
        "emp_code": "Code", "full_name": "Name", "department_name": "Department",
        "status": "Status", "check_in": "Check In", "check_out": "Check Out", "remarks": "Remarks",
    }
    st.dataframe(df[show_cols].rename(columns=rename), use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Tab 3 — Monthly Summary
# ---------------------------------------------------------------------------

def _render_monthly_summary():
    """Show attendance percentage for all employees in a selected month."""
    st.markdown("### Monthly Attendance Summary")
    col1, col2 = st.columns(2)
    with col1:
        sel_month = st.selectbox(
            "Month", list(range(1, 13)),
            format_func=month_name, index=date.today().month - 1, key="sum_month"
        )
    with col2:
        sel_year = st.number_input("Year", min_value=2020, max_value=2030,
                                   value=date.today().year, key="sum_year")

    df = get_monthly_summary(sel_month, int(sel_year))
    if df.empty:
        st.info(f"No attendance data for {month_name(sel_month)} {sel_year}.")
        return

    st.metric("Company-wide avg attendance",
              f"{df['attendance_pct'].mean():.1f}%" if "attendance_pct" in df.columns else "—")

    # Color-code attendance_pct column
    show_cols = ["emp_code", "full_name", "department_name", "present_days",
                 "absent_days", "wfh_days", "half_days", "total_records", "attendance_pct"]
    show_cols = [c for c in show_cols if c in df.columns]
    rename = {
        "emp_code": "Code", "full_name": "Name", "department_name": "Department",
        "present_days": "Present", "absent_days": "Absent", "wfh_days": "WFH",
        "half_days": "Half-Day", "total_records": "Total Days", "attendance_pct": "Att %",
    }
    show_df = df[show_cols].rename(columns=rename).copy()
    if "Att %" in show_df.columns:
        show_df["Att %"] = show_df["Att %"].apply(
            lambda x: f"{float(x):.1f}%" if pd.notna(x) else "—"
        )

    st.dataframe(show_df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Tab 4 — Employee History
# ---------------------------------------------------------------------------

def _render_emp_history():
    """Show last 90 days of attendance for a selected employee."""
    st.markdown("### Employee Attendance History (Last 90 Days)")

    emp_df = get_all_employees()
    if emp_df.empty:
        st.info("No employees found.")
        return

    emp_labels = {
        f"{r['emp_code']} — {r['full_name']}": int(r["employee_id"])
        for _, r in emp_df.iterrows()
    }
    selected = st.selectbox("Select Employee", list(emp_labels.keys()), key="hist_emp")
    emp_id   = emp_labels[selected]

    df = get_employee_attendance_history(emp_id)
    if df.empty:
        st.info("No attendance records found for this employee.")
        return

    # Summary
    if "status" in df.columns:
        sc = df["status"].value_counts()
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Present",  sc.get("Present",  0))
        with c2: st.metric("WFH",      sc.get("WFH",      0))
        with c3: st.metric("Absent",   sc.get("Absent",   0))
        with c4: st.metric("Half-Day", sc.get("Half-Day", 0))

    st.markdown("---")
    rename = {
        "attendance_date": "Date", "status": "Status",
        "check_in": "Check In", "check_out": "Check Out", "remarks": "Remarks",
    }
    show_df = df.rename(columns=rename).copy()
    if "Date" in show_df.columns:
        show_df["Date"] = pd.to_datetime(show_df["Date"]).dt.strftime("%d %b %Y")

    st.dataframe(show_df, use_container_width=True, hide_index=True)
