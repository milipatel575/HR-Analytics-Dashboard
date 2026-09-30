"""
ui/pages/leave_page.py
-----------------------
Streamlit UI for Leave Management.

Tabs:
  1. Apply for Leave      – employee submits leave request
  2. Pending Approvals    – HR approves or rejects pending leaves
  3. Leave History        – view all leave applications
  4. Leave Balances       – view an employee's remaining balance
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta

from modules.leave import (
    get_leave_types,
    get_leave_balance,
    apply_leave,
    get_all_leaves,
    get_pending_leaves,
    get_employee_leaves,
    update_leave_status,
    cancel_leave,
)
from modules.employee import get_all_employees
from utils.validators import validate_leave_days
from utils.formatters import format_date, status_badge, month_name


def render():
    """Render the Leave Management page."""
    st.markdown("## 🗓️ Leave Management")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📨 Apply for Leave",
        "✅ Pending Approvals",
        "📋 Leave History",
        "💰 Leave Balances",
    ])

    with tab1:
        _render_apply()
    with tab2:
        _render_approvals()
    with tab3:
        _render_history()
    with tab4:
        _render_balances()


# ---------------------------------------------------------------------------
# Tab 1 — Apply for Leave
# ---------------------------------------------------------------------------

def _render_apply():
    """Render the leave application form."""
    st.markdown("### Apply for Leave")

    emp_df      = get_all_employees()
    leave_types = get_leave_types()

    if emp_df.empty:
        st.warning("No employees found.")
        return
    if not leave_types:
        st.warning("No leave types configured.")
        return

    active_emp = emp_df[emp_df["status"] == "Active"]
    emp_labels = {
        f"{r['emp_code']} — {r['full_name']}": int(r["employee_id"])
        for _, r in active_emp.iterrows()
    }
    lt_map = {lt["type_name"]: lt["leave_type_id"] for lt in leave_types}

    with st.form("apply_leave_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            emp_label     = st.selectbox("Employee *", list(emp_labels.keys()))
            leave_type    = st.selectbox("Leave Type *", list(lt_map.keys()))
            start_date    = st.date_input("Start Date *", value=date.today() + timedelta(days=1))
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            end_date = st.date_input("End Date *",   value=date.today() + timedelta(days=1))

        reason = st.text_area("Reason", placeholder="Brief reason for leave…", max_chars=500)

        # Preview
        if end_date >= start_date:
            total = (end_date - start_date).days + 1
            st.info(f"📅 **{total} day(s)** requested ({start_date.strftime('%d %b')} → {end_date.strftime('%d %b %Y')})")

        submitted = st.form_submit_button("📨 Submit Application", type="primary", use_container_width=True)

    if submitted:
        ok_date, msg_date = validate_leave_days(start_date, end_date)
        if not ok_date:
            st.error(f"❌ {msg_date}")
        elif not reason.strip():
            st.error("❌ Please provide a reason for the leave.")
        else:
            emp_id        = emp_labels[emp_label]
            leave_type_id = lt_map[leave_type]
            ok, msg = apply_leave(emp_id, leave_type_id, start_date, end_date, reason)
            if ok:
                st.success("✅ Leave application submitted successfully!")
                st.balloons()
            else:
                st.error(f"❌ {msg}")


# ---------------------------------------------------------------------------
# Tab 2 — Pending Approvals
# ---------------------------------------------------------------------------

def _render_approvals():
    """Allow HR to approve or reject pending leave applications."""
    st.markdown("### Pending Leave Applications")

    # For this demo, approver_id is fixed as employee 9 (Meera Pillai, HR Manager)
    APPROVER_ID = 9

    df = get_pending_leaves()
    if df.empty:
        st.success("🎉 No pending leave applications!")
        return

    st.markdown(f"**{len(df)} pending application(s)**")

    for _, row in df.iterrows():
        leave_id = int(row["leave_id"])
        with st.expander(
            f"📄 {row.get('full_name','—')} ({row.get('emp_code','')}) — "
            f"{row.get('type_name','—')} | {row.get('total_days', 0)} day(s) | "
            f"Applied: {str(row.get('applied_at', ''))[:10]}"
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Department:** {row.get('department_name', '—')}")
                st.write(f"**Leave Type:** {row.get('type_name', '—')}")
            with col2:
                st.write(f"**From:** {str(row.get('start_date', ''))}")
                st.write(f"**To:** {str(row.get('end_date', ''))}")
            with col3:
                st.write(f"**Days:** {row.get('total_days', 0)}")
                st.write(f"**Status:** {row.get('status', '—')}")

            if row.get("reason"):
                st.write(f"**Reason:** {row['reason']}")

            c_approve, c_reject = st.columns(2)
            with c_approve:
                if st.button(f"✅ Approve", key=f"approve_{leave_id}", type="primary"):
                    ok, msg = update_leave_status(leave_id, "Approved", APPROVER_ID)
                    if ok:
                        st.success("Leave approved!")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
            with c_reject:
                if st.button(f"❌ Reject", key=f"reject_{leave_id}", type="secondary"):
                    ok, msg = update_leave_status(leave_id, "Rejected", APPROVER_ID)
                    if ok:
                        st.warning("Leave rejected.")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")


# ---------------------------------------------------------------------------
# Tab 3 — Leave History
# ---------------------------------------------------------------------------

def _render_history():
    """Show all leave applications with filters."""
    st.markdown("### Leave History")

    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Pending", "Approved", "Rejected", "Cancelled"],
            key="lv_hist_status"
        )
    with col2:
        emp_df = get_all_employees()
        emp_opts = {"All Employees": None}
        for _, r in emp_df.iterrows():
            emp_opts[f"{r['emp_code']} — {r['full_name']}"] = int(r["employee_id"])
        emp_sel = st.selectbox("Filter by Employee", list(emp_opts.keys()), key="lv_hist_emp")

    emp_id_filter = emp_opts[emp_sel]

    if emp_id_filter:
        df = get_employee_leaves(emp_id_filter)
        # add dummy columns for consistent display
        df["emp_code"]       = ""
        df["full_name"]      = emp_sel.split("—")[-1].strip() if "—" in emp_sel else ""
        df["department_name"] = ""
    else:
        df = get_all_leaves()

    if status_filter != "All":
        df = df[df["status"] == status_filter]

    if df.empty:
        st.info("No leave applications match the selected filters.")
        return

    st.markdown(f"**{len(df)} record(s) found**")

    show_cols = [c for c in [
        "emp_code", "full_name", "department_name", "type_name",
        "start_date", "end_date", "total_days", "status",
        "approved_by_name", "applied_at",
    ] if c in df.columns]

    rename = {
        "emp_code": "Code", "full_name": "Name", "department_name": "Department",
        "type_name": "Leave Type", "start_date": "From", "end_date": "To",
        "total_days": "Days", "status": "Status",
        "approved_by_name": "Actioned By", "applied_at": "Applied At",
    }
    show_df = df[show_cols].rename(columns=rename).copy()
    if "From" in show_df.columns:
        show_df["From"] = pd.to_datetime(show_df["From"]).dt.strftime("%d %b %Y")
    if "To" in show_df.columns:
        show_df["To"] = pd.to_datetime(show_df["To"]).dt.strftime("%d %b %Y")

    st.dataframe(show_df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Tab 4 — Leave Balances
# ---------------------------------------------------------------------------

def _render_balances():
    """Display leave balance for a selected employee."""
    st.markdown("### Leave Balance Tracker")

    emp_df = get_all_employees()
    if emp_df.empty:
        st.info("No employees found.")
        return

    col1, col2 = st.columns(2)
    with col1:
        emp_labels = {
            f"{r['emp_code']} — {r['full_name']}": int(r["employee_id"])
            for _, r in emp_df.iterrows()
        }
        selected = st.selectbox("Select Employee", list(emp_labels.keys()), key="bal_emp")
        emp_id   = emp_labels[selected]
    with col2:
        year = st.number_input("Year", min_value=2024, max_value=2030,
                               value=date.today().year, key="bal_year")

    df = get_leave_balance(emp_id, int(year))
    if df.empty:
        st.info(f"No leave balance data found for {year}. It may not be initialised yet.")
        return

    st.markdown("---")
    # KPI cards per leave type
    cols = st.columns(len(df))
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i]:
            remaining = int(row.get("remaining_days", 0))
            total     = int(row.get("total_days",     0))
            used      = int(row.get("used_days",       0))
            paid_tag  = "💰 Paid" if row.get("is_paid") else "⛔ Unpaid"
            st.metric(
                label=f"{row['type_name']} {paid_tag}",
                value=f"{remaining} days left",
                delta=f"Used {used} of {total}",
                delta_color="inverse",
            )

    st.markdown("---")
    rename = {
        "type_name": "Leave Type", "is_paid": "Paid?",
        "total_days": "Annual Quota", "used_days": "Used",
        "remaining_days": "Remaining",
    }
    show_df = df[["type_name", "total_days", "used_days", "remaining_days"]].rename(columns=rename)
    st.dataframe(show_df, use_container_width=True, hide_index=True)
