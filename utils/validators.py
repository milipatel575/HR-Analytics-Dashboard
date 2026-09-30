"""
utils/validators.py
-------------------
Input validation helpers used across all Streamlit pages.

Every public function returns a (bool, str) tuple:
    (True, "")          → valid input
    (False, "message")  → invalid, with a human-readable error message

No database calls are made here — pure Python validation.
"""

import re
from datetime import date


# ---------------------------------------------------------------------------
# String helpers
# ---------------------------------------------------------------------------

def validate_name(value: str, field_name: str = "Name") -> tuple[bool, str]:
    """
    Validate a person's name or a text label.

    Rules
    -----
    - Must not be blank or whitespace-only.
    - Must be between 2 and 100 characters.
    - May contain letters, spaces, hyphens, apostrophes, and dots.
    """
    value = value.strip()
    if not value:
        return False, f"{field_name} cannot be empty."
    if len(value) < 2:
        return False, f"{field_name} must be at least 2 characters."
    if len(value) > 100:
        return False, f"{field_name} must be at most 100 characters."
    if not re.match(r"^[A-Za-z\s\-'\.]+$", value):
        return False, f"{field_name} may only contain letters, spaces, hyphens, apostrophes, and dots."
    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate an email address using a standard RFC-5321 pattern.
    """
    email = email.strip()
    if not email:
        return False, "Email cannot be empty."
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, f"'{email}' is not a valid email address."
    return True, ""


def validate_phone(phone: str) -> tuple[bool, str]:
    """
    Validate an Indian mobile/phone number.

    Accepts formats: 9876543210, +919876543210, 09876543210.
    Phone is optional — an empty string is considered valid.
    """
    phone = phone.strip()
    if not phone:
        return True, ""   # phone is optional
    pattern = r"^(\+91|0)?[6-9]\d{9}$"
    if not re.match(pattern, phone):
        return False, f"'{phone}' is not a valid Indian phone number (e.g. 9876543210)."
    return True, ""


# ---------------------------------------------------------------------------
# Numeric helpers
# ---------------------------------------------------------------------------

def validate_salary(salary: float, field_name: str = "Salary") -> tuple[bool, str]:
    """
    Validate a monetary salary value.

    Rules
    -----
    - Must be ≥ 0.
    - Must be ≤ 10,000,000 (1 crore) to catch data-entry errors.
    """
    if salary < 0:
        return False, f"{field_name} cannot be negative."
    if salary > 10_000_000:
        return False, f"{field_name} seems unrealistically high (> ₹1 crore). Please verify."
    return True, ""


def validate_positive_int(value: int, field_name: str = "Value") -> tuple[bool, str]:
    """Validate that an integer is strictly greater than zero."""
    if value <= 0:
        return False, f"{field_name} must be a positive integer."
    return True, ""


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def validate_joining_date(joining_date: date) -> tuple[bool, str]:
    """
    Validate an employee joining date.

    Rules
    -----
    - Must not be in the future (can't join tomorrow).
    - Must not be before 1990-01-01 (reasonable company founding year).
    """
    if joining_date > date.today():
        return False, "Joining date cannot be in the future."
    if joining_date.year < 1990:
        return False, "Joining date seems too far in the past (before 1990)."
    return True, ""


def validate_dob(dob: date) -> tuple[bool, str]:
    """
    Validate a date of birth.

    Rules
    -----
    - Employee must be at least 18 years old.
    - Must not be in the future.
    """
    if dob > date.today():
        return False, "Date of birth cannot be in the future."
    age = (date.today() - dob).days // 365
    if age < 18:
        return False, "Employee must be at least 18 years old."
    if age > 80:
        return False, "Date of birth seems unrealistic (age > 80). Please verify."
    return True, ""


def validate_date_range(start: date, end: date) -> tuple[bool, str]:
    """
    Validate that a start date is not after an end date.
    """
    if end < start:
        return False, "End date must be on or after the start date."
    return True, ""


def validate_leave_days(start: date, end: date) -> tuple[bool, str]:
    """
    Validate leave date range:
    - End must not be before start.
    - Maximum consecutive leave is 90 days.
    """
    ok, msg = validate_date_range(start, end)
    if not ok:
        return False, msg
    days = (end - start).days + 1
    if days > 90:
        return False, "Leave request cannot exceed 90 consecutive days."
    return True, ""


# ---------------------------------------------------------------------------
# Composite helper (used by employee forms)
# ---------------------------------------------------------------------------

def validate_employee_form(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    salary: float,
    joining_date: date,
    dob: date | None,
) -> list[str]:
    """
    Run all employee-form validations and return a list of error messages.

    An empty list means all fields are valid.

    Parameters
    ----------
    first_name, last_name : str
    email, phone          : str
    salary                : float
    joining_date          : date
    dob                   : date or None  (optional)

    Returns
    -------
    list[str]
        Zero or more human-readable error messages.
    """
    errors: list[str] = []

    checks = [
        validate_name(first_name, "First name"),
        validate_name(last_name, "Last name"),
        validate_email(email),
        validate_phone(phone),
        validate_salary(salary),
        validate_joining_date(joining_date),
    ]
    if dob is not None:
        checks.append(validate_dob(dob))

    for ok, msg in checks:
        if not ok:
            errors.append(msg)

    return errors
