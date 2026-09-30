"""
ui/pages/payroll_page.py
--------------------------
Streamlit UI for Payroll Management.

Tabs:
  1. Generate Payroll  – run payroll for one employee or all employees
  2. Payroll Register  – browse monthly payroll register
  3. Payslip View      – detailed payslip for a specific record
  4. Employee History  – all pay months for one employee
"""

import streamlit as st
import pandas as pd
from datetime import date
import calendar

from modules.payroll import (
    generate_payroll_for_employee,
    generate_payroll_bulk,
    get_payroll_by_month,
    get_payroll_history,
    get_payslip_details,
    mark_payslip_generated,
    payroll_exists,
)
from modules.employee import get_all_employees
from utils.formatters import format_inr, format_datetime, month_name


def render():
    """Render the Payroll Management page."""
    st.markdown("## 💰 Payroll Management")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "⚙️ Generate Payroll",
        "📋 Monthly Register",
        "🧾 Payslip View",
        "📜 Employee History",
    ])

    with tab1:
        _render_generate()
    with tab2:
        _render_register()
    with tab3:
        _render_payslip()
    with tab4:
        _render_emp_history()


# ---------------------------------------------------------------------------
# Tab 1 — Generate Payroll
# ---------------------------------------------------------------------------

def _render_generate():
    """Payroll generation controls — single employee or bulk."""
    st.markdown("### Generate Monthly Payroll")
    st.info(
        "ℹ️ Payroll is calculated using the **sp_generate_payroll** stored procedure. "
        "It prorates salary by attendance and applies HRA, Medical, Transport allowances "
        "and PF + Professional Tax deductions."
    )

    col1, col2 = st.columns(2)
    with col1:
        sel_month = st.selectbox(
            "Month *", list(range(1, 13)),
            format_func=month_name,
            index=date.today().month - 2 if date.today().month > 1 else 0,
            key="gen_month",
        )
    with col2:
        sel_year = st.number_input("Year *", min_value=2020, max_value=2030,
                                   value=date.today().year, key="gen_year")

    emp_df = get_all_employees()
    active_emp = emp_df[emp_df["status"] == "Active"] if not emp_df.empty else pd.DataFrame()

    st.markdown("---")
    mode = st.radio("Generation Mode", ["🏢 Bulk (all active employees)", "👤 Single employee"], key="gen_mode")

    if mode.startswith("🏢"):
        # Bulk generation
        st.markdown(f"**{len(active_emp)} active employees** will be processed.")
        col_gen, col_info = st.columns([1, 3])
        with col_gen:
            if st.button("🚀 Run Bulk Payroll", type="primary"):
                emp_ids = active_emp["employee_id"].tolist()
                with st.spinner("Generating payroll…"):
                    s, f, errs = generate_payroll_bulk(
                        emp_ids, int(sel_month), int(sel_year)
                    )
                st.success(f"✅ **{s}** processed successfully.")
                if f:
                    st.warning(f"⚠️ **{f}** skipped (already generated or error).")
                    with st.expander("Details"):
                        for err in errs:
                            st.text(err)
    else:
        # Single employee
        emp_labels = {
            f"{r['emp_code']} — {r['full_name']}": int(r["employee_id"])
            for _, r in active_emp.iterrows()
        }
        if not emp_labels:
            st.info("No active employees.")
            return
        selected = st.selectbox("Select Employee", list(emp_labels.keys()), key="gen_emp")
        emp_id   = emp_labels[selected]

        already = payroll_exists(emp_id, int(sel_month), int(sel_year))
        if already:
            st.warning(f"⚠️ Payroll for {month_name(sel_month)} {sel_year} already exists for this employee.")

        if st.button("🚀 Generate Payroll", type="primary", disabled=already):
            ok, msg = generate_payroll_for_employee(emp_id, int(sel_month), int(sel_year))
            if ok:
                st.success("✅ Payroll generated successfully!")
                st.balloons()
            else:
                st.error(f"❌ {msg}")


# ---------------------------------------------------------------------------
# Tab 2 — Monthly Register
# ---------------------------------------------------------------------------

def _render_register():
    """Browse the payroll register for a selected month."""
    st.markdown("### Monthly Payroll Register")

    col1, col2 = st.columns(2)
    with col1:
        sel_month = st.selectbox(
            "Month", list(range(1, 13)),
            format_func=month_name,
            index=date.today().month - 2 if date.today().month > 1 else 0,
            key="reg_month",
        )
    with col2:
        sel_year = st.number_input("Year", min_value=2020, max_value=2030,
                                   value=date.today().year, key="reg_year")

    df = get_payroll_by_month(int(sel_month), int(sel_year))
    if df.empty:
        st.info(f"No payroll records for {month_name(sel_month)} {sel_year}. Generate payroll first.")
        return

    # Summary KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Employees", len(df))
    with c2: st.metric("Total Payroll", format_inr(df["net_salary"].astype(float).sum()))
    with c3: st.metric("Avg Net Salary", format_inr(df["net_salary"].astype(float).mean()))
    with c4: st.metric("Avg Attendance", f"{(df['present_days'].astype(float) / df['working_days'].astype(float) * 100).mean():.1f}%")

    st.markdown("---")

    show_cols = [c for c in [
        "emp_code", "full_name", "department_name", "designation",
        "basic_salary", "total_allowances", "total_deductions", "net_salary",
        "working_days", "present_days", "payslip_generated",
    ] if c in df.columns]
    rename = {
        "emp_code": "Code", "full_name": "Name",
        "department_name": "Department", "designation": "Designation",
        "basic_salary": "Basic (₹)", "total_allowances": "Allowances (₹)",
        "total_deductions": "Deductions (₹)", "net_salary": "Net Salary (₹)",
        "working_days": "Working Days", "present_days": "Present Days",
        "payslip_generated": "Payslip Generated",
    }
    show_df = df[show_cols].rename(columns=rename).copy()
    for col in ["Basic (₹)", "Allowances (₹)", "Deductions (₹)", "Net Salary (₹)"]:
        if col in show_df.columns:
            show_df[col] = show_df[col].apply(lambda x: f"₹{float(x):,.0f}")

    st.dataframe(show_df, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Tab 3 — Payslip View
# ---------------------------------------------------------------------------

def _render_payslip():
    """Show a detailed payslip for a selected employee and month."""
    st.markdown("### Payslip Viewer")

    col1, col2, col3 = st.columns(3)
    with col1:
        emp_df = get_all_employees()
        emp_labels = {
            f"{r['emp_code']} — {r['full_name']}": int(r["employee_id"])
            for _, r in emp_df.iterrows()
        }
        selected = st.selectbox("Employee", list(emp_labels.keys()), key="ps_emp")
        emp_id   = emp_labels[selected]
    with col2:
        sel_month = st.selectbox(
            "Month", list(range(1, 13)), format_func=month_name,
            index=date.today().month - 2 if date.today().month > 1 else 0,
            key="ps_month",
        )
    with col3:
        sel_year = st.number_input("Year", min_value=2020, max_value=2030,
                                   value=date.today().year, key="ps_year")

    # Find payroll record
    payroll_df = get_payroll_by_month(int(sel_month), int(sel_year))
    emp_payroll = payroll_df[payroll_df["employee_id"] == emp_id] if not payroll_df.empty else pd.DataFrame()

    if emp_payroll.empty:
        st.info("No payroll record found for this selection. Generate payroll first.")
        return

    row = emp_payroll.iloc[0]
    payroll_id = int(row["payroll_id"])

    # ---- Payslip card ----
    st.markdown("---")
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #ec489911 0%, #06b6d411 100%);
                    border-radius: 16px; padding: 28px; color: #f3f4f6; margin-bottom: 24px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h2 style="margin:0; color:#ec4899;">PAYSLIP</h2>
                    <p style="margin:4px 0 0 0; color:#a1a1aa; font-size:0.9rem;">
                        {month_name(int(row['month']))} {int(row['year'])}
                    </p>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:0.85rem; color:#a1a1aa;">Generated</span><br>
                    <span style="font-size:0.85rem;">{str(row.get('generated_at','—'))[:16]}</span>
                </div>
            </div>
            <hr style="border-color:#27272a; margin: 20px 0;">
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div>
                    <p style="margin:0; color:#a1a1aa; font-size:0.8rem;">EMPLOYEE</p>
                    <p style="margin:0; font-size:1.1rem; font-weight:600;">{row.get('full_name','—')}</p>
                    <p style="margin:4px 0 0 0; color:#a1a1aa; font-size:0.85rem;">{row.get('emp_code','')}</p>
                </div>
                <div>
                    <p style="margin:0; color:#a1a1aa; font-size:0.8rem;">DEPARTMENT / DESIGNATION</p>
                    <p style="margin:0;">{row.get('department_name','—')}</p>
                    <p style="margin:4px 0 0 0; color:#a1a1aa; font-size:0.85rem;">{row.get('designation','—')}</p>
                </div>
                <div>
                    <p style="margin:0; color:#a1a1aa; font-size:0.8rem;">WORKING DAYS / PRESENT</p>
                    <p style="margin:0;">{row.get('working_days','—')} / {row.get('present_days','—')}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Breakdown
    details_df = get_payslip_details(payroll_id)
    if not details_df.empty:
        allowances = details_df[details_df["component_type"] == "Allowance"]
        deductions = details_df[details_df["component_type"] == "Deduction"]

        col_ea, col_ed = st.columns(2)
        with col_ea:
            st.markdown("##### 📈 Earnings")
            st.markdown(
                f"| Component | Amount |\n|---|---|\n"
                f"| Basic Salary | {format_inr(float(row['basic_salary']))} |\n"
                + "".join(
                    f"| {r['component_name']} | {format_inr(float(r['amount']))} |\n"
                    for _, r in allowances.iterrows()
                )
            )
        with col_ed:
            st.markdown("##### 📉 Deductions")
            st.markdown(
                "| Component | Amount |\n|---|---|\n"
                + "".join(
                    f"| {r['component_name']} | {format_inr(float(r['amount']))} |\n"
                    for _, r in deductions.iterrows()
                )
            )

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Gross (Basic + Allowances)", format_inr(float(row['basic_salary']) + float(row['total_allowances'])))
    with c2:
        st.metric("Total Deductions", format_inr(float(row['total_deductions'])))
    with c3:
        st.metric("🟢 Net Salary", format_inr(float(row['net_salary'])))

    st.markdown("---")
    if not row.get("payslip_generated"):
        if st.button("📄 Mark as Payslip Issued", type="primary"):
            ok, msg = mark_payslip_generated(payroll_id)
            if ok:
                st.success("Payslip marked as issued.")
                st.rerun()
            else:
                st.error(f"❌ {msg}")
    else:
        st.success("✅ Payslip has been issued.")


# ---------------------------------------------------------------------------
# Tab 4 — Employee Payroll History
# ---------------------------------------------------------------------------

def _render_emp_history():
    """Show all pay months for a single employee."""
    st.markdown("### Employee Payroll History")

    emp_df = get_all_employees()
    emp_labels = {
        f"{r['emp_code']} — {r['full_name']}": int(r["employee_id"])
        for _, r in emp_df.iterrows()
    }
    selected = st.selectbox("Select Employee", list(emp_labels.keys()), key="ph_emp")
    emp_id   = emp_labels[selected]

    df = get_payroll_history(emp_id)
    if df.empty:
        st.info("No payroll history found for this employee.")
        return

    st.metric("Total Records", len(df))
    st.metric("Total Earned (Net)", format_inr(df["net_salary"].astype(float).sum()))

    rename = {
        "month": "Month", "year": "Year",
        "basic_salary": "Basic (₹)", "total_allowances": "Allowances (₹)",
        "total_deductions": "Deductions (₹)", "net_salary": "Net Salary (₹)",
        "working_days": "Working Days", "present_days": "Present Days",
        "payslip_generated": "Issued",
    }
    show_cols = [c for c in rename if c in df.columns]
    show_df = df[show_cols].rename(columns=rename).copy()
    show_df["Month"] = show_df["Month"].apply(lambda m: month_name(int(m)))
    for col in ["Basic (₹)", "Allowances (₹)", "Deductions (₹)", "Net Salary (₹)"]:
        if col in show_df.columns:
            show_df[col] = show_df[col].apply(lambda x: f"₹{float(x):,.0f}")

    st.dataframe(show_df, use_container_width=True, hide_index=True)
