"""
modules/leave.py
-----------------
Business logic for Leave Management.

Implements the leave workflow:
    Employee applies → HR approves/rejects → balance updated.
"""

import pandas as pd
from datetime import date
from mysql.connector import Error as MySQLError
from database.connection import DBConnection, execute_query
from database import queries as Q


def get_leave_types() -> list[dict]:
    """
    Fetch all configured leave types.

    Returns
    -------
    list[dict]
        Each dict has: leave_type_id, type_name, annual_quota, is_paid
    """
    try:
        return execute_query(Q.LEAVE_TYPES_ALL) or []
    except MySQLError:
        return []


def get_leave_balance(employee_id: int, year: int) -> pd.DataFrame:
    """
    Fetch leave balance for an employee in a given year.

    Parameters
    ----------
    employee_id : int
    year        : int

    Returns
    -------
    pd.DataFrame
        Columns: type_name, is_paid, total_days, used_days, remaining_days
    """
    try:
        rows = execute_query(Q.LEAVE_BALANCE_BY_EMP, (employee_id, year))
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def apply_leave(
    employee_id: int,
    leave_type_id: int,
    start_date: date,
    end_date: date,
    reason: str,
) -> tuple[bool, str]:
    """
    Submit a new leave application.

    Computes total_days from start_date and end_date (inclusive).
    Validates that the employee has enough remaining balance before inserting.

    Parameters
    ----------
    employee_id   : int
    leave_type_id : int
    start_date    : date
    end_date      : date
    reason        : str

    Returns
    -------
    (True, "")       on success
    (False, message) on insufficient balance or DB error
    """
    total_days = (end_date - start_date).days + 1
    year = start_date.year

    try:
        # Check balance
        balance_rows = execute_query(Q.LEAVE_BALANCE_BY_EMP, (employee_id, year))
        balance = None
        for row in (balance_rows or []):
            if row["leave_type_id"] == leave_type_id:  # type: ignore[index]
                balance = row
                break

        if balance is None:
            return False, "No leave balance found for this employee and leave type."

        remaining = int(balance["remaining_days"])
        if total_days > remaining:
            return False, (
                f"Insufficient leave balance. "
                f"Requested: {total_days} days, Available: {remaining} days."
            )

        execute_query(
            Q.LEAVE_APPLY,
            (employee_id, leave_type_id, start_date, end_date, total_days, reason.strip()),
            fetch="none",
        )
        return True, ""
    except MySQLError as exc:
        return False, f"Database error: {exc}"


def get_all_leaves() -> pd.DataFrame:
    """
    Fetch all leave applications with employee and leave type details.

    Returns
    -------
    pd.DataFrame
    """
    try:
        rows = execute_query(Q.LEAVE_GET_ALL)
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def get_pending_leaves() -> pd.DataFrame:
    """
    Fetch only pending leave applications (awaiting HR action).

    Returns
    -------
    pd.DataFrame
    """
    try:
        rows = execute_query(Q.LEAVE_GET_PENDING)
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def get_employee_leaves(employee_id: int) -> pd.DataFrame:
    """
    Fetch all leave applications for a specific employee.

    Parameters
    ----------
    employee_id : int

    Returns
    -------
    pd.DataFrame
    """
    try:
        rows = execute_query(Q.LEAVE_GET_BY_EMP, (employee_id,))
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def update_leave_status(
    leave_id: int,
    new_status: str,
    approver_id: int,
) -> tuple[bool, str]:
    """
    Approve or reject a leave application.

    If approving, also deducts the leave days from the employee's balance.
    Status must be 'Approved' or 'Rejected'.

    Parameters
    ----------
    leave_id    : int
    new_status  : str  – 'Approved' or 'Rejected'
    approver_id : int  – employee_id of the HR manager taking action

    Returns
    -------
    (True, "")       on success
    (False, message) on failure
    """
    if new_status not in ("Approved", "Rejected"):
        return False, "Status must be 'Approved' or 'Rejected'."

    try:
        with DBConnection() as conn:
            cursor = conn.cursor(dictionary=True)

            # Fetch leave details before updating
            cursor.execute(
                "SELECT employee_id, leave_type_id, total_days, start_date "
                "FROM leaves WHERE leave_id = %s",
                (leave_id,)
            )
            leave = cursor.fetchone()
            if not leave:
                return False, "Leave application not found."

            # Update status
            cursor.execute(Q.LEAVE_UPDATE_STATUS, (new_status, approver_id, leave_id))

            # If approved, deduct from balance
            if new_status == "Approved":
                year = leave["start_date"].year
                cursor.execute(Q.LEAVE_BALANCE_UPDATE_USED, (
                    leave["total_days"],
                    leave["employee_id"],
                    leave["leave_type_id"],
                    year,
                ))

        return True, ""
    except MySQLError as exc:
        return False, f"Database error: {exc}"


def cancel_leave(leave_id: int) -> tuple[bool, str]:
    """
    Cancel a pending leave application.

    Only 'Pending' leaves can be cancelled. Already actioned leaves
    must be rejected by HR, not cancelled by the employee.

    Parameters
    ----------
    leave_id : int

    Returns
    -------
    (True, "")       on success
    (False, message) on failure
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT status FROM leaves WHERE leave_id = %s",
                (leave_id,)
            )
            row = cursor.fetchone()
            if not row:
                return False, "Leave application not found."
            if row["status"] != "Pending":
                return False, "Only pending leave applications can be cancelled."
            cursor.execute(
                "UPDATE leaves SET status = 'Cancelled', action_at = NOW() WHERE leave_id = %s",
                (leave_id,)
            )
        return True, ""
    except MySQLError as exc:
        return False, f"Database error: {exc}"
