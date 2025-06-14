# Clinical Notes Database Schema and ER Diagram

## ER Diagram (Text Format)

```
[NOTE]
*note_id [PK]
provider_id [FK]
insurance_id [FK]
system_prompt_id
system_prompt_sort_id
note_date
note_id_external
note (TEXT)
encounter_id [FK]
note_status_id [FK]
category_id [FK]
order_id [FK]
diagnosis
diagnosis_id
is_archive
created_at
updated_at
inserted_by
updated_by

[PROVIDER]
*provider_id [PK]
provider_name
npi
specialty
is_active

[INSURANCE]
*insurance_id [PK]
insurance_name
plan_type
is_active

[ENCOUNTER]
*encounter_id [PK]
patient_id [FK]
visit_date
encounter_type
department

[NOTE_STATUS] {meta schema}
*note_status_id [PK]
status_name
description

[CATEGORY] {meta schema}
*category_id [PK]
category_name
description

[ORDER]
*order_id [PK]
order_date
order_type
status

[SYSTEM_PROMPT]
*system_prompt_id [PK]
prompt_text
is_active
sort_order

Relationships:
NOTE }--|| PROVIDER: "has"
NOTE }--|| INSURANCE: "has"
NOTE }--|| ENCOUNTER: "belongs to"
NOTE }--|| NOTE_STATUS: "has"
NOTE }--|| CATEGORY: "belongs to"
NOTE }--|| ORDER: "related to"
NOTE }--|| SYSTEM_PROMPT: "uses"
```

## SQL Schema (PostgreSQL)

```sql
-- Create schemas if not exist
CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS meta;

-- Note Status table (meta schema)
CREATE TABLE meta.note_status (
    note_status_id BIGINT PRIMARY KEY,
    status_name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Category table (meta schema)
CREATE TABLE meta.category (
    category_id BIGINT PRIMARY KEY,
    category_name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Provider table (app schema)
CREATE TABLE app.provider (
    provider_id BIGINT PRIMARY KEY,
    provider_name TEXT NOT NULL,
    npi TEXT,
    specialty TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insurance table (app schema)
CREATE TABLE app.insurance (
    insurance_id BIGINT PRIMARY KEY,
    insurance_name TEXT NOT NULL,
    plan_type TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Encounter table (app schema)
CREATE TABLE app.encounter (
    encounter_id BIGINT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    visit_date DATE NOT NULL,
    encounter_type TEXT,
    department TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Order table (app schema)
CREATE TABLE app.order (
    order_id BIGINT PRIMARY KEY,
    order_date DATE NOT NULL,
    order_type TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System Prompt table (app schema)
CREATE TABLE app.system_prompt (
    system_prompt_id BIGINT PRIMARY KEY,
    prompt_text TEXT NOT NULL,
    sort_order INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Note table (app schema)
CREATE TABLE app.note (
    note_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    provider_id BIGINT REFERENCES app.provider(provider_id),
    insurance_id BIGINT REFERENCES app.insurance(insurance_id),
    system_prompt_id BIGINT NOT NULL,
    system_prompt_sort_id BIGINT NOT NULL,
    note_date DATE,
    note_id_external BIGINT,
    note TEXT NOT NULL,
    encounter_id INTEGER REFERENCES app.encounter(encounter_id),
    note_status_id BIGINT REFERENCES meta.note_status(note_status_id),
    category_id BIGINT REFERENCES meta.category(category_id),
    order_id BIGINT REFERENCES app.order(order_id),
    diagnosis TEXT,
    diagnosis_id BIGINT,
    is_archive BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    inserted_by BIGINT NOT NULL,
    updated_by BIGINT NOT NULL
);

-- Indexes
CREATE INDEX idx_note_provider ON app.note(provider_id);
CREATE INDEX idx_note_insurance ON app.note(insurance_id);
CREATE INDEX idx_note_encounter ON app.note(encounter_id);
CREATE INDEX idx_note_status ON app.note(note_status_id);
CREATE INDEX idx_note_category ON app.note(category_id);
CREATE INDEX idx_note_order ON app.note(order_id);
CREATE INDEX idx_note_system_prompt ON app.note(system_prompt_id);
CREATE INDEX idx_note_date ON app.note(note_date);
CREATE INDEX idx_note_external ON app.note(note_id_external);
CREATE INDEX idx_note_diagnosis ON app.note(diagnosis_id);
CREATE INDEX idx_note_archive ON app.note(is_archive);

-- Update triggers for timestamp management
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_note_timestamp
    BEFORE UPDATE ON app.note
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

## Key Features

1. **Schema Organization**:
   - `app` schema: Core application tables
   - `meta` schema: Metadata and lookup tables

2. **Main Tables**:
   - `app.note`: Primary notes table
   - `app.provider`: Healthcare providers
   - `app.insurance`: Insurance information
   - `app.encounter`: Patient encounters
   - `app.order`: Medical orders
   - `meta.note_status`: Note status lookup
   - `meta.category`: Note categories

3. **Key Fields in Note Table**:
   - `note_id`: Auto-incrementing primary key
   - `system_prompt_id`: Links to AI system prompts
   - `note`: Actual note content
   - `diagnosis`: Clinical diagnosis
   - `is_archive`: Archival status

4. **Optimizations**:
   - Appropriate indexes on foreign keys
   - Timestamp management triggers
   - Boolean flags for active/archive status
   - External ID support

5. **Data Types**:
   - `BIGINT` for IDs
   - `TEXT` for variable-length strings
   - `TIMESTAMP WITH TIME ZONE` for timestamps
   - `DATE` for dates
   - `BOOLEAN` for flags

## Relationships

1. Note → Provider (Optional)
2. Note → Insurance (Optional)
3. Note → Encounter (Optional)
4. Note → Note Status (Optional)
5. Note → Category (Optional)
6. Note → Order (Optional)
7. Note → System Prompt (Required)

## Common Queries

```sql
-- Get recent notes for a provider
SELECT n.*, p.provider_name
FROM app.note n
JOIN app.provider p ON n.provider_id = p.provider_id
WHERE n.provider_id = ? 
  AND n.note_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY n.note_date DESC;

-- Get notes by encounter
SELECT n.*, ns.status_name
FROM app.note n
JOIN meta.note_status ns ON n.note_status_id = ns.note_status_id
WHERE n.encounter_id = ?
ORDER BY n.created_at;

-- Get notes with specific category and status
SELECT n.*, c.category_name
FROM app.note n
JOIN meta.category c ON n.category_id = c.category_id
WHERE n.category_id = ?
  AND n.note_status_id = ?
  AND n.is_archive = false;
```
