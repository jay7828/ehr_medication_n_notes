-- SQLite Healthcare Database Schema (Simplified)
-- Based on FHIR resources: Medication, MedicationRequest, MedicationAdministration

-- Drop tables if they exist to ensure clean creation
DROP TABLE IF EXISTS medication_administration;
DROP TABLE IF EXISTS medication_request;
DROP TABLE IF EXISTS medication;

-- Medication table - stores basic medication information
CREATE TABLE medication (
    medication_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Internal auto-incremental ID
    medication_id_external TEXT UNIQUE,              -- External FHIR resource ID
    medication TEXT,             -- Display name of medication
    form TEXT,                   -- Dosage form (e.g., tablet, solution)
    ingredient TEXT,             -- Main ingredient(s)
    strength TEXT,               -- Strength of medication
    manufacturer TEXT            -- Manufacturer name
);

-- MedicationRequest table - stores prescription/medication order information
CREATE TABLE medication_request (
    medication_request_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Internal auto-incremental ID
    medication_request_id_external TEXT UNIQUE,              -- External FHIR resource ID
    medication_id TEXT,          -- Reference to medication
    medication TEXT,             -- Display name of medication (for cases without medication_id)
    status TEXT,                 -- Status of request (active, completed, etc.)
    practitioner_id TEXT,        -- Prescriber identifier
    encounter_id TEXT,           -- Associated encounter
    authored_on TEXT,            -- When prescription was written
    dosage_text TEXT,            -- Dosage instructions as text
    dosage_route TEXT,           -- Route of administration
    dosage_method TEXT,          -- Method of administration
    dosage_quantity REAL,        -- Dose quantity
    dosage_unit TEXT,            -- Dose unit
    timing_frequency INTEGER,     -- How many times per period
    timing_period REAL,          -- Period value
    timing_period_unit TEXT,     -- Period unit (day, week, etc.)
    timing_start TEXT,           -- When to start taking
    timing_end TEXT              -- When to stop taking
);

-- MedicationAdministration table - stores information about medication administration
CREATE TABLE medication_administration (
    medication_administration_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Internal auto-incremental ID
    medication_administration_id_external TEXT UNIQUE,              -- External FHIR resource ID
    medication_id TEXT,          -- Reference to medication
    medication_display TEXT,     -- Display name of medication (for cases without medication_id)
    status TEXT,                 -- Status of administration (completed, etc.)
    practitioner_id TEXT,        -- Administering practitioner identifier
    request_id TEXT,             -- Associated medication request
    encounter_id TEXT,           -- Associated encounter
    effective_start TEXT,        -- When administration started
    effective_end TEXT,          -- When administration ended
    dosage_text TEXT,            -- Dosage instructions as text
    dosage_route TEXT,           -- Route of administration
    dosage_method TEXT,          -- Method of administration
    dosage_quantity REAL,        -- Dose quantity
    dosage_unit TEXT             -- Dose unit
);
