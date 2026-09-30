"""
modules/attendance.py
----------------------
Business logic for Attendance Tracking.

Handles daily attendance marking, history retrieval,
and monthly summary aggregation.
"""

import pandas as pd
from datetime import date
from mysql.connector import Error as MySQLError
from database.connection import execute_query
from database import queries as Q


def mark_attendance(
    employee_id: int,
    attendance_date: date,
    status: str,
    check_in: str | None = None,
    check_out: str | None = None,
    remarks: str = "",
) -> tuple[bool, str]:
    """
    Insert or update attendance for one employee on a given date.

    Uses INSERT … ON DUPLICATE KEY UPDATE so re-submitting the same
    date simply overwrites the previous entry.

    Parameters
    ----------
    employee_id     : int
    attendance_date : date
    status          : str – one of Present/Absent/Half-Day/WFH/Holiday
    check_in        : str | None – HH:MM format
    check_out       : str | None – HH:MM format
    remarks         : str

    Returns
    -------
    (True, "")       on success
    (False, message) on failure
    """
    try:
        execute_query(
            Q.ATT_MARK,
            (employee_id, attendance_date, status, check_in or None, check_out or None, remarks or None),
            fetch="none",
        )
        return True, ""
    except MySQLError as exc:
        return False, f"Could not mark attendance: {exc}"


def get_attendance_by_date(attendance_date: date) -> pd.DataFrame:
    """
    Fetch attendance records for all employees on a specific date.

    Parameters
    ----------
    attendance_date : date

    Returns
    -------
    pd.DataFrame
        Columns: attendance_id, employee_id, emp_code, full_name,
                 department_name, attendance_date, status, check_in,
                 check_out, remarks
    """
    try:
        rows = execute_query(Q.ATT_GET_BY_DATE, (attendance_date,))
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def get_employee_attendance_history(employee_id: int) -> pd.DataFrame:
    """
    Fetch the last 90 attendance records for a single employee.

    Parameters
    ----------
    employee_id : int

    Returns
    -------
    pd.DataFrame
    """
    try:
        rows = execute_query(Q.ATT_HISTORY_BY_EMP, (employee_id,))
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def get_monthly_summary(month: int, year: int) -> pd.DataFrame:
    """
    Fetch attendance summary for all employees in a given month/year.

    Reads from the v_monthly_attendance_summary view.

    Parameters
    ----------
    month : int  (1–12)
    year  : int

    Returns
    -------
    pd.DataFrame
        Columns include attendance_pct, present_days, absent_days, etc.
    """
    try:
        rows = execute_query(Q.ATT_MONTHLY_SUMMARY_ALL, (month, year))
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def get_emp_monthly_summary(employee_id: int, month: int, year: int) -> dict | None:
    """
    Fetch attendance summary for one employee in a given month.

    Parameters
    ----------
    employee_id : int
    month       : int
    year        : int

    Returns
    -------
    dict | None
    """
    try:
        return execute_query(Q.ATT_GET_BY_EMP_MONTH, (employee_id, month, year), fetch="one")
    except MySQLError:
        return None


def get_attendance_trend() -> pd.DataFrame:
    """
    Fetch company-wide average monthly attendance percentage over time.

    Used by the HR Analytics dashboard to plot the attendance trend chart.

    Returns
    -------
    pd.DataFrame
        Columns: year, month, avg_attendance_pct
    """
    try:
        rows = execute_query(Q.ATT_TREND)
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def bulk_mark_attendance(
    employee_ids: list[int],
    attendance_date: date,
    status: str,
) -> tuple[int, int]:
    """
    Mark the same attendance status for a list of employees on one date.

    Useful for marking a company holiday or bulk-setting a day.

    Parameters
    ----------
    employee_ids    : list[int]
    attendance_date : date
    status          : str

    Returns
    -------
    (success_count, failure_count)
    """
    success = 0
    failure = 0
    for emp_id in employee_ids:
        ok, _ = mark_attendance(emp_id, attendance_date, status)
        if ok:
            success += 1
        else:
            failure += 1
    return success, failure
