"""
ui/pages/employee_page.py
--------------------------
Streamlit UI for Employee Management.

Tabs:
  1. Employee Directory  – search, filter, view all employees
  2. Add Employee        – validated form to create a new employee
  3. Edit / Delete       – select an employee and modify or remove them
"""

import streamlit as st
import pandas as pd
from datetime import date

from modules.employee import (
    get_all_employees, search_employees, filter_employees,
    get_departments, get_designations,
    get_employee_by_id,
    add_employee, update_employee, delete_employee,
)
from utils.validators import validate_employee_form
from utils.formatters import format_inr, format_date, status_badge, tenure_string

STATUSES = ["Active", "Inactive", "Resigned", "Terminated"]


def render():
    """Render the Employee Management page with three tabs."""
    st.markdown("## 👥 Employee Management")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 Directory", "➕ Add Employee", "✏️ Edit / Delete"])

    with tab1:
        _render_directory()

    with tab2:
        _render_add_form()

    with tab3:
        _render_edit_delete()


# ---------------------------------------------------------------------------
# Tab 1 — Directory
# ---------------------------------------------------------------------------

def _render_directory():
    """Display the employee directory with search and filter controls."""
    departments = get_departments()
    dept_map = {d["department_name"]: d["department_id"] for d in departments}

    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        search_term = st.text_input("🔍 Search by name, code, email, department…", key="emp_search")
    with col2:
        dept_filter = st.selectbox(
            "Department", ["All"] + list(dept_map.keys()), key="emp_dept_filter"
        )
    with col3:
        status_filter = st.selectbox(
            "Status", ["All"] + STATUSES, key="emp_status_filter"
        )

    # Fetch data
    if search_term:
        df = search_employees(search_term)
    elif dept_filter != "All":
        df = filter_employees(department_id=dept_map[dept_filter])
    elif status_filter != "All":
        df = filter_employees(status=status_filter)
    else:
        df = get_all_employees()

    if df.empty:
        st.info("No employees found matching the criteria.")
        return

    st.markdown(f"**{len(df)} employee(s) found**")

    # Display table
    display_cols = [
        "emp_code", "full_name", "department_name", "designation",
        "joining_date", "basic_salary", "status", "tenure_years",
    ]
    rename_map = {
        "emp_code": "Code", "full_name": "Name",
        "department_name": "Department", "designation": "Designation",
        "joining_date": "Joined", "basic_salary": "Basic Salary (₹)",
        "status": "Status", "tenure_years": "Tenure (yrs)",
    }
    visible = [c for c in display_cols if c in df.columns]
    show_df = df[visible].rename(columns=rename_map).copy()
    if "Basic Salary (₹)" in show_df.columns:
        show_df["Basic Salary (₹)"] = show_df["Basic Salary (₹)"].apply(
            lambda x: f"₹{float(x):,.0f}" if pd.notna(x) else "—"
        )
    if "Joined" in show_df.columns:
        show_df["Joined"] = pd.to_datetime(show_df["Joined"]).dt.strftime("%d %b %Y")

    st.dataframe(show_df, use_container_width=True, hide_index=True)

    # Quick stats
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Shown", len(df))
    with c2:
        active = len(df[df["status"] == "Active"]) if "status" in df.columns else 0
        st.metric("Active", active)
    with c3:
        if "basic_salary" in df.columns and not df.empty:
            avg = df["basic_salary"].astype(float).mean()
            st.metric("Avg Salary", format_inr(avg))
    with c4:
        if "tenure_years" in df.columns and not df.empty:
            avg_t = df["tenure_years"].astype(float).mean()
            st.metric("Avg Tenure", f"{avg_t:.1f} yrs")


# ---------------------------------------------------------------------------
# Tab 2 — Add Employee
# ---------------------------------------------------------------------------

def _render_add_form():
    """Render a validated form to add a new employee."""
    departments = get_departments()
    designations = get_designations()

    if not departments:
        st.warning("No departments found. Please seed the database first.")
        return
    if not designations:
        st.warning("No designations found. Please seed the database first.")
        return

    dept_options = {d["department_name"]: d["department_id"] for d in departments}
    desig_options = {d["title"]: d["designation_id"] for d in designations}

    with st.form("add_employee_form", clear_on_submit=True):
        st.markdown("### New Employee Details")
        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input("First Name *", placeholder="e.g. Aarav")
            email      = st.text_input("Email *", placeholder="aarav@company.in")
            dept_name  = st.selectbox("Department *", list(dept_options.keys()))
            joining_dt = st.date_input("Joining Date *", value=date.today())
            salary     = st.number_input("Basic Salary (₹) *", min_value=0.0, step=1000.0, value=40000.0)

        with col2:
            last_name  = st.text_input("Last Name *", placeholder="e.g. Sharma")
            phone      = st.text_input("Phone", placeholder="9876543210")
            desig_name = st.selectbox("Designation *", list(desig_options.keys()))
            dob        = st.date_input("Date of Birth", value=date(1995, 1, 1))
            status     = st.selectbox("Status", STATUSES, index=0)

        submitted = st.form_submit_button("➕ Add Employee", type="primary", use_container_width=True)

    if submitted:
        errors = validate_employee_form(
            first_name, last_name, email, phone, salary, joining_dt, dob
        )
        if errors:
            for err in errors:
                st.error(f"❌ {err}")
        else:
            ok, result = add_employee(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                department_id=dept_options[dept_name],
                designation_id=desig_options[desig_name],
                joining_date=joining_dt,
                date_of_birth=dob,
                basic_salary=salary,
                status=status,
            )
            if ok:
                st.success(f"✅ Employee added successfully! Employee Code: **{result}**")
                st.balloons()
            else:
                st.error(f"❌ {result}")


# ---------------------------------------------------------------------------
# Tab 3 — Edit / Delete
# ---------------------------------------------------------------------------

def _render_edit_delete():
    """Render employee edit and delete controls."""
    df = get_all_employees()
    if df.empty:
        st.info("No employees found.")
        return

    departments  = get_departments()
    designations = get_designations()
    dept_options  = {d["department_name"]: d["department_id"] for d in departments}
    desig_options = {d["title"]: d["designation_id"] for d in designations}

    # Employee picker
    emp_labels = {
        f"{r['emp_code']} — {r['full_name']}": r["employee_id"]
        for _, r in df.iterrows()
    }
    selected_label = st.selectbox("Select Employee", list(emp_labels.keys()), key="edit_emp_select")
    emp_id = emp_labels[selected_label]
    emp = get_employee_by_id(emp_id)

    if not emp:
        st.error("Could not load employee data.")
        return

    st.markdown("---")
    col_edit, col_del = st.columns([4, 1])

    with col_edit:
        st.markdown("### Edit Employee")

    with col_del:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Delete Employee", type="secondary", key="del_btn"):
            st.session_state["confirm_delete"] = emp_id

    # Delete confirmation
    if st.session_state.get("confirm_delete") == emp_id:
        st.warning(f"⚠️ Are you sure you want to delete **{emp['full_name']}**? This cannot be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Yes, Delete", type="primary", key="confirm_del_yes"):
                ok, msg = delete_employee(emp_id)
                if ok:
                    st.success("Employee deleted successfully.")
                    st.session_state.pop("confirm_delete", None)
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
        with c2:
            if st.button("❌ Cancel", key="confirm_del_no"):
                st.session_state.pop("confirm_delete", None)
                st.rerun()

    # Resolve current dept/desig names
    curr_dept_name  = emp.get("department_name", list(dept_options.keys())[0])
    curr_desig_name = emp.get("designation", list(desig_options.keys())[0])
    dept_list  = list(dept_options.keys())
    desig_list = list(desig_options.keys())
    dept_idx  = dept_list.index(curr_dept_name)  if curr_dept_name  in dept_list  else 0
    desig_idx = desig_list.index(curr_desig_name) if curr_desig_name in desig_list else 0
    curr_status_idx = STATUSES.index(emp.get("status", "Active")) if emp.get("status") in STATUSES else 0

    with st.form(f"edit_employee_form_{emp_id}"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *", value=emp.get("first_name", ""))
            email      = st.text_input("Email *",      value=emp.get("email", ""))
            dept_name  = st.selectbox("Department *",  dept_list,  index=dept_idx)
            joining_dt = st.date_input(
                "Joining Date *",
                value=emp.get("joining_date") or date.today(),
            )
            salary = st.number_input(
                "Basic Salary (₹) *",
                min_value=0.0, step=1000.0,
                value=float(emp.get("basic_salary") or 0),
            )
        with col2:
            last_name  = st.text_input("Last Name *", value=emp.get("last_name", ""))
            phone      = st.text_input("Phone",       value=emp.get("phone", "") or "")
            desig_name = st.selectbox("Designation *", desig_list, index=desig_idx)
            dob_val    = emp.get("date_of_birth") or date(1990, 1, 1)
            dob        = st.date_input("Date of Birth", value=dob_val)
            status     = st.selectbox("Status", STATUSES, index=curr_status_idx)

        submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)

    if submitted:
        errors = validate_employee_form(
            first_name, last_name, email, phone, salary, joining_dt, dob
        )
        if errors:
            for err in errors:
                st.error(f"❌ {err}")
        else:
            ok, msg = update_employee(
                employee_id=emp_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                department_id=dept_options[dept_name],
                designation_id=desig_options[desig_name],
                joining_date=joining_dt,
                date_of_birth=dob,
                basic_salary=salary,
                status=status,
            )
            if ok:
                st.success("✅ Employee updated successfully!")
                st.rerun()
            else:
                st.error(f"❌ {msg}")
