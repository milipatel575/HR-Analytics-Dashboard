"""
app/main.py
-----------
Streamlit entry point for the HR Analytics & Employee Management Dashboard.

Run with:
    streamlit run app/main.py

The app uses a sidebar navigation menu to route between five pages.
sys.path is patched so that all sibling packages (database/, modules/, ui/)
are importable from the project root.
"""

import sys
import os

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so all packages resolve correctly
# regardless of where streamlit is launched from.
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

# ---- Page configuration (must be first Streamlit call) --------------------
st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Global CSS -----------------------------------------------------------
st.markdown(
    """
    <style>
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar Styling ── */
    [data-testid="stSidebar"] {
        background: #0F172A !important;
        border-right: none;
    }
    
    [data-testid="stSidebar"] * {
        color: #F8FAFC;
    }
    
    [data-testid="stSidebarNav"] a {
        color: #94A3B8 !important;
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.2s ease-in-out;
    }
    
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #FFFFFF !important;
    }

    [aria-selected="true"][data-testid="stSidebarNav"] a {
        background: #4F46E5 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }

    /* ── Metric Cards ── */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05), 0 8px 10px -6px rgba(0,0,0,0.01);
        border-color: #CBD5E1;
    }
    
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-weight: 600 !important;
        font-size: 0.9rem;
    }
    
    [data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 700 !important;
    }

    /* ── General Component Styling (Buttons, DataFrames, Inputs) ── */
    .stButton > button[kind="primary"] {
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
        transform: translateY(-1px);
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* ── Expander ── */
    [data-testid="stExpander"] {
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        background: #FFFFFF;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

    /* ── Divider ── */
    hr { border-color: #E2E8F0 !important; margin: 2rem 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Import page modules --------------------------------------------------
from ui.pages import (
    employee_page,
    attendance_page,
    leave_page,
    payroll_page,
    analytics_page,
)

# ---- Navigation -----------------------------------------------------------
PAGES = {
    "📊 HR Analytics":        analytics_page,
    "👥 Employee Management": employee_page,
    "📅 Attendance Tracking": attendance_page,
    "🗓️ Leave Management":    leave_page,
    "💰 Payroll Management":  payroll_page,
}

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 20px 0 10px 0;">
            <div style="font-size:2.5rem;">⚡</div>
            <h2 style="color:#FFFFFF; margin:4px 0; font-size:1.1rem; font-weight:700;">
                HR Analytics
            </h2>
            <p style="color:#94A3B8; font-size:0.75rem; margin:0;">
                Employee Management Dashboard
            </p>
        </div>
        <hr style="border-color:#1E293B; margin: 12px 0;">
        """,
        unsafe_allow_html=True,
    )

    selected_page = st.radio(
        "Navigation",
        list(PAGES.keys()),
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <hr style="border-color:#1E293B; margin: 12px 0;">
        <p style="color:#94A3B8; font-size:0.72rem; text-align:center;">
            Built with Python · Streamlit · MySQL<br>
            © 2026 Internship Project
        </p>
        """,
        unsafe_allow_html=True,
    )

# ---- Render selected page -------------------------------------------------
PAGES[selected_page].render()
