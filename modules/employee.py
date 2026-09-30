"""
modules/employee.py
--------------------
Business logic for Employee Management.

All database calls use parameterized queries from database/queries.py.
No f-strings or string concatenation with user-supplied data.
"""

import pandas as pd
from mysql.connector import Error as MySQLError
from database.connection import DBConnection, execute_query
from database import queries as Q


# ---------------------------------------------------------------------------
# Auto-generate next employee code
# ---------------------------------------------------------------------------

def generate_emp_code() -> str:
    """
    Generate the next sequential employee code in the format EMP001.

    Reads the last inserted employee code, increments by 1, and
    returns the formatted string. Returns 'EMP001' for the very first employee.

    Returns
    -------
    str
        Next employee code, e.g. 'EMP042'.
    """
    try:
        row = execute_query(Q.EMP_GET_LAST_CODE, fetch="one")
        if row and row.get("emp_code"):
            last_num = int(row["emp_code"].replace("EMP", ""))
            return f"EMP{last_num + 1:03d}"
        return "EMP001"
    except (MySQLError, ValueError):
        return "EMP001"


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------

def get_all_employees() -> pd.DataFrame:
    """
    Fetch all employees from v_employee_full_details view.

    Returns
    -------
    pd.DataFrame
        All columns from the view; empty DataFrame on error.
    """
    try:
        rows = execute_query(Q.EMP_GET_ALL)
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def get_employee_by_id(employee_id: int) -> dict | None:
    """
    Fetch a single employee record by primary key.

    Parameters
    ----------
    employee_id : int

    Returns
    -------
    dict | None
        Row dict from the view, or None if not found / on error.
    """
    try:
        return execute_query(Q.EMP_GET_BY_ID, (employee_id,), fetch="one")
    except MySQLError:
        return None


def search_employees(query: str) -> pd.DataFrame:
    """
    Full-text search across name, emp_code, email, department, designation.

    Parameters
    ----------
    query : str
        Search term (wildcards added automatically).

    Returns
    -------
    pd.DataFrame
    """
    try:
        like = f"%{query}%"
        rows = execute_query(Q.EMP_SEARCH, (like, like, like, like, like))
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def filter_employees(department_id: int | None = None, status: str | None = None) -> pd.DataFrame:
    """
    Filter employees by department or status.

    Parameters
    ----------
    department_id : int | None  – filter by department if provided
    status        : str | None  – filter by status if provided

    Returns
    -------
    pd.DataFrame
    """
    try:
        if department_id:
            rows = execute_query(Q.EMP_FILTER_BY_DEPT, (department_id,))
        elif status:
            rows = execute_query(Q.EMP_FILTER_BY_STATUS, (status,))
        else:
            rows = execute_query(Q.EMP_GET_ALL)
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def get_departments() -> list[dict]:
    """
    Fetch all departments as a list of dicts (department_id, department_name).

    Returns
    -------
    list[dict]
    """
    try:
        return execute_query(Q.DEPT_GET_ALL) or []
    except MySQLError:
        return []


def get_designations() -> list[dict]:
    """
    Fetch all designations as a list of dicts (designation_id, title, grade).

    Returns
    -------
    list[dict]
    """
    try:
        return execute_query(Q.DESIG_GET_ALL) or []
    except MySQLError:
        return []


# ---------------------------------------------------------------------------
# Write operations
# ---------------------------------------------------------------------------

def add_employee(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    department_id: int,
    designation_id: int,
    joining_date,
    date_of_birth,
    basic_salary: float,
    status: str,
) -> tuple[bool, str]:
    """
    Insert a new employee record.

    Generates the emp_code automatically. Initialises leave balances
    for the current year for the new employee.

    Parameters
    ----------
    first_name, last_name : str
    email, phone          : str
    department_id         : int
    designation_id        : int
    joining_date          : date
    date_of_birth         : date | None
    basic_salary          : float
    status                : str

    Returns
    -------
    (True, emp_code)   on success
    (False, message)   on failure
    """
    emp_code = generate_emp_code()
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(Q.EMP_INSERT, (
                emp_code, first_name.strip(), last_name.strip(),
                email.strip(), phone.strip(),
                department_id, designation_id,
                joining_date, date_of_birth,
                basic_salary, status,
            ))
            new_id = cursor.lastrowid
            # Initialise leave balances for current year
            import datetime
            year = datetime.date.today().year
            cursor.execute(Q.LEAVE_INIT_BALANCES_FOR_EMP, (new_id, year))
        return True, emp_code
    except MySQLError as exc:
        if exc.errno == 1062:   # Duplicate entry
            return False, "An employee with this email already exists."
        return False, f"Database error: {exc}"


def update_employee(
    employee_id: int,
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    department_id: int,
    designation_id: int,
    joining_date,
    date_of_birth,
    basic_salary: float,
    status: str,
) -> tuple[bool, str]:
    """
    Update an existing employee record.

    Returns
    -------
    (True, "")       on success
    (False, message) on failure
    """
    try:
        execute_query(Q.EMP_UPDATE, (
            first_name.strip(), last_name.strip(),
            email.strip(), phone.strip(),
            department_id, designation_id,
            joining_date, date_of_birth,
            basic_salary, status,
            employee_id,
        ), fetch="none")
        return True, ""
    except MySQLError as exc:
        if exc.errno == 1062:
            return False, "Another employee with this email already exists."
        return False, f"Database error: {exc}"


def delete_employee(employee_id: int) -> tuple[bool, str]:
    """
    Delete an employee record (cascades to attendance, leaves, payroll).

    Parameters
    ----------
    employee_id : int

    Returns
    -------
    (True, "")       on success
    (False, message) on failure
    """
    try:
        execute_query(Q.EMP_DELETE, (employee_id,), fetch="none")
        return True, ""
    except MySQLError as exc:
        return False, f"Cannot delete employee: {exc}"


# ---------------------------------------------------------------------------
# Stats helpers (used by analytics module)
# ---------------------------------------------------------------------------

def get_headcount() -> int:
    """Return the number of currently active employees."""
    try:
        row = execute_query(Q.KPI_HEADCOUNT, fetch="one")
        return int(row["total"]) if row else 0
    except MySQLError:
        return 0


def get_attrition_rate() -> float:
    """Return attrition rate as a percentage (0–100)."""
    try:
        row = execute_query(Q.KPI_ATTRITION_RATE, fetch="one")
        return float(row["attrition_rate"] or 0) if row else 0.0
    except MySQLError:
        return 0.0


def get_avg_salary() -> float:
    """Return average basic salary of active employees."""
    try:
        row = execute_query(Q.EMP_AVG_SALARY, fetch="one")
        return float(row["avg_salary"] or 0) if row else 0.0
    except MySQLError:
        return 0.0


def get_avg_tenure() -> float:
    """Return average tenure in years of active employees."""
    try:
        row = execute_query(Q.EMP_AVG_TENURE, fetch="one")
        return float(row["avg_tenure"] or 0) if row else 0.0
    except MySQLError:
        return 0.0


def get_dept_headcount() -> pd.DataFrame:
    """Return department-wise headcount for active employees."""
    try:
        rows = execute_query(Q.EMP_COUNT_BY_DEPT)
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()


def get_salary_distribution() -> pd.DataFrame:
    """Return salary band distribution of active employees."""
    try:
        rows = execute_query(Q.EMP_SALARY_DISTRIBUTION)
        return pd.DataFrame(rows or [])
    except MySQLError:
        return pd.DataFrame()
