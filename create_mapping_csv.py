import pandas as pd
from typing import Dict, List
from pathlib import Path

def create_mapping_csvs():
    # Create output directory if it doesn't exist
    output_dir = Path('mapping_files')
    output_dir.mkdir(exist_ok=True)

    # Note Table Mappings
    note_mappings = {
        'Table/Column': [
            'note.note_id',
            'note.note_id_external',
            'note.category_id',
            'note.note_type',
            'note.note_type_code',
            'note.encounter_id',
            'note.provider_id',
            'note.note_date',
            'note.current_version_id',
            'note.is_active',
            'note.created_at',
            'note.updated_at'
        ],
        'Description': [
            'Primary key',
            'External source identifier',
            'Reference to category',
            'Type of note',
            'Standardized type code',
            'Reference to encounter',
            'Reference to provider',
            'Date of note',
            'Current version reference',
            'Active status flag',
            'Creation timestamp',
            'Last update timestamp'
        ],
        'HL7 FHIR Path': [
            'DocumentReference.id',
            'DocumentReference.identifier',
            'DocumentReference.category[0].coding[0]',
            'DocumentReference.type.coding[0].display',
            'DocumentReference.type.coding[0].code',
            'DocumentReference.context.encounter.reference',
            'DocumentReference.author.reference',
            'DocumentReference.date',
            'DocumentReference.meta.versionId',
            'DocumentReference.status',
            'DocumentReference.meta.created',
            'DocumentReference.meta.lastUpdated'
        ],
        'Epic FHIR Path': [
            'Epic.DocumentReference.id',
            'Epic.DocumentReference.identifier[0].value',
            'Epic.DocumentReference.category.code',
            'Epic.DocumentReference.type.text',
            'Epic.DocumentReference.type.code',
            'Epic.DocumentReference.visit.reference',
            'Epic.DocumentReference.author.reference',
            'Epic.DocumentReference.serviceDate',
            'Epic.DocumentReference.version',
            'Epic.DocumentReference.status',
            'Epic.DocumentReference.created',
            'Epic.DocumentReference.updated'
        ],
        'Cerner FHIR Path': [
            'Cerner.DocumentReference.id',
            'Cerner.DocumentReference.identifier[0].value',
            'Cerner.DocumentReference.category[0].coding[0]',
            'Cerner.DocumentReference.type.display',
            'Cerner.DocumentReference.type.code',
            'Cerner.DocumentReference.context.reference',
            'Cerner.DocumentReference.author.reference',
            'Cerner.DocumentReference.created',
            'Cerner.DocumentReference.version',
            'Cerner.DocumentReference.status',
            'Cerner.DocumentReference.meta.created',
            'Cerner.DocumentReference.meta.lastUpdated'
        ]
    }

    # Note Version Table Mappings
    note_version_mappings = {
        'Table/Column': [
            'note_version.version_id',
            'note_version.note_id',
            'note_version.version_number',
            'note_version.note_text',
            'note_version.author_id',
            'note_version.created_at'
        ],
        'Description': [
            'Primary key for version',
            'Reference to note',
            'Version number',
            'Note content',
            'Author of version',
            'Version creation time'
        ],
        'HL7 FHIR Path': [
            'DocumentReference.meta.versionId',
            'DocumentReference.id',
            'DocumentReference.meta.versionId',
            'DocumentReference.content[0].attachment.data',
            'DocumentReference.author.reference',
            'DocumentReference.date'
        ],
        'Epic FHIR Path': [
            'Epic.DocumentReference.version',
            'Epic.DocumentReference.id',
            'Epic.DocumentReference.version',
            'Epic.DocumentReference.content.data',
            'Epic.DocumentReference.author.reference',
            'Epic.DocumentReference.created'
        ],
        'Cerner FHIR Path': [
            'Cerner.DocumentReference.version',
            'Cerner.DocumentReference.id',
            'Cerner.DocumentReference.version',
            'Cerner.DocumentReference.content[0].attachment.data',
            'Cerner.DocumentReference.author.reference',
            'Cerner.DocumentReference.created'
        ]
    }

    # Category Table Mappings
    category_mappings = {
        'Table/Column': [
            'note_category.category_id',
            'note_category.category_code',
            'note_category.category_display',
            'note_category.loinc_code',
            'note_category.is_active'
        ],
        'Description': [
            'Primary key for category',
            'Category code',
            'Display name',
            'LOINC code reference',
            'Active status'
        ],
        'HL7 FHIR Path': [
            'DocumentReference.category[0].id',
            'DocumentReference.category[0].coding[0].code',
            'DocumentReference.category[0].coding[0].display',
            'DocumentReference.category[0].coding[0].code',
            'DocumentReference.category[0].coding[0].active'
        ],
        'Epic FHIR Path': [
            'Epic.DocumentReference.category.id',
            'Epic.DocumentReference.category.code',
            'Epic.DocumentReference.category.display',
            'Epic.DocumentReference.category.code',
            'Epic.DocumentReference.category.active'
        ],
        'Cerner FHIR Path': [
            'Cerner.DocumentReference.category[0].id',
            'Cerner.DocumentReference.category[0].code',
            'Cerner.DocumentReference.category[0].display',
            'Cerner.DocumentReference.category[0].code',
            'Cerner.DocumentReference.category[0].active'
        ]
    }

    # Write each mapping to separate CSV files
    pd.DataFrame(note_mappings).to_csv(output_dir / 'note_mappings.csv', index=False)
    pd.DataFrame(note_version_mappings).to_csv(output_dir / 'note_version_mappings.csv', index=False)
    pd.DataFrame(category_mappings).to_csv(output_dir / 'category_mappings.csv', index=False)

    print("CSV mapping files created successfully in 'mapping_files' directory!")

if __name__ == "__main__":
    create_mapping_csvs()
