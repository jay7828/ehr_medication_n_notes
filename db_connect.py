import sqlite3
import os

def create_healthcare_database():
    # Define the path to the database file
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'healthcare.db')
    
    # Define the path to the schema file
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'healthcare_sqlite_schema.sql')
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clinical_notes_schema_corrected.sql')
    
    # Check if the database file already exists
    if os.path.exists(db_path):
        print(f"Database already exists at {db_path}")
        choice = input("Do you want to recreate the database? (y/n): ")
        if choice.lower() != 'y':
            print("Exiting without recreating the database.")
            return
        else:
            os.remove(db_path)
            print("Existing database removed.")
    
    # Connect to the SQLite database (this will create the file if it doesn't exist)
    print(f"Creating new database at {db_path}")
    conn = sqlite3.connect(db_path)
    
    try:
        # Read the schema file
        with open(schema_path, 'r') as f:
            schema_script = f.read()
        
        # Execute the schema script
        conn.executescript(schema_script)
        
        # Commit the changes
        conn.commit()
        
        print("Database created successfully with all tables and indexes.")
        
        # # Insert some sample data (optional)
        # print("Would you like to add some sample data? (y/n): ")
        # choice = input()
        # if choice.lower() == 'y':
        #     insert_sample_data(conn)
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        conn.close()


if __name__ == '__main__':
    create_healthcare_database()
