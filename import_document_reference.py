import json
import sqlite3
import os
import base64
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='document_import.log',
    filemode='w'
)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('healthcare.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to create tables if they don't exist
def ensure_tables_exist():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Read the schema file
    with open('clinical_notes_schema_corrected.sql', 'r') as f:
        schema_script = f.read()
    
    # Execute the schema script
    try:
        cursor.executescript(schema_script)
        conn.commit()
        logging.info("Database schema created or verified successfully")
    except sqlite3.Error as e:
        logging.error(f"Error creating schema: {e}")
        conn.rollback()
    finally:
        conn.close()

# Function to import categories from DocumentReference
def import_categories(doc_references):
    conn = get_db_connection()
    cursor = conn.cursor()
    categories_added = 0
    
    try:
        # Extract unique categories from all documents
        unique_categories = set()
        for doc in doc_references:
            if 'category' in doc and isinstance(doc['category'], list):
                for category in doc['category']:
                    if 'coding' in category and isinstance(category['coding'], list):
                        for coding in category['coding']:
                            if 'code' in coding and 'display' in coding:
                                unique_categories.add((coding['code'], coding['display']))
        
        # Insert unique categories
        for code, display in unique_categories:
            try:
                cursor.execute(
                    "INSERT INTO note_category (category_code, category_display) VALUES (?, ?)",
                    (code, display)
                )
                categories_added += 1
            except sqlite3.IntegrityError:
                # Category already exists (due to UNIQUE constraint)
                pass
        
        conn.commit()
        logging.info(f"Imported {categories_added} categories")
    except Exception as e:
        logging.error(f"Error importing categories: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    return categories_added

# Function to get category_id from code
def get_category_id(category_code):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT category_id FROM note_category WHERE category_code = ?",
            (category_code,)
        )
        result = cursor.fetchone()
        if result:
            return result['category_id']
        return None
    except Exception as e:
        logging.error(f"Error getting category ID: {e}")
        return None
    finally:
        conn.close()

# Function to import DocumentReference resources
def import_document_references(doc_references):
    conn = get_db_connection()
    cursor = conn.cursor()
    notes_added = 0
    versions_added = 0
    
    try:
        for doc in doc_references:
            try:
                # Extract basic metadata
                doc_id = doc.get('id')
                status = doc.get('status', 'unknown')
                doc_status = doc.get('docStatus', 'unknown')
                
                # Get document type
                note_type = None
                note_type_code = None
                if 'type' in doc and 'coding' in doc['type'] and len(doc['type']['coding']) > 0:
                    note_type = doc['type']['coding'][0].get('display')
                    note_type_code = doc['type']['coding'][0].get('code')
                
                # Get category
                category_id = None
                if 'category' in doc and isinstance(doc['category'], list) and len(doc['category']) > 0:
                    if 'coding' in doc['category'][0] and isinstance(doc['category'][0]['coding'], list) and len(doc['category'][0]['coding']) > 0:
                        category_code = doc['category'][0]['coding'][0].get('code')
                        if category_code:
                            category_id = get_category_id(category_code)
                
                # Get encounter reference
                encounter_id = None
                if 'context' in doc and 'encounter' in doc['context'] and isinstance(doc['context']['encounter'], list) and len(doc['context']['encounter']) > 0:
                    encounter_ref = doc['context']['encounter'][0].get('reference', '')
                    if encounter_ref.startswith('Encounter/'):
                        encounter_id = encounter_ref.split('/')[-1]
                
                # Get date
                note_date = None
                if 'date' in doc:
                    note_date = doc['date']
                
                # Insert note record
                cursor.execute(
                    """INSERT INTO note 
                       (note_id_external, category_id, note_type, note_type_code, encounter_id, note_date) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (doc_id, category_id, note_type, note_type_code, encounter_id, note_date)
                )
                note_id = cursor.lastrowid
                notes_added += 1
                
                # Get content
                if 'content' in doc and isinstance(doc['content'], list) and len(doc['content']) > 0:
                    content_item = doc['content'][0]
                    if 'attachment' in content_item:
                        attachment = content_item['attachment']
                        
                        # Get text content - could be in 'data' (base64) or 'url' field
                        note_text = None
                        if 'data' in attachment:
                            try:
                                # Try to decode base64 data
                                note_text = base64.b64decode(attachment['data']).decode('utf-8')
                            except Exception as e:
                                logging.warning(f"Could not decode base64 data for document {doc_id}: {e}")
                                note_text = attachment['data']  # Store as is if can't decode
                        elif 'url' in attachment:
                            note_text = f"URL: {attachment['url']}"  # Store URL reference
                        
                        # Get author/practitioner
                        practitioner_id = None
                        if 'author' in doc and isinstance(doc['author'], list) and len(doc['author']) > 0:
                            author_ref = doc['author'][0].get('reference', '')
                            if author_ref.startswith('Practitioner/'):
                                practitioner_id = author_ref.split('/')[-1]
                        
                        # Insert note version
                        cursor.execute(
                            """INSERT INTO note_version 
                               (note_id, version_number, note_text, practioner_id) 
                               VALUES (?, ?, ?, ?)""",
                            (note_id, 1, note_text, practitioner_id)
                        )
                        version_id = cursor.lastrowid
                        versions_added += 1
                        
                        # Update note with current version
                        cursor.execute(
                            "UPDATE note SET current_version_id = ? WHERE note_id = ?",
                            (version_id, note_id)
                        )
                
                conn.commit()
            except Exception as e:
                logging.error(f"Error processing document {doc.get('id', 'unknown')}: {e}")
                conn.rollback()
        
        logging.info(f"Imported {notes_added} notes with {versions_added} versions")
    except Exception as e:
        logging.error(f"Error in import process: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    return notes_added, versions_added

# Main function
def main():
    try:
        # Ensure database tables exist
        ensure_tables_exist()
        
        # Load DocumentReference data
        doc_reference_file = 'DocumentReference_patient_12769853_data.json'
        if not os.path.exists(doc_reference_file):
            logging.error(f"File not found: {doc_reference_file}")
            return
        
        with open(doc_reference_file, 'r') as f:
            doc_data = json.load(f)
        
        # Check if it's an array or a single object
        if isinstance(doc_data, dict):
            if doc_data.get('resourceType') == 'Bundle' and 'entry' in doc_data:
                # Handle FHIR Bundle
                doc_references = [entry['resource'] for entry in doc_data['entry'] 
                                if entry.get('resource', {}).get('resourceType') == 'DocumentReference']
            elif doc_data.get('resourceType') == 'DocumentReference':
                # Single DocumentReference
                doc_references = [doc_data]
            else:
                doc_references = []
        elif isinstance(doc_data, list):
            # Array of resources
            doc_references = [doc for doc in doc_data if doc.get('resourceType') == 'DocumentReference']
        else:
            doc_references = []
        
        logging.info(f"Found {len(doc_references)} DocumentReference resources")
        
        # Import categories first
        categories_added = import_categories(doc_references)
        
        # Import documents
        notes_added, versions_added = import_document_references(doc_references)
        
        logging.info(f"Import complete. Added {categories_added} categories, {notes_added} notes, and {versions_added} versions.")
    
    except Exception as e:
        logging.error(f"Unexpected error in main function: {e}")

if __name__ == "__main__":
    main()