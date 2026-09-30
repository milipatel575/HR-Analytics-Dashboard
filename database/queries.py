"""
database/queries.py
-------------------
Central repository of ALL SQL statements used by the application.

Rules enforced here:
  1. Every constant is a plain string with %s placeholders — NEVER f-strings
     or string concatenation using user-supplied data.
  2. Module files import these constants and pass params as tuples to
     cursor.execute(SQL, (p1, p2, ...)) — guaranteeing no SQL injection.
  3. Column names used in ORDER BY / GROUP BY are hard-coded here, not
     passed from the UI, so there is no injection vector there either.
"""

# ===========================================================
# DEPARTMENT QUERIES
# ===========================================================

DEPT_GET_ALL = """
    SELECT department_id, department_name
    FROM   departments
    ORDER BY department_name
"""

DEPT_INSERT = """
    INSERT INTO departments (department_name)
    VALUES (%s)
"""

# ===========================================================
# DESIGNATION QUERIES
# ===========================================================

DESIG_GET_ALL = """
    SELECT designation_id, title, grade
    FROM   designations
    ORDER BY grade, title
"""

DESIG_INSERT = """
    INSERT INTO designations (title, grade)
    VALUES (%s, %s)
"""

# ===========================================================
# EMPLOYEE QUERIES
# ===========================================================

EMP_GET_ALL = """
    SELECT *
    FROM   v_employee_full_details
    ORDER BY emp_code
"""

EMP_GET_BY_ID = """
    SELECT *
    FROM   v_employee_full_details
    WHERE  employee_id = %s
"""

EMP_SEARCH = """
    SELECT *
    FROM   v_employee_full_details
    WHERE  (full_name       LIKE %s
         OR emp_code        LIKE %s
         OR email           LIKE %s
         OR department_name LIKE %s
         OR designation     LIKE %s)
    ORDER BY emp_code
"""

EMP_FILTER_BY_DEPT = """
    SELECT *
    FROM   v_employee_full_details
    WHERE  department_id = %s
    ORDER BY emp_code
"""

EMP_FILTER_BY_STATUS = """
    SELECT *
    FROM   v_employee_full_details
    WHERE  status = %s
    ORDER BY emp_code
"""

EMP_INSERT = """
    INSERT INTO employees
        (emp_code, first_name, last_name, email, phone,
         department_id, designation_id, joining_date, date_of_birth,
         basic_salary, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

EMP_UPDATE = """
    UPDATE employees
    SET    first_name     = %s,
           last_name      = %s,
           email          = %s,
           phone          = %s,
           department_id  = %s,
           designation_id = %s,
           joining_date   = %s,
           date_of_birth  = %s,
           basic_salary   = %s,
           status         = %s
    WHERE  employee_id = %s
"""

EMP_DELETE = """
    DELETE FROM employees
    WHERE  employee_id = %s
"""

EMP_GET_LAST_CODE = """
    SELECT emp_code
    FROM   employees
    ORDER BY employee_id DESC
    LIMIT  1
"""

EMP_COUNT_BY_STATUS = """
    SELECT status, COUNT(*) AS count
    FROM   employees
    GROUP BY status
"""

EMP_COUNT_BY_DEPT = """
    SELECT d.department_name, COUNT(e.employee_id) AS headcount
    FROM   departments d
    LEFT JOIN employees e ON e.department_id = d.department_id
                          AND e.status = 'Active'
    GROUP BY d.department_id, d.department_name
    ORDER BY headcount DESC
"""

EMP_AVG_SALARY = """
    SELECT ROUND(AVG(basic_salary), 2) AS avg_salary
    FROM   employees
    WHERE  status = 'Active'
"""

EMP_AVG_TENURE = """
    SELECT ROUND(AVG(TIMESTAMPDIFF(YEAR, joining_date, CURDATE())), 1) AS avg_tenure
    FROM   employees
    WHERE  status = 'Active'
"""

EMP_SALARY_DISTRIBUTION = """
    SELECT
        CASE
            WHEN basic_salary <  30000                     THEN 'Below 30K'
            WHEN basic_salary BETWEEN 30000  AND  59999   THEN '30K–60K'
            WHEN basic_salary BETWEEN 60000  AND  89999   THEN '60K–90K'
            WHEN basic_salary BETWEEN 90000  AND 119999   THEN '90K–120K'
            ELSE '120K+'
        END AS salary_band,
        COUNT(*) AS count
    FROM employees
    WHERE status = 'Active'
    GROUP BY salary_band
    ORDER BY MIN(basic_salary)
"""

# ===========================================================
# ATTENDANCE QUERIES
# ===========================================================

ATT_MARK = """
    INSERT INTO attendance (employee_id, attendance_date, status, check_in, check_out, remarks)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        status    = VALUES(status),
        check_in  = VALUES(check_in),
        check_out = VALUES(check_out),
        remarks   = VALUES(remarks)
"""

ATT_GET_BY_DATE = """
    SELECT
        a.attendance_id,
        a.employee_id,
        v.emp_code,
        v.full_name,
        v.department_name,
        a.attendance_date,
        a.status,
        a.check_in,
        a.check_out,
        a.remarks
    FROM attendance a
    JOIN v_employee_full_details v ON v.employee_id = a.employee_id
    WHERE a.attendance_date = %s
    ORDER BY v.emp_code
"""

ATT_GET_BY_EMP_MONTH = """
    SELECT *
    FROM   v_monthly_attendance_summary
    WHERE  employee_id = %s
      AND  month       = %s
      AND  year        = %s
"""

ATT_MONTHLY_SUMMARY_ALL = """
    SELECT *
    FROM   v_monthly_attendance_summary
    WHERE  month = %s AND year = %s
    ORDER BY attendance_pct DESC
"""

ATT_TREND = """
    SELECT
        year,
        month,
        ROUND(AVG(attendance_pct), 2) AS avg_attendance_pct
    FROM   v_monthly_attendance_summary
    GROUP BY year, month
    ORDER BY year, month
"""

ATT_GET_EMP_DATE = """
    SELECT *
    FROM   attendance
    WHERE  employee_id     = %s
      AND  attendance_date = %s
"""

ATT_HISTORY_BY_EMP = """
    SELECT
        a.attendance_date,
        a.status,
        a.check_in,
        a.check_out,
        a.remarks
    FROM   attendance a
    WHERE  a.employee_id = %s
    ORDER BY a.attendance_date DESC
    LIMIT  90
"""

# ===========================================================
# LEAVE QUERIES
# ===========================================================

LEAVE_TYPES_ALL = """
    SELECT leave_type_id, type_name, annual_quota, is_paid
    FROM   leave_types
    ORDER BY type_name
"""

LEAVE_BALANCE_BY_EMP = """
    SELECT
        lb.balance_id,
        lb.employee_id,
        lb.leave_type_id,
        lt.type_name,
        lt.is_paid,
        lb.year,
        lb.total_days,
        lb.used_days,
        (lb.total_days - lb.used_days) AS remaining_days
    FROM leave_balances lb
    JOIN leave_types lt
        ON lt.leave_type_id = lb.leave_type_id
    WHERE lb.employee_id = %s
      AND lb.year = %s
    ORDER BY lt.type_name
"""

LEAVE_APPLY = """
    INSERT INTO leaves
        (employee_id, leave_type_id, start_date, end_date, total_days, reason, status)
    VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
"""

LEAVE_GET_ALL = """
    SELECT
        l.leave_id,
        v.emp_code,
        v.full_name,
        v.department_name,
        lt.type_name,
        l.start_date,
        l.end_date,
        l.total_days,
        l.reason,
        l.status,
        CONCAT(ap.first_name, ' ', ap.last_name) AS approved_by_name,
        l.applied_at,
        l.action_at
    FROM   leaves   l
    JOIN   v_employee_full_details v  ON v.employee_id   = l.employee_id
    JOIN   leave_types             lt ON lt.leave_type_id = l.leave_type_id
    LEFT JOIN employees            ap ON ap.employee_id   = l.approved_by
    ORDER BY l.applied_at DESC
"""

LEAVE_GET_PENDING = """
    SELECT
        l.leave_id,
        v.emp_code,
        v.full_name,
        v.department_name,
        lt.type_name,
        l.start_date,
        l.end_date,
        l.total_days,
        l.reason,
        l.status,
        l.applied_at
    FROM   leaves l
    JOIN   v_employee_full_details v  ON v.employee_id   = l.employee_id
    JOIN   leave_types             lt ON lt.leave_type_id = l.leave_type_id
    WHERE  l.status = 'Pending'
    ORDER BY l.applied_at
"""

LEAVE_GET_BY_EMP = """
    SELECT
        l.leave_id,
        lt.type_name,
        l.start_date,
        l.end_date,
        l.total_days,
        l.reason,
        l.status,
        l.applied_at,
        l.action_at
    FROM   leaves      l
    JOIN   leave_types lt ON lt.leave_type_id = l.leave_type_id
    WHERE  l.employee_id = %s
    ORDER BY l.applied_at DESC
"""

LEAVE_UPDATE_STATUS = """
    UPDATE leaves
    SET    status      = %s,
           approved_by = %s,
           action_at   = NOW()
    WHERE  leave_id    = %s
"""

LEAVE_BALANCE_UPDATE_USED = """
    UPDATE leave_balances
    SET    used_days = used_days + %s
    WHERE  employee_id   = %s
      AND  leave_type_id = %s
      AND  year          = %s
"""

LEAVE_GET_TYPE_FOR_APPLICATION = """
    SELECT leave_type_id
    FROM   leaves
    WHERE  leave_id = %s
"""

LEAVE_INIT_BALANCES_FOR_EMP = """
    INSERT INTO leave_balances (employee_id, leave_type_id, year, total_days, used_days)
    SELECT %s, leave_type_id, %s, annual_quota, 0
    FROM   leave_types
    ON DUPLICATE KEY UPDATE total_days = total_days
"""

# ===========================================================
# PAYROLL QUERIES
# ===========================================================

PAYROLL_GET_BY_MONTH = """
    SELECT
        p.payroll_id,
        p.employee_id,
        v.emp_code,
        v.full_name,
        v.department_name,
        v.designation,
        p.month,
        p.year,
        p.basic_salary,
        p.total_allowances,
        p.total_deductions,
        p.net_salary,
        p.working_days,
        p.present_days,
        p.payslip_generated,
        p.generated_at
    FROM payroll p
    JOIN v_employee_full_details v
        ON v.employee_id = p.employee_id
    WHERE p.month = %s
    AND p.year = %s
    ORDER BY v.emp_code
"""

PAYROLL_GET_BY_EMP = """
    SELECT
        p.payroll_id,
        p.month,
        p.year,
        p.basic_salary,
        p.total_allowances,
        p.total_deductions,
        p.net_salary,
        p.working_days,
        p.present_days,
        p.payslip_generated,
        p.generated_at
    FROM   payroll p
    WHERE  p.employee_id = %s
    ORDER BY p.year DESC, p.month DESC
"""

PAYROLL_GET_DETAILS = """
    SELECT
        pc.name      AS component_name,
        pc.type      AS component_type,
        pd.amount
    FROM   payroll_details pd
    JOIN   payroll_components pc ON pc.component_id = pd.component_id
    WHERE  pd.payroll_id = %s
    ORDER BY pc.type, pc.name
"""

PAYROLL_MARK_GENERATED = """
    UPDATE payroll
    SET    payslip_generated = TRUE,
           generated_at      = NOW()
    WHERE  payroll_id = %s
"""

PAYROLL_COMPONENTS_ALL = """
    SELECT component_id, name, type, is_percentage, default_value
    FROM   payroll_components
    ORDER BY type, name
"""

PAYROLL_TREND = """
    SELECT
        month,
        year,
        ROUND(SUM(net_salary), 2)  AS total_payroll,
        ROUND(AVG(net_salary), 2)  AS avg_net_salary,
        COUNT(*)                   AS employee_count
    FROM   payroll
    GROUP BY year, month
    ORDER BY year, month
"""

PAYROLL_EXISTS = """
    SELECT COUNT(*) AS cnt
    FROM   payroll
    WHERE  employee_id = %s AND month = %s AND year = %s
"""

PAYROLL_PRESENT_DAYS = """
    SELECT
        COUNT(*) AS present_days
    FROM   attendance
    WHERE  employee_id     = %s
      AND  MONTH(attendance_date) = %s
      AND  YEAR(attendance_date)  = %s
      AND  status IN ('Present', 'WFH', 'Half-Day')
"""

# ===========================================================
# ANALYTICS / KPI QUERIES
# ===========================================================

KPI_HEADCOUNT = """
    SELECT COUNT(*) AS total
    FROM   employees
    WHERE  status = 'Active'
"""

KPI_ATTRITION_RATE = """
    SELECT
        ROUND(
            100.0 * SUM(CASE WHEN status IN ('Resigned','Terminated') THEN 1 ELSE 0 END)
            / NULLIF(COUNT(*), 0),
        2) AS attrition_rate
    FROM employees
"""

KPI_PENDING_LEAVES = """
    SELECT COUNT(*) AS total
    FROM   leaves
    WHERE  status = 'Pending'
"""

KPI_PAYROLL_CURRENT_MONTH = """
    SELECT ROUND(SUM(net_salary), 2) AS total_payroll
    FROM   payroll
    WHERE  month = %s AND year = %s
"""
