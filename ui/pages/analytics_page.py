"""
ui/pages/analytics_page.py
----------------------------
Streamlit UI for the HR Analytics Dashboard.

Displays:
  - KPI cards: headcount, attrition rate, avg salary, avg tenure, pending leaves
  - Department-wise headcount bar chart (Plotly)
  - Attendance trend line chart (Plotly)
  - Salary distribution bar chart (Plotly)
  - Payroll trend area chart (Plotly)
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import pandas as pd

from modules.analytics import (
    get_kpi_data,
    get_dept_chart_data,
    get_attendance_trend_data,
    get_salary_dist_data,
    get_payroll_trend_data,
)
from utils.formatters import format_inr

# ---- Plotly theme settings ------------------------------------------------
PLOTLY_THEME   = "plotly_white"
PRIMARY_COLOR  = "#4F46E5"
ACCENT_COLORS  = ["#4F46E5", "#0EA5E9", "#10B981", "#F59E0B", "#8B5CF6", "#F43F5E"]
CHART_BG       = "rgba(0,0,0,0)"
FONT_FAMILY    = "Inter, sans-serif"


def _plotly_layout(title: str = "") -> dict:
    """Return a consistent Plotly layout dict for all charts."""
    return dict(
        title=dict(text=title, font=dict(size=16, color="#0F172A", family=FONT_FAMILY)),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color="#64748B", family=FONT_FAMILY),
        margin=dict(l=16, r=16, t=48, b=16),
    )


def render():
    """Render the HR Analytics Dashboard page."""
    st.markdown("## 📊 HR Analytics Dashboard")
    st.markdown("---")

    today = date.today()
    # Use previous month for payroll KPI (current month may not be generated yet)
    kpi_month = today.month - 1 if today.month > 1 else 12
    kpi_year  = today.year if today.month > 1 else today.year - 1

    with st.spinner("Loading analytics…"):
        kpis        = get_kpi_data(kpi_month, kpi_year)
        dept_df     = get_dept_chart_data()
        att_df      = get_attendance_trend_data()
        salary_df   = get_salary_dist_data()
        payroll_df  = get_payroll_trend_data()

    # -----------------------------------------------------------------------
    # KPI Row
    # -----------------------------------------------------------------------
    st.markdown("### 🔢 Key Performance Indicators")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        _kpi_card(c1, "👥 Headcount",      str(kpis["headcount"]),         None)
    with c2:
        _kpi_card(c2, "📉 Attrition Rate", f"{kpis['attrition_rate']:.1f}%", None)
    with c3:
        _kpi_card(c3, "💰 Avg Salary",     format_inr(kpis["avg_salary"]), None)
    with c4:
        _kpi_card(c4, "📅 Avg Tenure",     f"{kpis['avg_tenure']:.1f} yrs", None)
    with c5:
        _kpi_card(c5, "🗓️ Pending Leaves", str(kpis["pending_leaves"]),    None)
    with c6:
        _kpi_card(c6, "🏦 Payroll (prev mo.)", format_inr(kpis["total_payroll"]), None)

    st.markdown("---")

    # -----------------------------------------------------------------------
    # Row 1: Department Headcount + Salary Distribution
    # -----------------------------------------------------------------------
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 🏢 Department-wise Headcount")
        if not dept_df.empty:
            fig = px.bar(
                dept_df,
                x="headcount",
                y="department_name",
                orientation="h",
                color="headcount",
                color_continuous_scale=["#0EA5E9", "#4F46E5"],
                text="headcount",
                template=PLOTLY_THEME,
            )
            fig.update_traces(
                textposition="outside",
                marker_line_width=0,
                hovertemplate="<b>%{y}</b><br>Headcount: %{x}<extra></extra>",
            )
            fig.update_layout(
                **_plotly_layout(""),
                xaxis_title="",
                yaxis_title="",
                coloraxis_showscale=False,
                height=380,
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No department data available.")

    with col_right:
        st.markdown("#### 💵 Salary Distribution (Active Employees)")
        if not salary_df.empty:
            fig = px.bar(
                salary_df,
                x="salary_band",
                y="count",
                color="salary_band",
                color_discrete_sequence=ACCENT_COLORS,
                text="count",
                template=PLOTLY_THEME,
            )
            fig.update_traces(
                textposition="outside",
                marker_line_width=0,
                hovertemplate="<b>%{x}</b><br>Employees: %{y}<extra></extra>",
            )
            fig.update_layout(
                **_plotly_layout(""),
                xaxis_title="Salary Band",
                yaxis_title="No. of Employees",
                height=380,
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No salary data available.")

    st.markdown("---")

    # -----------------------------------------------------------------------
    # Row 2: Attendance Trend + Payroll Trend
    # -----------------------------------------------------------------------
    col_att, col_pay = st.columns(2)

    with col_att:
        st.markdown("#### 📅 Attendance Trend (Company-wide %)")
        if not att_df.empty and "label" in att_df.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=att_df["label"],
                y=att_df["avg_attendance_pct"].astype(float),
                mode="lines+markers",
                line=dict(color=PRIMARY_COLOR, width=3),
                marker=dict(size=8, color=PRIMARY_COLOR),
                fill="tozeroy",
                fillcolor="rgba(79,70,229,0.12)",
                hovertemplate="<b>%{x}</b><br>Attendance: %{y:.1f}%<extra></extra>",
            ))
            fig.add_hline(
                y=90, line_dash="dot", line_color="#10B981",
                annotation_text="Target 90%", annotation_position="top right",
            )
            fig.update_layout(
                **_plotly_layout(""),
                xaxis_title="",
                yaxis_title="Attendance %",
                yaxis=dict(range=[0, 105]),
                height=320,
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor="rgba(226,232,240,0.5)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No attendance trend data available.")

    with col_pay:
        st.markdown("#### 🏦 Monthly Payroll Trend")
        if not payroll_df.empty and "label" in payroll_df.columns:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=payroll_df["label"],
                y=payroll_df["total_payroll"].astype(float),
                marker_color=ACCENT_COLORS[1],
                hovertemplate="<b>%{x}</b><br>Total Payroll: ₹%{y:,.0f}<extra></extra>",
                name="Total Payroll",
            ))
            fig.add_trace(go.Scatter(
                x=payroll_df["label"],
                y=payroll_df["avg_net_salary"].astype(float),
                mode="lines+markers",
                line=dict(color="#10B981", width=2),
                marker=dict(size=7),
                yaxis="y2",
                name="Avg Net Salary",
                hovertemplate="<b>%{x}</b><br>Avg Net: ₹%{y:,.0f}<extra></extra>",
            ))
            fig.update_layout(
                **_plotly_layout(""),
                showlegend=True,
                xaxis_title="",
                yaxis_title="Total Payroll (₹)",
                yaxis2=dict(
                    title="Avg Net Salary (₹)",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                    color="#10B981",
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                height=320,
            )
            fig.update_xaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No payroll trend data available. Generate payroll for previous months.")

    st.markdown("---")

    # -----------------------------------------------------------------------
    # Row 3: Status Breakdown Donut
    # -----------------------------------------------------------------------
    st.markdown("#### 👥 Employee Status Breakdown")
    from database.connection import execute_query
    from database.queries import EMP_COUNT_BY_STATUS
    try:
        status_rows = execute_query(EMP_COUNT_BY_STATUS)
        if status_rows:
            status_df = pd.DataFrame(status_rows)
            STATUS_COLORS_PIE = {
                "Active": "#10B981", "Inactive": "#F59E0B",
                "Resigned": "#64748B", "Terminated": "#EF4444",
            }
            colors = [STATUS_COLORS_PIE.get(s, "#64748B") for s in status_df["status"]]
            fig = go.Figure(go.Pie(
                labels=status_df["status"],
                values=status_df["count"],
                hole=0.55,
                marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
            ))
            fig.update_layout(
                **_plotly_layout(""),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.15),
                height=300,
                annotations=[dict(
                    text=f"<b>{sum(r['count'] for r in status_rows)}</b><br>Total",
                    x=0.5, y=0.5, font_size=18, showarrow=False, font_color="#0F172A",
                )],
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Helper: KPI card using Streamlit metric + custom CSS
# ---------------------------------------------------------------------------

def _kpi_card(col, label: str, value: str, delta):
    """Render a metric in the given column."""
    with col:
        st.metric(label=label, value=value, delta=delta)
