"""
utils/formatters.py
-------------------
Display-layer formatting utilities.

These functions are pure (no side effects, no DB calls) and are
imported by Streamlit page modules to render values consistently.
"""

from datetime import date, datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Currency
# ---------------------------------------------------------------------------

def format_inr(amount: float | None, show_symbol: bool = True) -> str:
    """
    Format a numeric value as Indian Rupees with comma grouping.

    Parameters
    ----------
    amount      : float or None
    show_symbol : bool  – prepend '₹' when True (default)

    Returns
    -------
    str
        e.g. format_inr(125000.50) → '₹1,25,000.50'
             format_inr(None)      → '—'
    """
    if amount is None:
        return "—"
    # Indian comma grouping: last 3 digits, then every 2
    amount = float(amount)
    integer_part, _, decimal_part = f"{amount:.2f}".partition(".")
    s = integer_part
    if len(s) > 3:
        last3 = s[-3:]
        rest  = s[:-3]
        rest  = ",".join(
            [rest[max(0, i-2):i] for i in range(len(rest), 0, -2)][::-1]
        )
        s = rest + "," + last3
    result = f"{s}.{decimal_part}"
    return f"₹{result}" if show_symbol else result


# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------

def format_date(d: Optional[date]) -> str:
    """
    Format a date object as 'DD Mon YYYY'.

    Returns '—' for None values.
    """
    if d is None:
        return "—"
    return d.strftime("%d %b %Y")


def format_datetime(dt: Optional[datetime]) -> str:
    """
    Format a datetime object as 'DD Mon YYYY HH:MM'.

    Returns '—' for None values.
    """
    if dt is None:
        return "—"
    return dt.strftime("%d %b %Y %H:%M")


def days_since(d: date) -> int:
    """Return the number of days elapsed since the given date."""
    return (date.today() - d).days


def tenure_string(joining_date: date) -> str:
    """
    Compute a human-readable tenure string from a joining date.

    e.g. '3 years, 4 months'
    """
    total_months = (date.today().year - joining_date.year) * 12 + \
                   (date.today().month - joining_date.month)
    years, months = divmod(total_months, 12)
    parts = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    return ", ".join(parts) if parts else "< 1 month"


# ---------------------------------------------------------------------------
# Status badges (returns HTML string for st.markdown use)
# ---------------------------------------------------------------------------

STATUS_COLORS = {
    # Employee status
    "Active":      ("#06b6d4", "#083344"), # Cyan
    "Inactive":    ("#a855f7", "#3b0764"), # Purple
    "Resigned":    ("#52525b", "#fafafa"), # Gray
    "Terminated":  ("#ec4899", "#500724"), # Pink
    # Leave status
    "Pending":     ("#a855f7", "#3b0764"), # Purple
    "Approved":    ("#06b6d4", "#083344"), # Cyan
    "Rejected":    ("#ec4899", "#500724"), # Pink
    "Cancelled":   ("#52525b", "#fafafa"), # Gray
    # Attendance status
    "Present":     ("#06b6d4", "#083344"), # Cyan
    "Absent":      ("#ec4899", "#500724"), # Pink
    "Half-Day":    ("#a855f7", "#3b0764"), # Purple
    "WFH":         ("#8b5cf6", "#2e1065"), # Violet
    "Holiday":     ("#f43f5e", "#4c0519"), # Rose
}


def status_badge(status: str) -> str:
    """
    Return an inline HTML badge <span> for the given status string.

    Parameters
    ----------
    status : str  e.g. 'Active', 'Pending', 'Present'

    Returns
    -------
    str  — HTML string, safe to use in st.markdown(..., unsafe_allow_html=True)
    """
    bg, fg = STATUS_COLORS.get(status, ("#f3f4f6", "#18181b"))
    return (
        f'<span style="background:{bg}; color:{fg}; padding:2px 10px; '
        f'border-radius:99px; font-size:0.78rem; font-weight:600;">'
        f'{status}</span>'
    )


# ---------------------------------------------------------------------------
# Attendance percentage
# ---------------------------------------------------------------------------

def attendance_pct_color(pct: float) -> str:
    """
    Return a hex color representing attendance quality.

    ≥ 90 → green, 75–89 → amber, < 75 → red
    """
    if pct is None:
        return "#a1a1aa" # Gray
    if pct >= 90:
        return "#06b6d4" # Cyan (Good)
    if pct >= 75:
        return "#a855f7" # Purple (Average)
    return "#ec4899" # Pink (Poor)


def month_name(month_num: int) -> str:
    """Convert a month number (1-12) to its abbreviated name."""
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    if 1 <= month_num <= 12:
        return months[month_num - 1]
    return str(month_num)
