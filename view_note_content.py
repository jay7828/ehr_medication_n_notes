import sqlite3
import base64
import os
import argparse

# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect('healthcare.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to get note content by ID
def get_note_content(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get note details
        cursor.execute(
            """SELECT n.note_id, n.note_type, nv.note_text, nv.content_type 
               FROM note n 
               JOIN note_version nv ON n.note_id = nv.note_id 
               WHERE n.note_id = ?""",
            (note_id,)
        )
        
        note = cursor.fetchone()
        
        if not note:
            print(f"Note with ID {note_id} not found.")
            return None
        
        return note
    except Exception as e:
        print(f"Error retrieving note: {e}")
        return None
    finally:
        conn.close()

# Function to save binary content to file
def save_content_to_file(content, content_type, note_id):
    # Determine file extension based on content type
    extension = 'bin'  # Default
    if content_type == 'application/pdf':
        extension = 'pdf'
    elif content_type == 'text/plain':
        extension = 'txt'
    elif content_type == 'text/html':
        extension = 'html'
    elif content_type == 'text/xml':
        extension = 'xml'
    elif content_type.startswith('image/'):
        extension = content_type.split('/')[-1]  # e.g., jpeg, png
    
    # Create output directory if it doesn't exist
    output_dir = 'note_content'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create filename
    filename = f"{output_dir}/note_{note_id}.{extension}"
    
    # Write content to file
    with open(filename, 'wb') as f:
        f.write(content)
    
    return filename

# Main function
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='View clinical note content')
    parser.add_argument('note_id', type=int, help='ID of the note to view')
    args = parser.parse_args()
    
    # Get note content
    note = get_note_content(args.note_id)
    
    if not note:
        return
    
    print(f"Note ID: {note['note_id']}")
    print(f"Note Type: {note['note_type']}")
    print(f"Content Type: {note['content_type'] or 'Not specified'}")
    
    # Check if content is a URL reference
    if note['note_text'].startswith('URL:'):
        print(f"Content: {note['note_text']}")
        print("Note: This content is a URL reference and has not been fetched.")
    elif note['content_type']:
        # Try to decode base64 content
        try:
            binary_content = base64.b64decode(note['note_text'])
            
            # For text content, display it
            if note['content_type'] in ['text/plain', 'text/html', 'text/xml']:
                try:
                    text_content = binary_content.decode('utf-8')
                    print("\nContent Preview:")
                    print(text_content[:500] + ("..." if len(text_content) > 500 else ""))
                except UnicodeDecodeError:
                    print("\nContent is binary and cannot be displayed as text.")
            else:
                print("\nContent is binary and cannot be displayed directly.")
            
            # Save content to file
            filename = save_content_to_file(binary_content, note['content_type'], note['note_id'])
            print(f"\nContent saved to: {filename}")
        except Exception as e:
            print(f"Error decoding content: {e}")
    else:
        # Display text content
        print("\nContent:")
        print(note['note_text'][:500] + ("..." if len(note['note_text']) > 500 else ""))

if __name__ == "__main__":
    main()