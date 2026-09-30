"""
modules/analytics.py
---------------------
Data aggregation layer for the HR Analytics Dashboard.

Calls employee, attendance, and payroll modules to assemble
the data frames consumed by Plotly charts on the analytics page.
"""

import pandas as pd
from datetime import date

from modules.employee import (
    get_headcount,
    get_attrition_rate,
    get_avg_salary,
    get_avg_tenure,
    get_dept_headcount,
    get_salary_distribution,
)
from modules.attendance import get_attendance_trend
from modules.payroll import get_payroll_trend, get_month_total_payroll
from database.connection import execute_query
from database import queries as Q
from mysql.connector import Error as MySQLError


def get_kpi_data(month: int, year: int) -> dict:
    """
    Aggregate all KPI values required for the top cards on the dashboard.

    Parameters
    ----------
    month : int  – for current-month payroll total
    year  : int

    Returns
    -------
    dict with keys:
        headcount          : int
        attrition_rate     : float  (%)
        avg_salary         : float  (₹)
        avg_tenure         : float  (years)
        pending_leaves     : int
        total_payroll      : float  (₹)
    """
    pending_leaves = 0
    try:
        row = execute_query(Q.KPI_PENDING_LEAVES, fetch="one")
        pending_leaves = int(row["total"]) if row else 0
    except MySQLError:
        pass

    return {
        "headcount":      get_headcount(),
        "attrition_rate": get_attrition_rate(),
        "avg_salary":     get_avg_salary(),
        "avg_tenure":     get_avg_tenure(),
        "pending_leaves": pending_leaves,
        "total_payroll":  get_month_total_payroll(month, year),
    }


def get_dept_chart_data() -> pd.DataFrame:
    """
    Return department-wise active headcount for the bar chart.

    Returns
    -------
    pd.DataFrame
        Columns: department_name, headcount
    """
    return get_dept_headcount()


def get_attendance_trend_data() -> pd.DataFrame:
    """
    Return month-wise average attendance percentage for the line chart.

    Adds a 'label' column formatted as 'Jan 2026' for the x-axis.

    Returns
    -------
    pd.DataFrame
        Columns: year, month, avg_attendance_pct, label
    """
    df = get_attendance_trend()
    if df.empty:
        return df
    month_names = [
        "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    df["label"] = df.apply(
        lambda r: f"{month_names[int(r['month'])]} {int(r['year'])}", axis=1
    )
    return df


def get_salary_dist_data() -> pd.DataFrame:
    """
    Return salary band distribution data for the histogram/bar chart.

    Returns
    -------
    pd.DataFrame
        Columns: salary_band, count
    """
    return get_salary_distribution()


def get_payroll_trend_data() -> pd.DataFrame:
    """
    Return monthly payroll totals over time for a line/area chart.

    Adds a 'label' column formatted as 'Jan 2026'.

    Returns
    -------
    pd.DataFrame
        Columns: month, year, total_payroll, avg_net_salary, employee_count, label
    """
    df = get_payroll_trend()
    if df.empty:
        return df
    month_names = [
        "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    df["label"] = df.apply(
        lambda r: f"{month_names[int(r['month'])]} {int(r['year'])}", axis=1
    )
    return df
