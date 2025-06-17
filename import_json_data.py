import json
import sqlite3
import os

def load_json_file(file_path):
    """Load a JSON file and return its contents"""
    with open(file_path, 'r') as file:
        return json.load(file)

def connect_to_db():
    """Connect to the SQLite database"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'healthcare.db')
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at {db_path}. Please run db_connect.py first.")
    return sqlite3.connect(db_path)

def import_medication(conn, medication_data):
    """Import medication data from medication.json"""
    cursor = conn.cursor()
    
    # Check if medication already exists
    cursor.execute("SELECT medication_id FROM medication WHERE medication_id_external = ?", (medication_data['id'],))
    if cursor.fetchone():
        print(f"Medication {medication_data['id']} already exists, skipping...")
        return
    
    # Extract medication data
    medication_id_external = medication_data['id']
    medication = medication_data['code']['coding'][0]['display'] if 'code' in medication_data and 'coding' in medication_data['code'] else None
    
    # Extract form data
    form = None
    if 'doseForm' in medication_data and 'coding' in medication_data['doseForm']:
        form = medication_data['doseForm']['coding'][0]['display']
    
    # Extract ingredient and strength
    ingredient = None
    strength = None
    if 'ingredient' in medication_data and medication_data['ingredient']:
        ing_data = medication_data['ingredient'][0]
        if 'item' in ing_data and 'concept' in ing_data['item'] and 'coding' in ing_data['item']['concept']:
            ingredient = ing_data['item']['concept']['coding'][0]['display']
        if 'strengthRatio' in ing_data:
            numerator = ing_data['strengthRatio'].get('numerator', {})
            denominator = ing_data['strengthRatio'].get('denominator', {})
            num_value = numerator.get('value')
            num_unit = numerator.get('code')
            if num_value and num_unit:
                strength = f"{num_value} {num_unit}"
    
    # Extract manufacturer
    manufacturer = None
    if 'marketingAuthorizationHolder' in medication_data and 'reference' in medication_data['marketingAuthorizationHolder']:
        ref = medication_data['marketingAuthorizationHolder']['reference']
        if ref.startswith('#'):
            org_id = ref[1:]
            for contained in medication_data.get('contained', []):
                if contained['id'] == org_id and contained['resourceType'] == 'Organization':
                    manufacturer = contained.get('name')
    
    # Insert medication data
    cursor.execute("""
    INSERT INTO medication (medication_id_external, medication, form, ingredient, strength, manufacturer)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (medication_id_external, medication, form, ingredient, strength, manufacturer))
    
    conn.commit()
    print(f"Imported medication: {medication_id_external}")

def import_medication_request(conn, request_data):
    """Import medication request data from medication_request.json"""
    cursor = conn.cursor()
    
    # Check if request already exists
    cursor.execute("SELECT medication_request_id FROM medication_request WHERE medication_request_id_external = ?", (request_data['id'],))
    if cursor.fetchone():
        print(f"Medication request {request_data['id']} already exists, skipping...")
        return
    
    # Extract medication reference
    medication_id = None
    medication = None
    if 'contained' in request_data:
        for contained in request_data['contained']:
            if contained['resourceType'] == 'Medication':
                medication_id = contained['id']
                if 'code' in contained and 'coding' in contained['code']:
                    medication = contained['code']['coding'][0]['display']
    
    # Extract basic information
    medication_request_id_external = request_data['id']
    status = request_data.get('status')
    # patient_id = request_data['subject']['reference'].split('/')[-1] if 'subject' in request_data else None
    practitioner_id = request_data['requester']['reference'].split('/')[-1] if 'requester' in request_data else None
    encounter_id = request_data['encounter']['reference'].split('/')[-1] if 'encounter' in request_data else None
    authored_on = request_data.get('authoredOn')
    # note = request_data['note'][0]['text'] if 'note' in request_data and request_data['note'] else None
    
    # Extract dosage information
    dosage_text = None
    dosage_route = None
    dosage_method = None
    dosage_quantity = None
    dosage_unit = None
    timing_frequency = None
    timing_period = None
    timing_period_unit = None
    timing_start = None
    timing_end = None
    
    if 'dosageInstruction' in request_data and request_data['dosageInstruction']:
        dosage = request_data['dosageInstruction'][0]
        dosage_text = dosage.get('text')
        
        if 'route' in dosage and 'coding' in dosage['route']:
            dosage_route = dosage['route']['coding'][0]['display']
        
        if 'method' in dosage and 'coding' in dosage['method']:
            dosage_method = dosage['method']['coding'][0]['display']
        
        if 'doseAndRate' in dosage and dosage['doseAndRate']:
            dose_rate = dosage['doseAndRate'][0]
            if 'doseQuantity' in dose_rate:
                dosage_quantity = dose_rate['doseQuantity'].get('value')
                dosage_unit = dose_rate['doseQuantity'].get('code')
        
        if 'timing' in dosage and 'repeat' in dosage['timing']:
            repeat = dosage['timing']['repeat']
            timing_frequency = repeat.get('frequency')
            timing_period = repeat.get('period')
            timing_period_unit = repeat.get('periodUnit')
            if 'boundsPeriod' in repeat:
                timing_start = repeat['boundsPeriod'].get('start')
                timing_end = repeat['boundsPeriod'].get('end')
    
    # Insert request data
    cursor.execute("""
    INSERT INTO medication_request (
        medication_request_id_external, medication_id, medication, status,
        practitioner_id, encounter_id, authored_on, dosage_text, dosage_route,
        dosage_method, dosage_quantity, dosage_unit, timing_frequency, timing_period,
        timing_period_unit, timing_start, timing_end
    ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        medication_request_id_external, medication_id, medication, status,
        practitioner_id, encounter_id, authored_on, dosage_text, dosage_route,
        dosage_method, dosage_quantity, dosage_unit, timing_frequency, timing_period,
        timing_period_unit, timing_start, timing_end,  
    ))
    
    conn.commit()
    print(f"Imported medication request: {medication_request_id_external}")

def import_medication_administration(conn, admin_data):
    """Import medication administration data from medication_administration.json"""
    cursor = conn.cursor()
    
    # Check if administration already exists
    cursor.execute("SELECT medication_administration_id FROM medication_administration WHERE medication_administration_id_external = ?", (admin_data['id'],))
    if cursor.fetchone():
        print(f"Medication administration {admin_data['id']} already exists, skipping...")
        return
    
    # Extract medication reference
    medication_id = None
    medication_display = None
    if 'contained' in admin_data:
        for contained in admin_data['contained']:
            if contained['resourceType'] == 'Medication':
                medication_id = contained['id']
                if 'code' in contained and 'coding' in contained['code']:
                    medication_display = contained['code']['coding'][0]['display']
    
    # Extract basic information
    medication_administration_id_external = admin_data['id']
    status = admin_data.get('status')
    # patient_id = admin_data['subject']['reference'].split('/')[-1] if 'subject' in admin_data else None
    practitioner_id = admin_data['performer'][0]['actor']['reference']['reference'].split('/')[-1] if 'performer' in admin_data and admin_data['performer'] else None
    request_id = admin_data['request']['reference'].split('/')[-1] if 'request' in admin_data else None
    encounter_id = admin_data['encounter']['reference'].split('/')[-1] if 'encounter' in admin_data else None
    
    # Extract timing
    effective_start = None
    effective_end = None
    if 'occurencePeriod' in admin_data:
        effective_start = admin_data['occurencePeriod'].get('start')
        effective_end = admin_data['occurencePeriod'].get('end')
    
    # Extract dosage information
    dosage_text = None
    dosage_route = None
    dosage_method = None
    dosage_quantity = None
    dosage_unit = None
    
    if 'dosage' in admin_data:
        dosage = admin_data['dosage']
        dosage_text = dosage.get('text')
        
        if 'route' in dosage and 'coding' in dosage['route']:
            dosage_route = dosage['route']['coding'][0]['display']
        
        if 'method' in dosage and 'coding' in dosage['method']:
            dosage_method = dosage['method']['coding'][0]['display']
        
        if 'dose' in dosage:
            dosage_quantity = dosage['dose'].get('value')
            dosage_unit = dosage['dose'].get('code')
    
    # Insert administration data
    cursor.execute("""
    INSERT INTO medication_administration (
        medication_administration_id_external, medication_id, medication_display, status,
         practitioner_id, request_id, encounter_id, effective_start,
        effective_end, dosage_text, dosage_route, dosage_method, dosage_quantity,
        dosage_unit
    ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        medication_administration_id_external, medication_id, medication_display, status,
         practitioner_id, request_id, encounter_id, effective_start,
        effective_end, dosage_text, dosage_route, dosage_method, dosage_quantity,
        dosage_unit
    ))
    
    conn.commit()
    print(f"Imported medication administration: {medication_administration_id_external}")

def main():
    """Main function to import all medication-related data"""
    conn = connect_to_db()
    
    try:
        # Import medication data
        medication_data = load_json_file('medication.json')
        import_medication(conn, medication_data)
        
        # Import medication request data
        request_data = load_json_file('medication_request.json')
        import_medication_request(conn, request_data)
        
        # Import medication administration data
        admin_data = load_json_file('medication_administration.json')
        import_medication_administration(conn, admin_data)
        
        print("Data import completed successfully!")
        
    except Exception as e:
        print(f"Error during import: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
