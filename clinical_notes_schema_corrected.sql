-- Create Category Table
CREATE TABLE note_category (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_code TEXT NOT NULL,
    category_display TEXT NOT NULL,
    -- loinc_code TEXT,
    -- is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_code)
);

-- Create Note Table (Metadata only)
CREATE TABLE note (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id_external TEXT,
    category_id INTEGER,
    note_type TEXT,
    note_type_code TEXT,
    encounter_id INTEGER,
    -- practitioner_id INTEGER,
    note_date DATE,
    current_version_id INTEGER,
    -- is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES note_category(category_id)
);

-- Create Note Version Table (Content with versioning)
CREATE TABLE note_version (
    version_id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER,
    version_number INTEGER,
    note_text TEXT,
    practioner_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES note(note_id)
);

-- Create indexes for better performance
CREATE INDEX idx_note_category ON note(category_id);
CREATE INDEX idx_note_type ON note(note_type);
CREATE INDEX idx_note_date ON note(note_date);
CREATE INDEX idx_note_version ON note_version(note_id, version_number);
-- -- Simplified Clinical Notes Database Schema
-- -- With proper versioning and categories

-- -- Enable foreign key constraints
-- PRAGMA foreign_keys = ON;

-- -- Patient table
-- CREATE TABLE PATIENT (
--     patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     mrn TEXT UNIQUE NOT NULL,
--     first_name TEXT NOT NULL,
--     last_name TEXT NOT NULL,
--     birth_date DATE NOT NULL,
--     gender TEXT,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
-- );

-- -- Encounter table
-- CREATE TABLE ENCOUNTER (
--     encounter_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     patient_id INTEGER NOT NULL,
--     start_time DATETIME NOT NULL,
--     end_time DATETIME,
--     encounter_type TEXT NOT NULL,
--     department TEXT,
--     visit_number TEXT UNIQUE,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (patient_id) REFERENCES PATIENT(patient_id)
-- );

-- -- Healthcare providers
-- CREATE TABLE PRACTITIONER (
--     practitioner_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     npi TEXT UNIQUE,
--     first_name TEXT NOT NULL,
--     last_name TEXT NOT NULL,
--     specialty TEXT,
--     department TEXT,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
-- );

-- -- Note categories table
-- CREATE TABLE NOTE_CATEGORY (
--     category_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     category_code TEXT NOT NULL,    -- Standardized category code
--     category_name TEXT NOT NULL,    -- Display name
--     description TEXT,              -- Category description
--     source_system TEXT,            -- FHIR/Epic/Cerner
--     is_active BOOLEAN DEFAULT true,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     UNIQUE(category_code, source_system)
-- );

-- -- -- Insert common note categories
-- -- INSERT INTO NOTE_CATEGORY (category_code, category_name, description) VALUES
-- --     ('NURSING', 'Nursing', 'Nursing notes and documentation'),
-- --     ('PHYSICIAN', 'Physician', 'Physician notes and documentation'),
-- --     ('DISCHARGE', 'Discharge Summary', 'Hospital discharge summaries'),
-- --     ('RADIOLOGY', 'Radiology', 'Radiology reports and notes'),
-- --     ('CARDIOLOGY', 'Cardiology', 'Cardiology reports including ECG, Echo'),
-- --     ('PHARMACY', 'Pharmacy', 'Pharmacy notes and documentation'),
-- --     ('CONSULT', 'Consultation', 'Specialist consultation notes'),
-- --     ('PROCEDURE', 'Procedure', 'Procedure notes and reports'),
-- --     ('PROGRESS', 'Progress Note', 'Clinical progress notes'),
-- --     ('EMERGENCY', 'Emergency', 'Emergency department notes');

-- -- Main notes table (metadata only)
-- CREATE TABLE NOTE (
--     note_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     external_id TEXT UNIQUE,        -- FHIR DocumentReference.id
--     -- patient_id INTEGER NOT NULL,
--     encounter_id INTEGER,
--     category_id INTEGER NOT NULL,   -- Reference to NOTE_CATEGORY
--     note_type TEXT NOT NULL,        -- Type of note (Progress Note, Discharge Summary, etc.)
--     title TEXT NOT NULL,            -- Note title
--     current_version_id INTEGER,     -- Reference to current version
--     status TEXT NOT NULL,           -- current, superseded, deleted
--     source_system TEXT NOT NULL,    -- FHIR/Epic/Cerner
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     created_by INTEGER NOT NULL,
--     updated_by INTEGER,
--     -- FOREIGN KEY (patient_id) REFERENCES PATIENT(patient_id),
--     FOREIGN KEY (encounter_id) REFERENCES ENCOUNTER(encounter_id),
--     FOREIGN KEY (category_id) REFERENCES NOTE_CATEGORY(category_id),
--     FOREIGN KEY (created_by) REFERENCES PRACTITIONER(practitioner_id),
--     FOREIGN KEY (updated_by) REFERENCES PRACTITIONER(practitioner_id)
-- );

-- -- Note versions table (content with versioning)
-- CREATE TABLE NOTE_VERSION (
--     version_id INTEGER PRIMARY KEY AUTOINCREMENT,
--     note_id INTEGER NOT NULL,
--     version_number INTEGER NOT NULL, -- Sequential version number
--     note_text TEXT NOT NULL,        -- The actual note content
--     author_id INTEGER NOT NULL,     -- Provider who created this version
--     charttime DATETIME NOT NULL,    -- When this version was written
--     signature_time DATETIME,        -- When this version was signed
--     version_status TEXT NOT NULL,   -- preliminary, final, amended
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     created_by INTEGER NOT NULL,
--     FOREIGN KEY (note_id) REFERENCES NOTE(note_id),
--     FOREIGN KEY (author_id) REFERENCES PRACTITIONER(practitioner_id),
--     FOREIGN KEY (created_by) REFERENCES PRACTITIONER(practitioner_id),
--     UNIQUE(note_id, version_number)
-- );

-- -- Add foreign key for current_version_id after NOTE_VERSION table is created
-- ALTER TABLE NOTE 
-- ADD FOREIGN KEY (current_version_id) REFERENCES NOTE_VERSION(version_id);

-- -- Indexes for optimization

-- -- Patient indexes
-- CREATE INDEX idx_patient_mrn ON PATIENT(mrn);
-- CREATE INDEX idx_patient_name ON PATIENT(last_name, first_name);

-- -- Encounter indexes
-- CREATE INDEX idx_encounter_patient ON ENCOUNTER(patient_id);
-- CREATE INDEX idx_encounter_dates ON ENCOUNTER(start_time, end_time);
-- CREATE INDEX idx_encounter_visit ON ENCOUNTER(visit_number);

-- -- Note indexes
-- CREATE INDEX idx_note_patient ON NOTE(patient_id);
-- CREATE INDEX idx_note_encounter ON NOTE(encounter_id);
-- CREATE INDEX idx_note_category ON NOTE(category_id);
-- CREATE INDEX idx_note_external ON NOTE(external_id);
-- CREATE INDEX idx_note_type ON NOTE(note_type);
-- CREATE INDEX idx_note_status ON NOTE(status);
-- CREATE INDEX idx_note_current_version ON NOTE(current_version_id);

-- -- Version indexes
-- CREATE INDEX idx_version_note ON NOTE_VERSION(note_id);
-- CREATE INDEX idx_version_author ON NOTE_VERSION(author_id);
-- CREATE INDEX idx_version_charttime ON NOTE_VERSION(charttime);
-- CREATE INDEX idx_version_status ON NOTE_VERSION(version_status);
-- CREATE INDEX idx_version_number ON NOTE_VERSION(note_id, version_number);

-- -- Category indexes
-- CREATE INDEX idx_category_code ON NOTE_CATEGORY(category_code);
-- CREATE INDEX idx_category_source ON NOTE_CATEGORY(source_system);
-- CREATE INDEX idx_category_active ON NOTE_CATEGORY(is_active);

-- -- Composite indexes for common queries
-- CREATE INDEX idx_note_patient_date 
-- ON NOTE_VERSION(note_id, charttime);

-- -- Triggers for automatic timestamp updates
-- CREATE TRIGGER update_patient_timestamp 
-- AFTER UPDATE ON PATIENT
-- BEGIN
--     UPDATE PATIENT SET updated_at = CURRENT_TIMESTAMP 
--     WHERE patient_id = NEW.patient_id;
-- END;

-- CREATE TRIGGER update_note_timestamp 
-- AFTER UPDATE ON NOTE
-- BEGIN
--     UPDATE NOTE SET updated_at = CURRENT_TIMESTAMP 
--     WHERE note_id = NEW.note_id;
-- END;

-- CREATE TRIGGER update_practitioner_timestamp 
-- AFTER UPDATE ON PRACTITIONER
-- BEGIN
--     UPDATE PRACTITIONER SET updated_at = CURRENT_TIMESTAMP 
--     WHERE practitioner_id = NEW.practitioner_id;
-- END;

-- -- Trigger to update current_version_id in NOTE table when a new version becomes current
-- CREATE TRIGGER update_current_version
-- AFTER INSERT ON NOTE_VERSION
-- BEGIN
--     UPDATE NOTE 
--     SET current_version_id = NEW.version_id,
--         updated_at = CURRENT_TIMESTAMP
--     WHERE note_id = NEW.note_id;
-- END;

-- -- Example of Category and Type relationships:
-- /*
-- Category: PHYSICIAN
-- - Types:
--   - Progress Note
--   - Admission Note
--   - Discharge Summary
--   - Consultation Note
--   - Procedure Note
--   - Operation Report

-- Category: NURSING
-- - Types:
--   - Nursing Assessment
--   - Care Plan Note
--   - Medication Administration Note
--   - Shift Handover Note
--   - Patient Education Note
--   - Wound Care Note

-- Category: RADIOLOGY
-- - Types:
--   - X-Ray Report
--   - CT Scan Report
--   - MRI Report
--   - Ultrasound Report
--   - Nuclear Medicine Report

-- Category: PHARMACY
-- - Types:
--   - Medication Review Note
--   - Clinical Pharmacy Note
--   - Drug Therapy Assessment
--   - Medication Reconciliation

-- Category: EMERGENCY
-- - Types:
--   - Emergency Assessment
--   - Triage Note
--   - Trauma Note
--   - Emergency Discharge Note
-- */
