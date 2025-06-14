import json
import sqlite3
import os
import base64
import logging
import requests
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='binary_extraction.log',
    filemode='w'
)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('healthcare.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to fetch binary content from URL
def fetch_binary_content(url):
    try:
        # First, try to get the Binary resource metadata using application/fhir+json
        metadata_headers = {
            'Accept': 'application/fhir+json'
        }
        
        # Make a GET request to get the Binary resource metadata
        metadata_response = requests.get(url, headers=metadata_headers, timeout=30)
        
        if metadata_response.status_code == 200:
            try:
                # Parse the Binary resource to get the contentType
                binary_resource = metadata_response.json()
                content_type = binary_resource.get('contentType', 'application/octet-stream')
                
                # Now request the actual binary content with the correct content type
                content_headers = {
                    'Accept': content_type
                }
                
                # Make a GET request to get the actual binary content
                content_response = requests.get(url, headers=content_headers, timeout=30)
                
                if content_response.status_code == 200:
                    return content_response.content, content_type
                else:
                    logging.error(f"Failed to fetch binary content from {url}. Status code: {content_response.status_code}")
            except json.JSONDecodeError:
                logging.error(f"Failed to parse Binary resource metadata from {url}")
        else:
            logging.error(f"Failed to fetch Binary resource metadata from {url}. Status code: {metadata_response.status_code}")
        
        # If we couldn't get the content with the specific approach, try with common MIME types
        common_mime_types = [
            'application/pdf', 
            'text/plain',
            'text/html',
            'image/jpeg',
            'image/png',
            'application/xml',
            'application/octet-stream'
        ]
        
        for mime_type in common_mime_types:
            headers = {
                'Accept': mime_type
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.content, mime_type
        
        logging.error(f"Failed to fetch content from {url} with any MIME type")
        return None, None
    except Exception as e:
        logging.error(f"Error fetching content from {url}: {e}")
        return None, None

# Function to update note version with actual content
def update_note_with_binary_content(note_id, version_id, binary_content, content_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Convert binary content to base64 for storage
        base64_content = base64.b64encode(binary_content).decode('utf-8')
        
        # Update the note_version record with the actual content
        cursor.execute(
            """UPDATE note_version 
               SET note_text = ?, content_type = ? 
               WHERE version_id = ?""",
            (base64_content, content_type, version_id)
        )
        
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"Error updating note version {version_id} with binary content: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Function to process all notes with URL references
def process_url_references():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Find all note versions with URL references
        cursor.execute(
            """SELECT n.note_id, nv.version_id, nv.note_text 
               FROM note n 
               JOIN note_version nv ON n.note_id = nv.note_id 
               WHERE nv.note_text LIKE 'URL: %'"""
        )
        
        url_notes = cursor.fetchall()
        logging.info(f"Found {len(url_notes)} notes with URL references")
        
        success_count = 0
        error_count = 0
        
        for note in url_notes:
            note_id = note['note_id']
            version_id = note['version_id']
            url_text = note['note_text']
            
            # Extract the URL from the text
            url = url_text.replace('URL: ', '').strip()
            
            logging.info(f"Processing note {note_id}, version {version_id} with URL: {url}")
            
            # Fetch the binary content
            binary_content, content_type = fetch_binary_content(url)
            
            if binary_content:
                # Update the note version with the actual content
                if update_note_with_binary_content(note_id, version_id, binary_content, content_type):
                    success_count += 1
                else:
                    error_count += 1
            else:
                error_count += 1
        
        logging.info(f"Completed processing URL references. Success: {success_count}, Errors: {error_count}")
        return success_count, error_count
    
    except Exception as e:
        logging.error(f"Error processing URL references: {e}")
        return 0, 0
    finally:
        conn.close()

# Add content_type column to note_version table if it doesn't exist
def ensure_content_type_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if content_type column exists
        cursor.execute("PRAGMA table_info(note_version)")
        columns = cursor.fetchall()
        column_names = [column['name'] for column in columns]
        
        if 'content_type' not in column_names:
            logging.info("Adding content_type column to note_version table")
            cursor.execute("ALTER TABLE note_version ADD COLUMN content_type TEXT")
            conn.commit()
            logging.info("Added content_type column to note_version table")
        else:
            logging.info("content_type column already exists in note_version table")
    
    except Exception as e:
        logging.error(f"Error ensuring content_type column: {e}")
        conn.rollback()
    finally:
        conn.close()

# Main function
def main():
    try:
        # Ensure content_type column exists
        ensure_content_type_column()
        
        # Process all URL references
        success_count, error_count = process_url_references()
        
        logging.info(f"Binary content extraction complete. Successfully updated {success_count} notes. Failed to update {error_count} notes.")
    
    except Exception as e:
        logging.error(f"Unexpected error in main function: {e}")

if __name__ == "__main__":
    main()