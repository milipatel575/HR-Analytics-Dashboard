-- =============================================================
-- HR Analytics & Employee Management Dashboard
-- schema.sql  — Full DDL
-- Author: Internship Project
-- Database: MySQL 8.0+
-- Run with: mysql -u root -p < sql/schema.sql
-- =============================================================

DROP DATABASE IF EXISTS hr_analytics;
CREATE DATABASE IF NOT EXISTS hr_analytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE hr_analytics;

-- ---------------------------------------------------------------
-- 1. DEPARTMENTS
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS departments (
    department_id   INT             NOT NULL AUTO_INCREMENT,
    department_name VARCHAR(100)    NOT NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (department_id),
    UNIQUE KEY uq_dept_name (department_name)
) ENGINE=InnoDB;


-- ---------------------------------------------------------------
-- 2. DESIGNATIONS
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS designations (
    designation_id  INT             NOT NULL AUTO_INCREMENT,
    title           VARCHAR(100)    NOT NULL,
    grade           ENUM('Junior','Mid','Senior','Lead','Manager','Director') NOT NULL DEFAULT 'Junior',
    PRIMARY KEY (designation_id),
    UNIQUE KEY uq_designation_title (title)
) ENGINE=InnoDB;


-- ---------------------------------------------------------------
-- 3. EMPLOYEES  (core table)
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS employees (
    employee_id     INT             NOT NULL AUTO_INCREMENT,
    emp_code        VARCHAR(20)     NOT NULL,
    first_name      VARCHAR(50)     NOT NULL,
    last_name       VARCHAR(50)     NOT NULL,
    email           VARCHAR(150)    NOT NULL,
    phone           VARCHAR(15),
    department_id   INT             NOT NULL,
    designation_id  INT             NOT NULL,
    joining_date    DATE            NOT NULL,
    date_of_birth   DATE,
    basic_salary    DECIMAL(12,2)   NOT NULL,
    status          ENUM('Active','Inactive','Resigned','Terminated') NOT NULL DEFAULT 'Active',
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (employee_id),
    UNIQUE KEY uq_emp_code  (emp_code),
    UNIQUE KEY uq_emp_email (email),
    CONSTRAINT fk_emp_dept  FOREIGN KEY (department_id)  REFERENCES departments  (department_id) ON UPDATE CASCADE,
    CONSTRAINT fk_emp_desig FOREIGN KEY (designation_id) REFERENCES designations (designation_id) ON UPDATE CASCADE,
    CONSTRAINT chk_salary   CHECK (basic_salary >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_emp_dept    ON employees (department_id);
CREATE INDEX idx_emp_status  ON employees (status);


-- ---------------------------------------------------------------
-- 4. ATTENDANCE
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id   INT             NOT NULL AUTO_INCREMENT,
    employee_id     INT             NOT NULL,
    attendance_date DATE            NOT NULL,
    status          ENUM('Present','Absent','Half-Day','WFH','Holiday') NOT NULL,
    check_in        TIME,
    check_out       TIME,
    remarks         VARCHAR(255),
    PRIMARY KEY (attendance_id),
    UNIQUE KEY uq_attendance (employee_id, attendance_date),
    CONSTRAINT fk_att_emp FOREIGN KEY (employee_id) REFERENCES employees (employee_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_att_date ON attendance (attendance_date);
CREATE INDEX idx_att_emp  ON attendance (employee_id);


-- ---------------------------------------------------------------
-- 5. LEAVE TYPES
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS leave_types (
    leave_type_id   INT             NOT NULL AUTO_INCREMENT,
    type_name       VARCHAR(50)     NOT NULL,
    annual_quota    INT             NOT NULL,
    is_paid         BOOLEAN         NOT NULL DEFAULT TRUE,
    PRIMARY KEY (leave_type_id),
    UNIQUE KEY uq_leave_type_name (type_name),
    CONSTRAINT chk_quota CHECK (annual_quota > 0)
) ENGINE=InnoDB;


-- ---------------------------------------------------------------
-- 6. LEAVE BALANCES
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS leave_balances (
    balance_id      INT             NOT NULL AUTO_INCREMENT,
    employee_id     INT             NOT NULL,
    leave_type_id   INT             NOT NULL,
    year            YEAR            NOT NULL,
    total_days      INT             NOT NULL,
    used_days       INT             NOT NULL DEFAULT 0,
    PRIMARY KEY (balance_id),
    UNIQUE KEY uq_leave_balance (employee_id, leave_type_id, year),
    CONSTRAINT fk_lb_emp   FOREIGN KEY (employee_id)   REFERENCES employees   (employee_id)   ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_lb_ltype FOREIGN KEY (leave_type_id) REFERENCES leave_types (leave_type_id) ON UPDATE CASCADE,
    CONSTRAINT chk_used_days CHECK (used_days >= 0)
) ENGINE=InnoDB;


-- ---------------------------------------------------------------
-- 7. LEAVES
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS leaves (
    leave_id        INT             NOT NULL AUTO_INCREMENT,
    employee_id     INT             NOT NULL,
    leave_type_id   INT             NOT NULL,
    start_date      DATE            NOT NULL,
    end_date        DATE            NOT NULL,
    total_days      INT             NOT NULL,
    reason          TEXT,
    status          ENUM('Pending','Approved','Rejected','Cancelled') NOT NULL DEFAULT 'Pending',
    approved_by     INT,
    applied_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    action_at       TIMESTAMP       NULL,
    PRIMARY KEY (leave_id),
    CONSTRAINT fk_lv_emp    FOREIGN KEY (employee_id)   REFERENCES employees   (employee_id)   ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_lv_ltype  FOREIGN KEY (leave_type_id) REFERENCES leave_types (leave_type_id) ON UPDATE CASCADE,
    CONSTRAINT fk_lv_approver FOREIGN KEY (approved_by) REFERENCES employees   (employee_id)   ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_lv_dates CHECK (end_date >= start_date),
    CONSTRAINT chk_lv_days  CHECK (total_days > 0)
) ENGINE=InnoDB;

CREATE INDEX idx_lv_emp    ON leaves (employee_id);
CREATE INDEX idx_lv_status ON leaves (status);


-- ---------------------------------------------------------------
-- 8. PAYROLL COMPONENTS
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payroll_components (
    component_id    INT             NOT NULL AUTO_INCREMENT,
    name            VARCHAR(100)    NOT NULL,
    type            ENUM('Allowance','Deduction') NOT NULL,
    is_percentage   BOOLEAN         NOT NULL DEFAULT FALSE,
    default_value   DECIMAL(10,2)   NOT NULL,
    PRIMARY KEY (component_id),
    UNIQUE KEY uq_component_name (name),
    CONSTRAINT chk_comp_val CHECK (default_value >= 0)
) ENGINE=InnoDB;


-- ---------------------------------------------------------------
-- 9. PAYROLL
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payroll (
    payroll_id          INT             NOT NULL AUTO_INCREMENT,
    employee_id         INT             NOT NULL,
    month               TINYINT         NOT NULL,
    year                YEAR            NOT NULL,
    basic_salary        DECIMAL(12,2)   NOT NULL,
    total_allowances    DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    total_deductions    DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    net_salary          DECIMAL(12,2)   NOT NULL,
    working_days        INT             NOT NULL,
    present_days        INT             NOT NULL,
    payslip_generated   BOOLEAN         NOT NULL DEFAULT FALSE,
    generated_at        TIMESTAMP       NULL,
    PRIMARY KEY (payroll_id),
    UNIQUE KEY uq_payroll (employee_id, month, year),
    CONSTRAINT fk_pr_emp FOREIGN KEY (employee_id) REFERENCES employees (employee_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_month CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT chk_net   CHECK (net_salary >= 0)
) ENGINE=InnoDB;

CREATE INDEX idx_pr_emp       ON payroll (employee_id);
CREATE INDEX idx_pr_month_yr  ON payroll (month, year);


-- ---------------------------------------------------------------
-- 10. PAYROLL DETAILS  (line items per payslip)
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payroll_details (
    detail_id       INT             NOT NULL AUTO_INCREMENT,
    payroll_id      INT             NOT NULL,
    component_id    INT             NOT NULL,
    amount          DECIMAL(10,2)   NOT NULL,
    PRIMARY KEY (detail_id),
    CONSTRAINT fk_pd_payroll    FOREIGN KEY (payroll_id)   REFERENCES payroll            (payroll_id)   ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pd_component  FOREIGN KEY (component_id) REFERENCES payroll_components (component_id) ON UPDATE CASCADE
) ENGINE=InnoDB;


-- =============================================================
-- VIEWS
-- =============================================================

-- ---------------------------------------------------------------
-- VIEW 1: Full employee details (flattens the 3-table join)
-- Used on every employee listing screen.
-- ---------------------------------------------------------------
CREATE OR REPLACE VIEW v_employee_full_details AS
SELECT
    e.employee_id,
    e.emp_code,
    CONCAT(e.first_name, ' ', e.last_name)  AS full_name,
    e.first_name,
    e.last_name,
    e.email,
    e.phone,
    e.joining_date,
    e.date_of_birth,
    e.basic_salary,
    e.status,
    e.created_at,
    e.updated_at,
    d.department_id,
    d.department_name,
    des.designation_id,
    des.title                               AS designation,
    des.grade,
    TIMESTAMPDIFF(YEAR, e.joining_date, CURDATE()) AS tenure_years
FROM employees      e
JOIN departments    d   ON e.department_id  = d.department_id
JOIN designations   des ON e.designation_id = des.designation_id;


-- ---------------------------------------------------------------
-- VIEW 2: Monthly attendance summary per employee
-- Powers the attendance analytics chart and monthly % calculation.
-- ---------------------------------------------------------------
CREATE OR REPLACE VIEW v_monthly_attendance_summary AS
SELECT
    a.employee_id,
    CONCAT(e.first_name, ' ', e.last_name) AS full_name,
    e.emp_code,
    d.department_name,
    MONTH(a.attendance_date)               AS month,
    YEAR(a.attendance_date)                AS year,
    COUNT(*)                               AS total_records,
    SUM(CASE WHEN a.status = 'Present'  THEN 1 ELSE 0 END) AS present_days,
    SUM(CASE WHEN a.status = 'Absent'   THEN 1 ELSE 0 END) AS absent_days,
    SUM(CASE WHEN a.status = 'Half-Day' THEN 1 ELSE 0 END) AS half_days,
    SUM(CASE WHEN a.status = 'WFH'      THEN 1 ELSE 0 END) AS wfh_days,
    SUM(CASE WHEN a.status = 'Holiday'  THEN 1 ELSE 0 END) AS holidays,
    ROUND(
        100.0 * SUM(CASE WHEN a.status IN ('Present','WFH') THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*) - SUM(CASE WHEN a.status = 'Holiday' THEN 1 ELSE 0 END), 0),
        2
    )                                      AS attendance_pct
FROM attendance a
JOIN employees   e ON a.employee_id   = e.employee_id
JOIN departments d ON e.department_id = d.department_id
GROUP BY
    a.employee_id, e.first_name, e.last_name, e.emp_code,
    d.department_name, MONTH(a.attendance_date), YEAR(a.attendance_date);


-- =============================================================
-- STORED PROCEDURE: Generate Payroll
-- Atomically computes and inserts payroll + line items.
-- Raises SQLSTATE '45000' if payroll already exists for the period.
-- =============================================================
DROP PROCEDURE IF EXISTS sp_generate_payroll;

DELIMITER $$

CREATE PROCEDURE sp_generate_payroll(
    IN  p_employee_id   INT,
    IN  p_month         TINYINT,
    IN  p_year          YEAR,
    IN  p_working_days  INT,
    IN  p_present_days  INT
)
BEGIN
    DECLARE v_basic_salary      DECIMAL(12,2);
    DECLARE v_total_allowances  DECIMAL(12,2) DEFAULT 0.00;
    DECLARE v_total_deductions  DECIMAL(12,2) DEFAULT 0.00;
    DECLARE v_net_salary        DECIMAL(12,2);
    DECLARE v_payroll_id        INT;
    DECLARE v_exists            INT DEFAULT 0;
    DECLARE v_comp_id           INT;
    DECLARE v_comp_type         VARCHAR(20);
    DECLARE v_is_pct            BOOLEAN;
    DECLARE v_def_val           DECIMAL(10,2);
    DECLARE v_amount            DECIMAL(10,2);
    DECLARE done                INT DEFAULT FALSE;

    -- Cursor iterates over all payroll components
    DECLARE comp_cursor CURSOR FOR
        SELECT component_id, type, is_percentage, default_value
        FROM payroll_components;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Guard: check if payroll already generated
    SELECT COUNT(*) INTO v_exists
    FROM payroll
    WHERE employee_id = p_employee_id
      AND month       = p_month
      AND year        = p_year;

    IF v_exists > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Payroll already generated for this employee and period.';
    END IF;

    -- Fetch basic salary (prorated if absent days > 0)
    SELECT basic_salary INTO v_basic_salary
    FROM employees
    WHERE employee_id = p_employee_id;

    -- Prorate: pay only for days present
    IF p_working_days > 0 THEN
        SET v_basic_salary = ROUND(v_basic_salary * p_present_days / p_working_days, 2);
    END IF;

    -- Begin transaction
    START TRANSACTION;

    -- Insert payroll header (net_salary filled after components loop)
    INSERT INTO payroll (employee_id, month, year, basic_salary,
                         total_allowances, total_deductions, net_salary,
                         working_days, present_days, payslip_generated, generated_at)
    VALUES (p_employee_id, p_month, p_year, v_basic_salary,
            0.00, 0.00, 0.00,
            p_working_days, p_present_days, FALSE, NULL);

    SET v_payroll_id = LAST_INSERT_ID();

    -- Loop over components
    OPEN comp_cursor;
    comp_loop: LOOP
        FETCH comp_cursor INTO v_comp_id, v_comp_type, v_is_pct, v_def_val;
        IF done THEN LEAVE comp_loop; END IF;

        IF v_is_pct THEN
            SET v_amount = ROUND(v_basic_salary * v_def_val / 100, 2);
        ELSE
            SET v_amount = v_def_val;
        END IF;

        INSERT INTO payroll_details (payroll_id, component_id, amount)
        VALUES (v_payroll_id, v_comp_id, v_amount);

        IF v_comp_type = 'Allowance' THEN
            SET v_total_allowances = v_total_allowances + v_amount;
        ELSE
            SET v_total_deductions = v_total_deductions + v_amount;
        END IF;
    END LOOP;
    CLOSE comp_cursor;

    SET v_net_salary = v_basic_salary + v_total_allowances - v_total_deductions;
    IF v_net_salary < 0 THEN SET v_net_salary = 0; END IF;

    -- Update header with computed totals
    UPDATE payroll
    SET total_allowances = v_total_allowances,
        total_deductions = v_total_deductions,
        net_salary       = v_net_salary
    WHERE payroll_id = v_payroll_id;

    COMMIT;
END$$

DELIMITER ;
