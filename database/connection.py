"""
database/connection.py
----------------------
Provides a thread-safe MySQLConnection class that manages
connection lifecycle using Python's context manager protocol.

All callers should use:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(SQL_CONSTANT, (param1, param2))
            ...

Environment variables read from .env via python-dotenv:
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
"""

import os
import mysql.connector
from mysql.connector import Error as MySQLError
from dotenv import load_dotenv
import streamlit as st

# Load .env once at import time
load_dotenv()


def get_connection() -> mysql.connector.MySQLConnection:
    """
    Create and return a new MySQL connection using credentials
    stored in environment variables.

    Returns
    -------
    mysql.connector.MySQLConnection
        An open, auto-commit disabled connection.

    Raises
    ------
    MySQLError
        If the connection cannot be established (wrong credentials,
        server down, etc.). The error is also surfaced to the
        Streamlit UI via st.error().
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "hr_analytics"),
            charset="utf8mb4",
            autocommit=False,
            connection_timeout=10,
        )
        return conn
    except MySQLError as exc:
        st.error(
            f"❌ **Database connection failed:** {exc}\n\n"
            "Please check your `.env` file and ensure MySQL is running."
        )
        raise


class DBConnection:
    """
    Context manager wrapper around mysql.connector.MySQLConnection.

    Usage
    -----
    with DBConnection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(SOME_QUERY, (param,))
        rows = cursor.fetchall()
    """

    def __init__(self):
        self._conn: mysql.connector.MySQLConnection | None = None

    def __enter__(self) -> mysql.connector.MySQLConnection:
        """Open the connection and return it."""
        self._conn = get_connection()
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Commit on success, rollback on exception, then close.

        Returns False so that any exception propagates to the caller.
        """
        if self._conn and self._conn.is_connected():
            if exc_type is None:
                self._conn.commit()
            else:
                self._conn.rollback()
            self._conn.close()
        return False  # do not suppress exceptions


def execute_query(sql: str, params: tuple = (), fetch: str = "all") -> list | dict | None:
    """
    Execute a parameterized SQL statement inside a managed connection.

    Parameters
    ----------
    sql : str
        The SQL statement with %s placeholders (never f-strings with user data).
    params : tuple
        Values to bind to the %s placeholders.
    fetch : str
        'all'  → fetchall() → list of dicts
        'one'  → fetchone() → dict or None
        'none' → no fetch (INSERT/UPDATE/DELETE)

    Returns
    -------
    list | dict | None
        Query results for SELECT; None for DML statements.

    Raises
    ------
    MySQLError
        Re-raised after rolling back and showing a Streamlit error.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, params)
            if fetch == "all":
                return cursor.fetchall()
            elif fetch == "one":
                return cursor.fetchone()
            else:
                return None
    except MySQLError as exc:
        st.error(f"❌ **Database error:** {exc}")
        raise


def call_procedure(proc_name: str, args: tuple = ()) -> None:
    """
    Call a MySQL stored procedure with the given arguments.

    Parameters
    ----------
    proc_name : str
        Name of the stored procedure.
    args : tuple
        Positional arguments for the procedure.

    Raises
    ------
    MySQLError
        Re-raised after rollback and Streamlit error display.
    """
    try:
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.callproc(proc_name, args)
    except MySQLError as exc:
        st.error(f"❌ **Procedure error ({proc_name}):** {exc}")
        raise
