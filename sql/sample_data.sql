-- =============================================================
-- HR Analytics & Employee Management Dashboard
-- sample_data.sql  — Realistic seed data
-- Run AFTER schema.sql:  mysql -u root -p hr_analytics < sql/sample_data.sql
-- =============================================================

USE hr_analytics;

-- ---------------------------------------------------------------
-- DEPARTMENTS  (8 departments)
-- ---------------------------------------------------------------
INSERT INTO departments (department_name) VALUES
    ('Engineering'),
    ('Human Resources'),
    ('Finance'),
    ('Marketing'),
    ('Sales'),
    ('Operations'),
    ('Product Management'),
    ('Customer Support');

-- ---------------------------------------------------------------
-- DESIGNATIONS  (18 designations)
-- ---------------------------------------------------------------
INSERT INTO designations (title, grade) VALUES
    ('Software Engineer',            'Junior'),
    ('Senior Software Engineer',     'Senior'),
    ('Lead Engineer',                'Lead'),
    ('Engineering Manager',          'Manager'),
    ('HR Executive',                 'Junior'),
    ('Senior HR Executive',          'Mid'),
    ('HR Manager',                   'Manager'),
    ('Accountant',                   'Junior'),
    ('Senior Accountant',            'Senior'),
    ('Finance Manager',              'Manager'),
    ('Marketing Executive',          'Junior'),
    ('Marketing Manager',            'Manager'),
    ('Sales Executive',              'Junior'),
    ('Senior Sales Executive',       'Mid'),
    ('Sales Manager',                'Manager'),
    ('Operations Analyst',           'Junior'),
    ('Product Manager',              'Manager'),
    ('Customer Support Executive',   'Junior');

-- ---------------------------------------------------------------
-- PAYROLL COMPONENTS  (5 components)
-- ---------------------------------------------------------------
INSERT INTO payroll_components (name, type, is_percentage, default_value) VALUES
    ('HRA',                     'Allowance', TRUE,  40.00),   -- 40% of basic
    ('Medical Allowance',       'Allowance', FALSE, 1500.00), -- fixed ₹1500
    ('Transport Allowance',     'Allowance', FALSE, 800.00),  -- fixed ₹800
    ('Provident Fund',          'Deduction', TRUE,  12.00),   -- 12% of basic
    ('Professional Tax',        'Deduction', FALSE, 200.00);  -- fixed ₹200

-- ---------------------------------------------------------------
-- LEAVE TYPES
-- ---------------------------------------------------------------
INSERT INTO leave_types (type_name, annual_quota, is_paid) VALUES
    ('Casual Leave',    12, TRUE),
    ('Sick Leave',      10, TRUE),
    ('Earned Leave',    15, TRUE),
    ('Maternity Leave', 90, TRUE),
    ('Unpaid Leave',    30, FALSE);

-- ---------------------------------------------------------------
-- EMPLOYEES  (40 employees)
-- ---------------------------------------------------------------
INSERT INTO employees
    (emp_code, first_name, last_name, email, phone,
     department_id, designation_id, joining_date, date_of_birth, basic_salary, status)
VALUES
-- Engineering (dept 1)
('EMP001', 'Aarav',     'Sharma',    'aarav.sharma@hrco.in',     '9876543210', 1, 2, '2021-03-15', '1993-07-22', 85000.00, 'Active'),
('EMP002', 'Priya',     'Nair',      'priya.nair@hrco.in',       '9876543211', 1, 1, '2022-06-01', '1997-02-14', 55000.00, 'Active'),
('EMP003', 'Rahul',     'Verma',     'rahul.verma@hrco.in',      '9876543212', 1, 3, '2020-01-10', '1990-11-30', 110000.00,'Active'),
('EMP004', 'Sneha',     'Iyer',      'sneha.iyer@hrco.in',       '9876543213', 1, 1, '2023-04-18', '1999-05-05', 52000.00, 'Active'),
('EMP005', 'Vikram',    'Mehta',     'vikram.mehta@hrco.in',     '9876543214', 1, 4, '2019-08-20', '1988-12-01', 145000.00,'Active'),
('EMP006', 'Ananya',    'Gupta',     'ananya.gupta@hrco.in',     '9876543215', 1, 2, '2021-11-05', '1994-03-18', 78000.00, 'Active'),
('EMP007', 'Kiran',     'Reddy',     'kiran.reddy@hrco.in',      '9876543216', 1, 1, '2023-09-01', '1998-08-25', 50000.00, 'Active'),
('EMP008', 'Deepak',    'Singh',     'deepak.singh@hrco.in',     '9876543217', 1, 2, '2022-02-14', '1995-06-12', 82000.00, 'Resigned'),

-- Human Resources (dept 2)
('EMP009', 'Meera',     'Pillai',    'meera.pillai@hrco.in',     '9876543218', 2, 7, '2018-05-01', '1985-04-20', 95000.00, 'Active'),
('EMP010', 'Arjun',     'Patel',     'arjun.patel@hrco.in',      '9876543219', 2, 5, '2022-08-15', '1996-10-08', 45000.00, 'Active'),
('EMP011', 'Lakshmi',   'Rao',       'lakshmi.rao@hrco.in',      '9876543220', 2, 6, '2021-01-25', '1993-01-15', 60000.00, 'Active'),

-- Finance (dept 3)
('EMP012', 'Suresh',    'Joshi',     'suresh.joshi@hrco.in',     '9876543221', 3, 10,'2017-07-01', '1982-09-10', 120000.00,'Active'),
('EMP013', 'Pooja',     'Kapoor',    'pooja.kapoor@hrco.in',     '9876543222', 3, 8, '2023-01-09', '1998-03-22', 42000.00, 'Active'),
('EMP014', 'Nitin',     'Bhatt',     'nitin.bhatt@hrco.in',      '9876543223', 3, 9, '2020-10-14', '1991-07-30', 70000.00, 'Active'),
('EMP015', 'Divya',     'Kulkarni',  'divya.kulkarni@hrco.in',   '9876543224', 3, 8, '2022-04-01', '1997-12-05', 44000.00, 'Active'),

-- Marketing (dept 4)
('EMP016', 'Rohit',     'Saxena',    'rohit.saxena@hrco.in',     '9876543225', 4, 12,'2019-02-18', '1989-06-14', 90000.00, 'Active'),
('EMP017', 'Nisha',     'Tiwari',    'nisha.tiwari@hrco.in',     '9876543226', 4, 11,'2021-07-07', '1994-11-27', 50000.00, 'Active'),
('EMP018', 'Aditya',    'Choudhary', 'aditya.choudhary@hrco.in', '9876543227', 4, 11,'2023-03-20', '1999-08-16', 48000.00, 'Active'),
('EMP019', 'Riya',      'Desai',     'riya.desai@hrco.in',       '9876543228', 4, 11,'2022-09-12', '1996-02-03', 49000.00, 'Inactive'),

-- Sales (dept 5)
('EMP020', 'Manish',    'Agarwal',   'manish.agarwal@hrco.in',   '9876543229', 5, 15,'2018-11-01', '1986-05-19', 105000.00,'Active'),
('EMP021', 'Swati',     'Bose',      'swati.bose@hrco.in',       '9876543230', 5, 13,'2023-05-08', '2000-01-11', 40000.00, 'Active'),
('EMP022', 'Rajesh',    'Kumar',     'rajesh.kumar@hrco.in',     '9876543231', 5, 14,'2021-12-01', '1992-09-28', 62000.00, 'Active'),
('EMP023', 'Kavya',     'Menon',     'kavya.menon@hrco.in',      '9876543232', 5, 13,'2022-07-25', '1997-04-17', 42000.00, 'Active'),
('EMP024', 'Sanjay',    'Mishra',    'sanjay.mishra@hrco.in',    '9876543233', 5, 14,'2020-03-05', '1990-08-08', 65000.00, 'Active'),

-- Operations (dept 6)
('EMP025', 'Preeti',    'Shah',      'preeti.shah@hrco.in',      '9876543234', 6, 16,'2020-06-22', '1992-12-15', 55000.00, 'Active'),
('EMP026', 'Amit',      'Pandey',    'amit.pandey@hrco.in',      '9876543235', 6, 16,'2021-09-13', '1994-07-03', 53000.00, 'Active'),
('EMP027', 'Shweta',    'Trivedi',   'shweta.trivedi@hrco.in',   '9876543236', 6, 16,'2023-02-28', '1998-10-21', 50000.00, 'Active'),
('EMP028', 'Gaurav',    'Malhotra',  'gaurav.malhotra@hrco.in',  '9876543237', 6, 16,'2019-04-15', '1988-03-07', 58000.00, 'Terminated'),

-- Product Management (dept 7)
('EMP029', 'Tanvi',     'Jain',      'tanvi.jain@hrco.in',       '9876543238', 7, 17,'2019-10-01', '1987-11-12', 130000.00,'Active'),
('EMP030', 'Abhishek',  'Dubey',     'abhishek.dubey@hrco.in',   '9876543239', 7, 17,'2021-05-17', '1991-06-25', 125000.00,'Active'),

-- Customer Support (dept 8)
('EMP031', 'Rekha',     'Nair',      'rekha.nair@hrco.in',       '9876543240', 8, 18,'2022-01-03', '1996-09-09', 38000.00, 'Active'),
('EMP032', 'Mohit',     'Sharma',    'mohit.sharma@hrco.in',     '9876543241', 8, 18,'2022-11-21', '1997-03-14', 38000.00, 'Active'),
('EMP033', 'Pallavi',   'Singh',     'pallavi.singh@hrco.in',    '9876543242', 8, 18,'2023-07-10', '1999-11-02', 36000.00, 'Active'),
('EMP034', 'Harsh',     'Yadav',     'harsh.yadav@hrco.in',      '9876543243', 8, 18,'2021-08-30', '1993-05-18', 40000.00, 'Active'),

-- More Engineering
('EMP035', 'Ishaan',    'Chopra',    'ishaan.chopra@hrco.in',    '9876543244', 1, 1, '2024-01-15', '2000-07-07', 50000.00, 'Active'),
('EMP036', 'Simran',    'Bhatia',    'simran.bhatia@hrco.in',    '9876543245', 1, 2, '2022-10-10', '1995-01-20', 80000.00, 'Active'),
('EMP037', 'Yash',      'Srivastava','yash.srivastava@hrco.in',  '9876543246', 1, 1, '2023-11-01', '1998-12-31', 52000.00, 'Active'),

-- More Sales
('EMP038', 'Neha',      'Verma',     'neha.verma@hrco.in',       '9876543247', 5, 13,'2024-02-01', '2001-04-10', 40000.00, 'Active'),
('EMP039', 'Kunal',     'Ahuja',     'kunal.ahuja@hrco.in',      '9876543248', 5, 14,'2020-09-07', '1991-10-14', 63000.00, 'Active'),
('EMP040', 'Alka',      'Chauhan',   'alka.chauhan@hrco.in',     '9876543249', 2, 5, '2023-08-14', '1999-06-27', 44000.00, 'Active');

-- ---------------------------------------------------------------
-- LEAVE BALANCES  (2026, for all active employees)
-- ---------------------------------------------------------------
INSERT INTO leave_balances (employee_id, leave_type_id, year, total_days, used_days)
SELECT e.employee_id, lt.leave_type_id, 2026, lt.annual_quota,
       FLOOR(RAND() * (lt.annual_quota * 0.4))   -- random used 0-40% of quota
FROM employees e
CROSS JOIN leave_types lt
WHERE e.status = 'Active';

-- ---------------------------------------------------------------
-- ATTENDANCE  (June 2026 — 26 working days, all active employees)
-- ---------------------------------------------------------------
-- We generate one row per active employee per working day in June 2026
-- Using a helper approach: insert day by day for the 22 weekdays of June 2026
-- Working days in June 2026 (Mon-Sat approach, 6-day week): 1-27 excl Sundays
-- For simplicity we mark Mon-Sat only (Sundays skipped)

INSERT INTO attendance (employee_id, attendance_date, status, remarks)
SELECT
    e.employee_id,
    d.work_date,
    CASE
        WHEN RAND() < 0.02 THEN 'Holiday'
        WHEN RAND() < 0.06 THEN 'Absent'
        WHEN RAND() < 0.10 THEN 'Half-Day'
        WHEN RAND() < 0.20 THEN 'WFH'
        ELSE 'Present'
    END AS status,
    NULL AS remarks
FROM employees e
CROSS JOIN (
    SELECT DATE('2026-06-01') + INTERVAL (n-1) DAY AS work_date
    FROM (
        SELECT 1 AS n UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
        UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
        UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
        UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20
        UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25
        UNION SELECT 26 UNION SELECT 27
    ) nums
    WHERE DAYOFWEEK(DATE('2026-06-01') + INTERVAL (n-1) DAY) NOT IN (1)  -- exclude Sundays
) d
WHERE e.status IN ('Active', 'Inactive');

-- Also add attendance for May 2026
INSERT INTO attendance (employee_id, attendance_date, status, remarks)
SELECT
    e.employee_id,
    d.work_date,
    CASE
        WHEN RAND() < 0.02 THEN 'Holiday'
        WHEN RAND() < 0.06 THEN 'Absent'
        WHEN RAND() < 0.10 THEN 'Half-Day'
        WHEN RAND() < 0.18 THEN 'WFH'
        ELSE 'Present'
    END AS status,
    NULL AS remarks
FROM employees e
CROSS JOIN (
    SELECT DATE('2026-05-01') + INTERVAL (n-1) DAY AS work_date
    FROM (
        SELECT 1 AS n UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
        UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
        UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
        UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20
        UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25
        UNION SELECT 26
    ) nums
    WHERE DAYOFWEEK(DATE('2026-05-01') + INTERVAL (n-1) DAY) NOT IN (1)
) d
WHERE e.status IN ('Active', 'Inactive');

-- ---------------------------------------------------------------
-- LEAVE APPLICATIONS
-- ---------------------------------------------------------------
INSERT INTO leaves (employee_id, leave_type_id, start_date, end_date, total_days, reason, status, approved_by, action_at)
VALUES
(2,  1, '2026-06-10', '2026-06-11', 2, 'Personal work',              'Approved',  9, '2026-06-09 10:00:00'),
(4,  2, '2026-06-05', '2026-06-05', 1, 'Fever',                       'Approved',  9, '2026-06-04 09:30:00'),
(7,  1, '2026-07-01', '2026-07-02', 2, 'Family function',             'Pending',   NULL, NULL),
(10, 3, '2026-05-20', '2026-05-24', 5, 'Annual vacation',             'Approved',  9, '2026-05-18 11:00:00'),
(13, 2, '2026-06-18', '2026-06-18', 1, 'Doctor appointment',         'Approved',  9, '2026-06-17 14:00:00'),
(17, 1, '2026-07-05', '2026-07-07', 3, 'Out of town',                 'Pending',   NULL, NULL),
(21, 1, '2026-06-23', '2026-06-24', 2, 'Personal',                    'Rejected',  9, '2026-06-22 16:00:00'),
(25, 3, '2026-05-12', '2026-05-16', 5, 'Planned leave',               'Approved',  9, '2026-05-10 09:00:00'),
(31, 2, '2026-06-12', '2026-06-13', 2, 'Illness',                     'Approved',  9, '2026-06-11 08:30:00'),
(33, 1, '2026-07-08', '2026-07-09', 2, 'Personal commitments',        'Pending',   NULL, NULL),
(6,  3, '2026-04-21', '2026-04-25', 5, 'Wedding',                     'Approved',  9, '2026-04-19 10:00:00'),
(22, 2, '2026-06-02', '2026-06-03', 2, 'Not feeling well',            'Approved',  9, '2026-06-01 09:00:00'),
(36, 1, '2026-07-14', '2026-07-15', 2, 'Personal work',               'Pending',   NULL, NULL),
(1,  3, '2026-03-10', '2026-03-14', 5, 'Family trip',                 'Approved',  9, '2026-03-08 11:00:00'),
(29, 1, '2026-06-16', '2026-06-17', 2, 'Personal',                    'Approved',  9, '2026-06-14 15:00:00');

-- ---------------------------------------------------------------
-- PAYROLL  (May 2026 payroll — manually generated for demo)
-- ---------------------------------------------------------------
INSERT INTO payroll
    (employee_id, month, year, basic_salary, total_allowances, total_deductions,
     net_salary, working_days, present_days, payslip_generated, generated_at)
SELECT
    e.employee_id,
    5              AS month,
    2026           AS year,
    e.basic_salary AS basic_salary,
    ROUND(e.basic_salary * 0.40 + 1500 + 800, 2)                 AS total_allowances,
    ROUND(e.basic_salary * 0.12 + 200, 2)                        AS total_deductions,
    ROUND(e.basic_salary + (e.basic_salary * 0.40 + 1500 + 800)
          - (e.basic_salary * 0.12 + 200), 2)                    AS net_salary,
    26             AS working_days,
    26             AS present_days,
    TRUE           AS payslip_generated,
    '2026-05-31 18:00:00' AS generated_at
FROM employees e
WHERE e.status IN ('Active','Inactive');

-- Payroll line items for May 2026
INSERT INTO payroll_details (payroll_id, component_id, amount)
SELECT
    p.payroll_id,
    pc.component_id,
    CASE
        WHEN pc.is_percentage = TRUE  THEN ROUND(p.basic_salary * pc.default_value / 100, 2)
        ELSE pc.default_value
    END AS amount
FROM payroll p
CROSS JOIN payroll_components pc
WHERE p.month = 5 AND p.year = 2026;
