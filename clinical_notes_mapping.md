# MIMIC Clinical Notes to FHIR DocumentReference Mapping

This document provides mapping guidance for converting MIMIC clinical notes to FHIR DocumentReference resources and the corresponding database schema.

## Database Schema

```sql
-- Clinical Notes table
CREATE TABLE clinical_notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,        -- Internal ID
    note_id_external TEXT UNIQUE,                     -- FHIR DocumentReference.id
    patient_id TEXT,                                  -- Reference to patient
    encounter_id TEXT,                                -- Reference to encounter
    practitioner_id TEXT,                             -- Reference to practitioner (author)
    note_type TEXT,                                   -- Type of clinical note
    note_category TEXT,                               -- Category of the note
    note_title TEXT,                                  -- Title of the note
    note_text TEXT,                                   -- The actual clinical note content
    status TEXT,                                      -- Status of the document (preliminary, final, etc.)
    created_date TEXT,                                -- When the note was created
    last_modified TEXT,                               -- When the note was last modified
    authenticator_id TEXT,                            -- Reference to practitioner who authenticated
    authentication_date TEXT                          -- When the note was authenticated
);

-- Note Sections table (for structured notes)
CREATE TABLE note_sections (
    section_id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER,                                  -- Reference to parent note
    section_title TEXT,                               -- Title of the section
    section_code TEXT,                                -- LOINC code for section type
    section_text TEXT,                                -- Content of the section
    FOREIGN KEY (note_id) REFERENCES clinical_notes(note_id)
);
```

## MIMIC to FHIR DocumentReference Mapping

| MIMIC Field | FHIR Path | Database Column | Notes |
|-------------|-----------|-----------------|-------|
| SUBJECT_ID | DocumentReference.subject.reference | patient_id | Reference to Patient resource |
| HADM_ID | DocumentReference.context.encounter.reference | encounter_id | Reference to Encounter resource |
| CHARTTIME | DocumentReference.date | created_date | When note was recorded |
| STORETIME | DocumentReference.meta.lastModified | last_modified | When note was last modified |
| CATEGORY | DocumentReference.category[0].coding[0].code | note_category | Note category (e.g., 'clinical-note', 'discharge-summary') |
| DESCRIPTION | DocumentReference.type.coding[0].display | note_type | Type of note |
| TEXT | DocumentReference.content[0].attachment.data | note_text | The actual note content (Base64 encoded in FHIR) |
| CGID | DocumentReference.author.reference | practitioner_id | Reference to care provider |

## FHIR DocumentReference Structure

```json
{
  "resourceType": "DocumentReference",
  "id": "<generated>",
  "status": "current",
  "docStatus": "final",
  "type": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "11506-3",
      "display": "Progress note"
    }]
  },
  "category": [{
    "coding": [{
      "system": "http://hl7.org/fhir/document-category",
      "code": "clinical-note",
      "display": "Clinical Note"
    }]
  }],
  "subject": {
    "reference": "Patient/<id>"
  },
  "date": "<created_date>",
  "author": [{
    "reference": "Practitioner/<id>"
  }],
  "authenticator": {
    "reference": "Practitioner/<id>"
  },
  "content": [{
    "attachment": {
      "contentType": "text/plain",
      "data": "<base64_encoded_note>",
      "title": "<note_title>"
    }
  }],
  "context": {
    "encounter": [{
      "reference": "Encounter/<id>"
    }],
    "period": {
      "start": "<encounter_start>",
      "end": "<encounter_end>"
    }
  }
}
```

## Section Types (LOINC Codes)

Common clinical note sections and their LOINC codes:

| Section Name | LOINC Code | Description |
|--------------|------------|-------------|
| Chief Complaint | 10154-3 | Patient's reported symptoms |
| History of Present Illness | 10164-2 | Chronological description of symptoms |
| Past Medical History | 11348-0 | Previous medical conditions |
| Medications | 10160-0 | Current medications |
| Physical Examination | 29545-1 | Physical examination findings |
| Assessment | 51848-0 | Clinical assessment |
| Plan | 18776-5 | Treatment plan |
| Progress Notes | 11506-3 | Ongoing progress notes |
| Discharge Summary | 18842-5 | Summary at discharge |

## Implementation Notes

1. **Text Processing**:
   - MIMIC clinical notes often contain special characters and formatting
   - Clean and standardize text before storing
   - Preserve original formatting where clinically relevant

2. **Section Parsing**:
   - Use regular expressions or NLP to identify sections
   - Map to standard LOINC codes
   - Store structured data in note_sections table

3. **Security Considerations**:
   - Implement appropriate access controls
   - Log all access to clinical notes
   - Ensure data encryption at rest

4. **Search Optimization**:
   - Consider full-text search indexing
   - Index commonly searched fields
   - Cache frequently accessed notes

5. **Quality Checks**:
   - Validate required fields
   - Check for appropriate date ranges
   - Verify practitioner references

## Handling Different Document Formats

The FHIR DocumentReference can handle various document formats through the `content.attachment` element. Here's how different formats are handled:

### 1. PDF Documents
```json
{
  "resourceType": "DocumentReference",
  "content": [{
    "attachment": {
      "contentType": "application/pdf",
      "data": "<base64_encoded_pdf>",
      "title": "Discharge Summary",
      "creation": "2025-06-13",
      "hash": "571ef9c5655840f324e679072ed62b1b95eef8a0",
      "size": 231044
    }
  }]
}
```

### 2. Scanned Documents (Images)
```json
{
  "resourceType": "DocumentReference",
  "content": [{
    "attachment": {
      "contentType": "image/jpeg",  // or image/png, image/tiff
      "data": "<base64_encoded_image>",
      "title": "Scanned Progress Note",
      "creation": "2025-06-13",
      "hash": "571ef9c5655840f324e679072ed62b1b95eef8a0",
      "size": 156032
    }
  }]
}
```

### 3. Rich Text Format (RTF)
```json
{
  "resourceType": "DocumentReference",
  "content": [{
    "attachment": {
      "contentType": "application/rtf",
      "data": "<base64_encoded_rtf>",
      "title": "Clinical Summary",
      "creation": "2025-06-13"
    }
  }]
}
```

### 4. HTML Documents
```json
{
  "resourceType": "DocumentReference",
  "content": [{
    "attachment": {
      "contentType": "text/html",
      "data": "<base64_encoded_html>",
      "title": "Operative Report",
      "creation": "2025-06-13"
    }
  }]
}
```

## Database Schema Updates for Document Formats

```sql
-- Add columns to clinical_notes table
ALTER TABLE clinical_notes ADD COLUMN content_type TEXT;    -- MIME type of the content
ALTER TABLE clinical_notes ADD COLUMN content_data BLOB;    -- Binary content for PDFs, images
ALTER TABLE clinical_notes ADD COLUMN file_hash TEXT;       -- SHA1 hash of the content
ALTER TABLE clinical_notes ADD COLUMN file_size INTEGER;    -- Size in bytes
```

## Common MIME Types for Clinical Documents

| Document Type | MIME Type | Description |
|--------------|-----------|-------------|
| Plain Text | text/plain | Standard text notes |
| PDF | application/pdf | PDF documents |
| JPEG Image | image/jpeg | Scanned documents |
| PNG Image | image/png | Scanned documents |
| TIFF Image | image/tiff | Scanned documents |
| RTF | application/rtf | Rich text documents |
| HTML | text/html | Web-based documents |
| XML | application/xml | Structured documents |
| CDA | application/hl7-cda+xml | HL7 CDA documents |

## Implementation Guidelines for Different Formats

1. **PDF Processing**:
   - Use OCR (Optical Character Recognition) to extract text
   - Store both original PDF and extracted text
   - Index extracted text for searching
   - Maintain PDF bookmarks and structure

2. **Image Processing**:
   - Apply OCR to extract text from scanned documents
   - Store original image and OCR'd text
   - Consider storing thumbnails for quick preview
   - Implement image enhancement if needed

3. **Binary Storage**:
   - Use BLOB storage for binary content
   - Consider external storage for large files
   - Implement proper backup procedures
   - Use compression when appropriate

4. **Content Validation**:
   - Verify file integrity using hash
   - Validate MIME types
   - Check file size limits
   - Scan for malware

5. **Content Access**:
   - Implement format-specific viewers
   - Provide download options
   - Support content transformation
   - Enable secure sharing

6. **Search Considerations**:
   - Index extracted text from all formats
   - Enable format-specific filters
   - Support metadata search
   - Implement full-text search

7. **Audit Trail**:
   - Log all document access
   - Track format conversions
   - Record viewing sessions
   - Monitor download activity
