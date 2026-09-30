# HR Analytics & Employee Management Dashboard

> **Internship Project** | Python · Streamlit · MySQL · Pandas · Plotly

A full-featured HR Analytics dashboard covering Employee Management, Attendance Tracking, Leave Management, Payroll Processing, and interactive analytics — built as a production-quality Python internship project.

---

## ✨ Features

| Module | Key Capabilities |
|---|---|
| 👥 **Employee Management** | Add / Edit / Delete employees, search by name/code/email, filter by department and status |
| 📅 **Attendance Tracking** | Daily marking (Present/Absent/WFH/Half-Day/Holiday), bulk-mark, monthly % summary, 90-day history |
| 🗓️ **Leave Management** | Apply for leave with balance check, Approve/Reject workflow, leave history, balance tracker |
| 💰 **Payroll Management** | Auto-generate payroll via stored procedure, styled payslip view, bulk payroll, monthly register |
| 📊 **HR Analytics** | KPI cards, department headcount chart, attendance trend, salary distribution, payroll trend — all Plotly |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Frontend | Streamlit 1.35 |
| Database | MySQL 8.0+ |
| Data handling | Pandas 2.2 |
| Charts | Plotly 5.22 |
| Config | python-dotenv |

---

## 🚀 Quick Setup

### 1. Clone the repository
```bash
git clone <repo-url>
cd HR-Analytics-Dashboard
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
copy .env.example .env   # Windows
# or: cp .env.example .env  (Linux/macOS)
```
Edit `.env` and set your MySQL credentials:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=hr_analytics
```

### 5. Set up the MySQL database
```bash
mysql -u root -p < sql/schema.sql
mysql -u root -p < sql/sample_data.sql
```

### 6. Run the app
```bash
streamlit run app/main.py
```
Open your browser at **http://localhost:8501**

---

## 📁 Project Structure

```
HR-Analytics-Dashboard/
├── app/main.py              ← Streamlit entry point
├── database/
│   ├── connection.py        ← DB connection manager
│   └── queries.py           ← All SQL constants
├── modules/
│   ├── employee.py          ← Employee CRUD logic
│   ├── attendance.py        ← Attendance logic
│   ├── leave.py             ← Leave workflow logic
│   ├── payroll.py           ← Payroll generation logic
│   └── analytics.py        ← Analytics data aggregation
├── ui/pages/
│   ├── employee_page.py     ← Employee UI
│   ├── attendance_page.py   ← Attendance UI
│   ├── leave_page.py        ← Leave UI
│   ├── payroll_page.py      ← Payroll UI
│   └── analytics_page.py   ← Dashboard UI
├── sql/
│   ├── schema.sql           ← DDL: tables, views, stored procedure
│   └── sample_data.sql      ← 40 employees + realistic seed data
├── utils/
│   ├── validators.py        ← Input validation
│   └── formatters.py        ← Display formatting
├── .env.example
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
```

---

## 🔒 Security Notes

- **No SQL injection risk**: All database calls use parameterized queries (`%s` placeholders). User-supplied data is never interpolated into SQL strings.
- **No hardcoded credentials**: All DB credentials are read from `.env` via `python-dotenv`. The `.env` file is in `.gitignore`.
- **Input validation**: Every form validates inputs before touching the database (name format, email, phone, salary range, date logic).

---

## 🗄️ Database Highlights

- **10 normalized tables** (3NF) with proper foreign keys, CHECK constraints, and compound indexes.
- **2 Views**: `v_employee_full_details` and `v_monthly_attendance_summary` — avoid repeated JOINs in application code.
- **1 Stored Procedure**: `sp_generate_payroll` — atomic payroll generation with prorating and ROLLBACK on error.

---

## 📋 Sample Data

The `sql/sample_data.sql` file seeds:
- 8 departments, 18 designations
- **40 employees** across all departments
- 2 months of attendance data (May & June 2026)
- 15 leave applications in various statuses
- May 2026 payroll with line-item details

---

## 📚 Documentation

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — Folder structure and data flow explanation

