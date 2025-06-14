# FHIR to Database Mapping

This document provides a detailed mapping between FHIR resources in JSON format and our SQLite database schema. It shows how each FHIR data element is mapped to corresponding database tables and columns.

## Table of Contents

1. [Medication Resource](#medication-resource)
2. [MedicationRequest Resource](#medicationrequest-resource)
3. [MedicationAdministration Resource](#medicationadministration-resource)
4. [Patient Resource](#patient-resource)
5. [Practitioner Resource](#practitioner-resource)
6. [Encounter Resource](#encounter-resource)

## Medication Resource

Source: `medication.json`

| FHIR Path | Database Table | Database Column | Notes |
|-----------|----------------|-----------------|-------|
| `resourceType` | N/A | N/A | Used to identify the resource type |
| `id` | Medication | id | Primary key |
| `code.coding[0].system` | Medication | system | Coding system for medication code |
| `code.coding[0].code` | Medication | code | Medication code |
| `code.coding[0].display` | Medication | display | Human-readable medication name |
| `doseForm.coding[0].system` | Medication | form_system | Coding system for dose form |
| `doseForm.coding[0].code` | Medication | form_code | Dose form code |
| `doseForm.coding[0].display` | Medication | form | Human-readable dose form |
| `contained[*].resourceType="Organization"` | N/A | N/A | Contained resource |
| `contained[*].id` | N/A | N/A | Reference to contained resource |
| `contained[*].name` | Medication | manufacturer | Manufacturer name |
| `marketingAuthorizationHolder.reference` | N/A | N/A | Reference to manufacturer |
| `batch.lotNumber` | Medication | lot_number | Batch lot number |
| `batch.expirationDate` | Medication | expiration_date | Batch expiration date |
| `ingredient[*].item.concept.coding[0].system` | Substance | system | Coding system for substance |
| `ingredient[*].item.concept.coding[0].code` | Substance | code | Substance code |
| `ingredient[*].item.concept.coding[0].display` | Substance | display | Human-readable substance name |
| `ingredient[*].strengthRatio.numerator.value` | MedicationIngredient | strength_numerator_value | Strength numerator value |
| `ingredient[*].strengthRatio.numerator.system` | MedicationIngredient | strength_numerator_system | Coding system for numerator unit |
| `ingredient[*].strengthRatio.numerator.code` | MedicationIngredient | strength_numerator_unit | Numerator unit |
| `ingredient[*].strengthRatio.denominator.value` | MedicationIngredient | strength_denominator_value | Strength denominator value |
| `ingredient[*].strengthRatio.denominator.system` | MedicationIngredient | strength_denominator_system | Coding system for denominator unit |
| `ingredient[*].strengthRatio.denominator.code` | MedicationIngredient | strength_denominator_unit | Denominator unit |

## MedicationRequest Resource

Source: `medication_request.json`

| FHIR Path | Database Table | Database Column | Notes |
|-----------|----------------|-----------------|-------|
| `resourceType` | N/A | N/A | Used to identify the resource type |
| `id` | MedicationRequest | id | Primary key |
| `status` | MedicationRequest | status | Request status (active, completed, etc.) |
| `intent` | MedicationRequest | intent | Request intent (order, plan, etc.) |
| `authoredOn` | MedicationRequest | authoredOn | Date when request was created |
| `medication.reference.reference` | MedicationRequest | medicationId | Reference to medication (FK) |
| `subject.reference` | MedicationRequest | patientId | Reference to patient (FK) |
| `subject.display` | N/A | N/A | Display name of patient |
| `encounter.reference` | MedicationRequest | encounterId | Reference to encounter (FK) |
| `encounter.display` | N/A | N/A | Display description of encounter |
| `requester.reference` | MedicationRequest | practitionerId | Reference to practitioner (FK) |
| `requester.display` | N/A | N/A | Display name of practitioner |
| `note[*].text` | MedicationRequest | note | Additional notes |
| `dosageInstruction[*].sequence` | DosageInstruction | sequence | Order of dosage instructions |
| `dosageInstruction[*].text` | DosageInstruction | text | Text instructions |
| `dosageInstruction[*].timing.repeat.boundsPeriod.start` | DosageInstruction | timing | Start of timing period (part of timing string) |
| `dosageInstruction[*].timing.repeat.boundsPeriod.end` | DosageInstruction | timing | End of timing period (part of timing string) |
| `dosageInstruction[*].timing.repeat.frequency` | DosageInstruction | timing | Frequency (part of timing string) |
| `dosageInstruction[*].timing.repeat.period` | DosageInstruction | timing | Period (part of timing string) |
| `dosageInstruction[*].timing.repeat.periodUnit` | DosageInstruction | timing | Period unit (part of timing string) |
| `dosageInstruction[*].route.coding[0].system` | DosageInstruction | route_system | Coding system for route |
| `dosageInstruction[*].route.coding[0].code` | DosageInstruction | route_code | Route code |
| `dosageInstruction[*].route.coding[0].display` | DosageInstruction | route | Human-readable route |
| `dosageInstruction[*].method.coding[0].system` | DosageInstruction | method_system | Coding system for method |
| `dosageInstruction[*].method.coding[0].code` | DosageInstruction | method_code | Method code |
| `dosageInstruction[*].method.coding[0].display` | DosageInstruction | method | Human-readable method |
| `dosageInstruction[*].doseAndRate[0].doseQuantity.value` | DosageInstruction | doseQuantity | Dose quantity value |
| `dosageInstruction[*].doseAndRate[0].doseQuantity.unit` | DosageInstruction | doseUnit | Dose unit |

## MedicationAdministration Resource

Source: `medication_administration.json`

| FHIR Path | Database Table | Database Column | Notes |
|-----------|----------------|-----------------|-------|
| `resourceType` | N/A | N/A | Used to identify the resource type |
| `id` | MedicationAdministration | id | Primary key |
| `status` | MedicationAdministration | status | Administration status |
| `medication.reference.reference` | MedicationAdministration | medicationId | Reference to medication (FK) |
| `subject.reference` | MedicationAdministration | patientId | Reference to patient (FK) |
| `subject.display` | N/A | N/A | Display name of patient |
| `encounter.reference` | MedicationAdministration | encounterId | Reference to encounter (FK) |
| `encounter.display` | N/A | N/A | Display description of encounter |
| `occurencePeriod.start` | MedicationAdministration | effectiveDateTime | Start time of administration |
| `occurencePeriod.end` | N/A | N/A | End time of administration (not stored) |
| `performer[*].actor.reference.reference` | MedicationAdministration | practitionerId | Reference to practitioner (FK) |
| `performer[*].actor.reference.display` | N/A | N/A | Display name of practitioner |
| `request.reference` | MedicationAdministration | requestId | Reference to medication request (FK) |
| `dosage.text` | N/A | N/A | Text description of dosage |
| `dosage.route.coding[0].system` | MedicationAdministration | dosageRoute_system | Coding system for route |
| `dosage.route.coding[0].code` | MedicationAdministration | dosageRoute_code | Route code |
| `dosage.route.coding[0].display` | MedicationAdministration | dosageRoute | Human-readable route |
| `dosage.method.coding[0].system` | MedicationAdministration | dosageMethod_system | Coding system for method |
| `dosage.method.coding[0].code` | MedicationAdministration | dosageMethod_code | Method code |
| `dosage.method.coding[0].display` | MedicationAdministration | dosageMethod | Human-readable method |
| `dosage.dose.value` | MedicationAdministration | dosageQuantity | Dose quantity value |
| `dosage.dose.unit` | MedicationAdministration | dosageUnit | Dose unit |
| `dosage.dose.system` | N/A | N/A | Coding system for dose unit (not stored) |
| `dosage.dose.code` | N/A | N/A | Dose unit code (not stored) |

## Patient Resource

Source: Referenced in other resources

| FHIR Path | Database Table | Database Column | Notes |
|-----------|----------------|-----------------|-------|
| `id` | Patient | id | Primary key |
| `name` | Patient | name | Patient name |
| `birthDate` | Patient | birthDate | Date of birth |
| `gender` | Patient | gender | Gender |
| `address` | Patient | address | Address information |
| `contact` | Patient | contact | Contact information |

## Practitioner Resource

Source: Referenced in other resources

| FHIR Path | Database Table | Database Column | Notes |
|-----------|----------------|-----------------|-------|
| `id` | Practitioner | id | Primary key |
| `name` | Practitioner | name | Practitioner name |
| `qualification` | Practitioner | qualification | Qualifications |
| `specialty` | Practitioner | specialty | Specialty |

## Encounter Resource

Source: Referenced in other resources

| FHIR Path | Database Table | Database Column | Notes |
|-----------|----------------|-----------------|-------|
| `id` | Encounter | id | Primary key |
| `status` | Encounter | status | Encounter status |
| `period.start` | Encounter | period_start | Start time of encounter |
| `period.end` | Encounter | period_end | End time of encounter |
| `subject.reference` | Encounter | patientId | Reference to patient (FK) |
| `type` | Encounter | type | Type of encounter |

## Relationship Mapping

### Foreign Key Relationships

| Database Table | Foreign Key | References | FHIR Relationship |
|----------------|-------------|------------|-------------------|
| Encounter | patientId | Patient.id | Encounter.subject -> Patient |
| MedicationRequest | patientId | Patient.id | MedicationRequest.subject -> Patient |
| MedicationRequest | practitionerId | Practitioner.id | MedicationRequest.requester -> Practitioner |
| MedicationRequest | medicationId | Medication.id | MedicationRequest.medication -> Medication |
| MedicationRequest | encounterId | Encounter.id | MedicationRequest.encounter -> Encounter |icationAdministration.medication -> Medication |
| MedicationAdministration | requestId | MedicationRequest.id | MedicationAdministration.request -> MedicationRequest |
| MedicationAdministration | encounterId | Encounter.id | MedicationAdministration.encounter -> Encounter |
| MedicationAdministration | practitionerId | Practitioner.id | MedicationAdministration.performer.actor -> Practitioner |
| MedicationIngredient | medicationId | Medication.id | Part of Medication |
| MedicationIngredient | substanceId | Substance.id | MedicationIngredient.item -> Substance |

## Data Transformation Notes

1. **Contained Resources**: FHIR allows resources to be contained within other resources. In our database, we extract these into separate tables with appropriate foreign key relationships.

2. **Complex Data Types**: FHIR uses complex data types (like CodeableConcept, Ratio, etc.) which are flattened into multiple columns in our relational database.

3. **References**: FHIR uses references to link resources. These are implemented as foreign keys in our database.

4. **Arrays**: FHIR resources can contain arrays of elements. For simplicity, some arrays (like dosageInstruction) are stored in separate tables with a foreign key back to the parent resource.

5. **Timing**: Complex timing information in FHIR is simplified and stored as text strings in our database.

6. **Coding**: FHIR uses coding systems for standardized values. We store both the code and the human-readable display value, along with the system URI.