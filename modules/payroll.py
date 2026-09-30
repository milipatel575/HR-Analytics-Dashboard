"""
modules/payroll.py
-------------------
Business logic for Payroll Management.

Payroll generation delegates heavy lifting to the MySQL stored procedure
sp_generate_payroll, which handles prorating, component calculation,
and atomicity via a BEGIN TRANSACTION/COMMIT block.

This module also provides read helpers for payslip views and history.
"""

import pandas as pd
from datetime import date
import calendar
from mysql.connector import Error as MySQLError
from database.connection import DBConnection, call_procedure, execute_query
from database import queries as Q


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _working_days_in_month(month: int, year: int) -> int:
    """
    Count working days (Mon-Sat) in the given month/year.

    Parameters
    ----------
    month : int  (1-12)
    year  : int

    Returns
    -------
    int  – number of weekdays excluding Sundays only
    """
    _, days_in_month = calendar.monthrange(year, month)
    count = 0
    for day in range(1, days_in_month + 1):
        weekday = date(year, month, day).weekday()  # 0=Mon … 6=Sun
        if weekday != 6:   # exclude Sundays
            count += 1
    return count


def _get_present_days(employee_id: int, month: int, year: int) -> int:
    """
    Count days an employee was Present/WFH/Half-Day in a given month.

    Half-Day counts as 1 (for salary purposes; you can change to 0.5).

    Parameters
    ----------
    employee_id : int
    month       : int
    year        : int

    Returns
    -------
    int
    """
    try:
        row = execute_query(Q.PAYROLL_PRESENT_DAYS, (employee_id, month, year), fetch="one")
        return int(row["present_days"]) if row else 0
    except MySQLError:
        return 0


# ---------------------------------------------------------------------------
# Check if payroll already exists
# ---------------------------------------------------------------------------

def payroll_exists(employee_id: int, month: int, year: int) -> bool:
    """
    Return True if payroll has already been generated for this period.

    Parameters
    ----------
    employee_id : int
    month       : int
    year        : int

    Returns
    -------
    bool
    """
    try:
        row = execute_query(Q.PAYROLL_EXISTS, (employee_id, month, year), fetch="one")
        return int(row["cnt"]) > 0 if row else False
    except MySQLError:
        return False


# ---------------------------------------------------------------------------
# Generate payroll (calls stored procedure)
# ---------------------------------------------------------------------------

def generate_payroll_for_employee(
    employee_id: int,
    month: int,
    year: int,
) -> tuple[bool, str]:
    """
    Generate payroll for one employee for a given month/year.

    Delegates to the MySQL stored procedure sp_generate_payroll which:
      - Prorates basic salary based on present days.
      - Applies all payroll components (allowances and deductions).
      - Inserts into payroll and payroll_details atomically.
      - Raises SQLSTATE 45000 if payroll already exists.

    Parameters
    ----------
    employee_id : int
    month       : int  (1-12)
    year        : int

    Returns
    -------
    (True, "")       on success
    (False, message) on failure
    """
    working_days = _working_days_in_month(month, year)
    present_days = _get_present_days(employee_id, month, year)

    try:
        call_procedure(
            "sp_generate_payroll",
            (employee_id, month, year, working_days, present_days),
        )
        return True, ""
    except MySQLError as exc:
        msg = str(exc)
        if "already generated" in msg:
            return False, "Payroll already generated for this period."
        return False, f"Payroll generation failed: {exc}"


def generate_payroll_bulk(
    employee_ids: list[int],
    month: int,
    year: int,
) -> tuple[int, int, list[str]]:
    """
    Generate payroll for multiple employees in one batch.

    Parameters
    ----------
    employee_ids : list[int]
    month        : int
    year         : int

    Returns
    -------
    (success_count, failure_count, error_messages)
    """
    success = 0
    failure = 0
    errors: list[str] = []
    for emp_id in employee_ids:
        ok, msg = generate_payroll_for_employee(emp_id, month, year)
        if ok:
            success += 1
        else:
            failure += 1
            errors.append(f"EMP#{emp_id}: {msg}")
    return success, failure, errors


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------

def get_payroll_by_month(month: int, year: int) -> pd.DataFrame:
    """
    Fetch all payroll records for a given month/year.

    Parameters
    ----------
    month : int
    year  : int

    Returns
    -------
    pd.DataFrame
    """
    try:
        rows = execute_query(Q.PAYROLL_GET_BY_MONTH, (month, year))
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def get_payroll_history(employee_id: int) -> pd.DataFrame:
    """
    Fetch all payroll records for a single employee (all months).

    Parameters
    ----------
    employee_id : int

    Returns
    -------
    pd.DataFrame
    """
    try:
        rows = execute_query(Q.PAYROLL_GET_BY_EMP, (employee_id,))
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def get_payslip_details(payroll_id: int) -> pd.DataFrame:
    """
    Fetch line-item breakdown (components) for a specific payroll record.

    Parameters
    ----------
    payroll_id : int

    Returns
    -------
    pd.DataFrame
        Columns: component_name, component_type, amount
    """
    try:
        rows = execute_query(Q.PAYROLL_GET_DETAILS, (payroll_id,))
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def mark_payslip_generated(payroll_id: int) -> tuple[bool, str]:
    """
    Mark a payroll record as 'payslip generated'.

    Called after the user views / downloads the payslip to record
    that it was formally issued.

    Parameters
    ----------
    payroll_id : int

    Returns
    -------
    (True, "")       on success
    (False, message) on failure
    """
    try:
        execute_query(Q.PAYROLL_MARK_GENERATED, (payroll_id,), fetch="none")
        return True, ""
    except MySQLError as exc:
        return False, f"Database error: {exc}"


def get_payroll_trend() -> pd.DataFrame:
    """
    Fetch monthly payroll totals and averages across all periods.

    Used by the analytics dashboard to show payroll trends.

    Returns
    -------
    pd.DataFrame
        Columns: month, year, total_payroll, avg_net_salary, employee_count
    """
    try:
        rows = execute_query(Q.PAYROLL_TREND)
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def get_month_total_payroll(month: int, year: int) -> float:
    """
    Return the total net salary payout for a given month/year.

    Parameters
    ----------
    month : int
    year  : int

    Returns
    -------
    float
    """
    try:
        row = execute_query(Q.KPI_PAYROLL_CURRENT_MONTH, (month, year), fetch="one")
        return float(row["total_payroll"] or 0) if row else 0.0
    except MySQLError:
        return 0.0
