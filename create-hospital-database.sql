-- Create the hospital database
CREATE DATABASE hospital;

-- Connect to the hospital database hospital

-- Create the appointments table
CREATE TABLE appointments (
    appointment_id   SERIAL PRIMARY KEY,
    patient_id       INTEGER NOT NULL REFERENCES patients,
    staff_id         INTEGER NOT NULL REFERENCES staff,
    appointment_date TIMESTAMP NOT NULL,
    appointment_type TEXT NOT NULL
);

-- Create the patients table
CREATE TABLE patients (
    patient_id      SERIAL PRIMARY KEY,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    date_of_birth   DATE NOT NULL,
    medical_history TEXT
);

-- Create the resources table
CREATE TABLE resources (
    resource_id   SERIAL PRIMARY KEY,
    resource_type TEXT NOT NULL,
    resource_name TEXT NOT NULL
);

-- Create the staff table
CREATE TABLE staff (
    staff_id   SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name  TEXT NOT NULL,
    role       TEXT NOT NULL,
    password   VARCHAR
);

-- Create the tests table
CREATE TABLE tests (
    test_id      SERIAL PRIMARY KEY,
    patient_id   INTEGER NOT NULL REFERENCES patients,
    test_type    TEXT NOT NULL,
    test_date    TIMESTAMP NOT NULL,
    test_results TEXT
);

-- Create the treatments table
CREATE TABLE treatments (
    treatment_id   SERIAL PRIMARY KEY,
    patient_id     INTEGER NOT NULL REFERENCES patients,
    treatment_type TEXT NOT NULL,
    treatment_date TIMESTAMP NOT NULL
);