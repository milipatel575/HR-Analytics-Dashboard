# Architecture — HR Analytics Dashboard

## Overview

This document explains the folder structure, the layered architecture,
and the data flow from the user's browser to the MySQL database.

---

## Folder Structure & Rationale

```
HR-Analytics-Dashboard/
├── app/
│   └── main.py
├── database/
│   ├── connection.py
│   └── queries.py
├── modules/
│   ├── employee.py
│   ├── attendance.py
│   ├── leave.py
│   ├── payroll.py
│   └── analytics.py
├── ui/
│   └── pages/
│       ├── employee_page.py
│       ├── attendance_page.py
│       ├── leave_page.py
│       ├── payroll_page.py
│       └── analytics_page.py
├── sql/
│   ├── schema.sql
│   └── sample_data.sql
└── utils/
    ├── validators.py
    └── formatters.py
```

### Why this separation?

| Layer | Package | Rule |
|---|---|---|
| **Presentation** | `ui/pages/` | Only imports `modules/` and `utils/`. No direct SQL calls. |
| **Business Logic** | `modules/` | No `streamlit` imports. Can be tested independently. |
| **Data Access** | `database/` | Only layer that knows about MySQL. Uses parameterized queries exclusively. |
| **Utilities** | `utils/` | Pure Python helpers, no side effects. |
| **SQL** | `sql/` | All DDL and seed data in one place for easy DB reset. |
| **Entry point** | `app/main.py` | Sets `sys.path`, configures Streamlit page, applies global CSS, and routes to pages. |

---

## Three-Layer Architecture

```
┌─────────────────────────────────────────────────┐
│              Browser (Streamlit UI)             │
│                 ui/pages/*.py                   │
│  - Renders widgets, forms, charts               │
│  - Collects user input                          │
│  - Calls module functions                       │
└─────────────────────┬───────────────────────────┘
                      │  function call (Python)
                      ▼
┌─────────────────────────────────────────────────┐
│            Business Logic Layer                 │
│               modules/*.py                      │
│  - Input validation (delegates to utils/)       │
│  - Workflow logic (e.g. leave approval deducts  │
│    balance atomically)                          │
│  - Calls database layer with query constants    │
└─────────────────────┬───────────────────────────┘
                      │  parameterized SQL
                      ▼
┌─────────────────────────────────────────────────┐
│              Data Access Layer                  │
│   database/connection.py + database/queries.py  │
│  - DBConnection context manager                 │
│  - execute_query(), call_procedure()            │
│  - All SQL is %s-parameterized constants        │
└─────────────────────┬───────────────────────────┘
                      │  TCP
                      ▼
              ┌───────────────┐
              │  MySQL 8.0+   │
              │  hr_analytics │
              └───────────────┘
```

---

## Database Schema (Entity Relationships)

```
departments ──────┐
                  │ 1:N
designations ─────┼──► employees ──────┐
                                       │ 1:N ──► attendance
                                       │ 1:N ──► leaves ──► leave_types
                                       │ 1:N ──► leave_balances
                                       │ 1:N ──► payroll ──► payroll_details ──► payroll_components
```

### Normalisation Choices

| Table | NF achieved | Key decision |
|---|---|---|
| `employees` | 3NF | dept/desig stored as FK, not text — avoids update anomalies |
| `payroll_components` | 3NF | Component names/values live in their own table — adding HRA increase is one row UPDATE |
| `leave_balances` | 3NF | Per-employee, per-type, per-year — avoids NULL columns for unused leave types |
| `payroll_details` | 3NF | Line items separate from header — mimics real accounting double-entry pattern |

---

## Key Design Decisions

### 1. All SQL in `database/queries.py`
Every SQL statement is a named string constant with `%s` placeholders.
No module file ever builds a query string from user input.
This is the single most important security decision — it makes SQL injection structurally impossible.

### 2. Context Manager (`DBConnection`)
```python
with DBConnection() as conn:
    cursor = conn.cursor(dictionary=True)
    cursor.execute(SQL_CONSTANT, (param,))
```
The `__exit__` method commits on success and rolls back on any exception,
ensuring the database is never left in an inconsistent state.

### 3. Views instead of repeated JOINs
`v_employee_full_details` joins `employees`, `departments`, and `designations`.
Every screen that lists employees queries this view — the JOIN is defined once
in the database, not repeated in Python code.

### 4. Stored Procedure for Payroll
`sp_generate_payroll` runs inside a transaction in the MySQL engine.
Even if the Python process dies mid-execution, the database ROLLBACK ensures
no partial payroll record is ever committed.

### 5. Separation of `modules/` from `ui/`
Module functions return plain Python objects (dicts, DataFrames, tuples).
They have zero knowledge of Streamlit. This means they can be called from
a CLI script, a REST API, or unit tests — without starting a browser.

---

## Data Flow: Marking Attendance

```
1. User picks a date and selects "Present" for employee EMP005
2. ui/pages/attendance_page.py calls:
       mark_attendance(emp_id, date, "Present")
3. modules/attendance.py calls:
       execute_query(Q.ATT_MARK, (emp_id, date, "Present", None, None, None), fetch="none")
4. database/connection.py opens a DBConnection, executes:
       INSERT INTO attendance (...) VALUES (%s, %s, %s, %s, %s, %s)
       ON DUPLICATE KEY UPDATE status = VALUES(status)
5. DBConnection.__exit__ commits the transaction
6. Python returns (True, "") → Streamlit shows "Saved ✓"
```

---

## Data Flow: Leave Approval

```
1. HR clicks "Approve" on a pending leave (leave_id = 7)
2. leave_page.py calls update_leave_status(7, "Approved", approver_id=9)
3. modules/leave.py:
   a. Opens a single DBConnection (one transaction)
   b. Fetches leave details (employee_id, leave_type_id, total_days, start_date)
   c. Executes LEAVE_UPDATE_STATUS → sets status='Approved', approved_by=9, action_at=NOW()
   d. Executes LEAVE_BALANCE_UPDATE_USED → used_days += total_days
   e. DBConnection commits both updates atomically
4. If either step fails, both roll back — balance is never decremented for a rejected leave
```
