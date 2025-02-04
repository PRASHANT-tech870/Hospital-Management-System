-- Drop tables if they exist

create database Hospital;
use Hospital;


DROP TABLE IF EXISTS Appointments;
DROP TABLE IF EXISTS Account;
DROP TABLE IF EXISTS Equipment;
DROP TABLE IF EXISTS Department;
DROP TABLE IF EXISTS Doctor;
DROP TABLE IF EXISTS Patient;
DROP TABLE IF EXISTS Staff;

-- Create Staff table
CREATE TABLE Staff (
    staff_id INT PRIMARY KEY,
    _name VARCHAR(100),
    _role VARCHAR(50),
    age INT,
    gender VARCHAR(20),
    salary DECIMAL(10,2),
    working_hours INT,
    department_id INT
);

-- Create Patient table
CREATE TABLE Patient (
    patient_id VARCHAR(20) PRIMARY KEY,
    fname VARCHAR(50),
    lname VARCHAR(50),
    dob DATE,
    age INT,
    blood_group VARCHAR(5),
    phone_no VARCHAR(15),
    email_id VARCHAR(100),
    _address TEXT,
    emergency_contact VARCHAR(100)
);

-- Create Doctor table
CREATE TABLE Doctor (
    doctor_id VARCHAR(20) PRIMARY KEY,
    _name VARCHAR(100),
    _specialization VARCHAR(100),
    years_experience INT,
    phone_no VARCHAR(15),
    email_id VARCHAR(100),
    consultation_fee DECIMAL(10,2),
    department_id INT
);

-- Create Department table
CREATE TABLE Department (
    department_id INT PRIMARY KEY,
    name VARCHAR(100),
    hod_doc_id INT,
    _location VARCHAR(100), -- Changed location to _location
    no_of_staff INT,
    budget DECIMAL(12,2)
);

-- Create Equipment table with product_id
CREATE TABLE Equipment (
    equipment_id INT,
    product_id VARCHAR(50), -- Composite key with equipment_id
    name VARCHAR(100),
    department_id INT,
    price_per_unit DECIMAL(10,2),
    date_of_purchase DATE,
    _status VARCHAR(50), -- Changed status to _status
    category VARCHAR(50),
    ward VARCHAR(50),
    PRIMARY KEY (equipment_id, product_id) -- Composite primary key
);

-- Create Account table
CREATE TABLE Account (
    invoice_id INT PRIMARY KEY,
    patient_id VARCHAR(20),
    amount DECIMAL(10,2),
    _date DATE,
    _status VARCHAR(50), -- Changed status to _status
    reason_for_billing TEXT
);

-- Create Appointments table
CREATE TABLE Appointments (
    appointment_id INT PRIMARY KEY,
    patient_id VARCHAR(20),
    doctor_id VARCHAR(20),
    _date DATE,
    _time TIME,  
    duration INT DEFAULT 30,  
    _status VARCHAR(50),
    purpose TEXT,
    doctor_name VARCHAR(100),
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Doctor(doctor_id)
);      

-- Add foreign key constraints
ALTER TABLE Staff
ADD FOREIGN KEY (department_id) REFERENCES Department(department_id);

ALTER TABLE Doctor
ADD FOREIGN KEY (department_id) REFERENCES Department(department_id);

ALTER TABLE Equipment
ADD FOREIGN KEY (department_id) REFERENCES Department(department_id);

-- Insert sample data
-- Departments
INSERT INTO Department VALUES
(1, 'Cardiology', 1, 'Building A, Floor 2', 15, 500000.00),
(2, 'Neurology', 2, 'Building B, Floor 1', 12, 450000.00),
(3, 'Pediatrics', 3, 'Building A, Floor 1', 10, 350000.00);

-- Doctors
INSERT INTO Doctor VALUES
('D001', 'Dr. John Smith', 'Cardiologist', 15, '555-0101', 'john.smith@hospital.com', 200.00, 1),
('D002', 'Dr. Sarah Johnson', 'Neurologist', 12, '555-0102', 'sarah.j@hospital.com', 180.00, 2),
('D003', 'Dr. Michael Brown', 'Pediatrician', 8, '555-0103', 'michael.b@hospital.com', 150.00, 3);

-- Staff
INSERT INTO Staff VALUES
(1, 'Jane Doe', 'Nurse', 28, 'Female', 45000.00, 40, 1),
(2, 'Robert Wilson', 'Technician', 35, 'Male', 52000.00, 40, 2),
(3, 'Mary Johnson', 'Nurse', 31, 'Female', 47000.00, 36, 3);

-- Patients
INSERT INTO Patient VALUES
('P001', 'William', 'Davis', '1980-05-15', 43, 'A+', '555-0201', 'william.d@email.com', '123 Main St', '555-0901'),
('P002', 'Emma', 'Wilson', '1992-08-22', 31, 'B-', '555-0202', 'emma.w@email.com', '456 Oak Ave', '555-0902'),
('P003', 'James', 'Taylor', '1975-03-10', 48, 'O+', '555-0203', 'james.t@email.com', '789 Pine Rd', '555-0903');

-- Equipment (Updated with product_id)
INSERT INTO Equipment VALUES
(1, 'ECG-2023-001', 'ECG Machine', 1, 12000.00, '2023-01-15', 'Active', 'Diagnostic', 'Cardiology'),
(2, 'MRI-2022-001', 'MRI Scanner', 2, 500000.00, '2022-06-20', 'Active', 'Imaging', 'Radiology'),
(3, 'VEN-2023-001', 'Ventilator', 3, 25000.00, '2023-03-10', 'Active', 'Life Support', 'ICU');

-- Accounts
INSERT INTO Account VALUES
(1, 'P001', 1500.00, '2024-01-10', 'Paid', 'Cardiac Consultation'),
(2, 'P002', 2500.00, '2024-01-12', 'Pending', 'MRI Scan'),
(3, 'P003', 800.00, '2024-01-15', 'Paid', 'Regular Checkup');

-- Appointments
INSERT INTO Appointments VALUES
(1, 'P001', 'D001', '2024-01-20', '10:00:00', 30, 'Scheduled', 'Follow-up', 'Dr. John Smith'),
(2, 'P002', 'D002', '2024-01-21', '11:00:00', 30, 'Confirmed', 'Initial Consultation', 'Dr. Sarah Johnson'),
(3, 'P003', 'D003', '2024-01-22', '09:00:00', 30, 'Completed', 'Regular Checkup', 'Dr. Michael Brown');
