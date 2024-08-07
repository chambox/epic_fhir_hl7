from flask import current_app as app
from flask import Flask, request
from flask_restx import Namespace, Resource, fields
from app.services.fhir import FhirService, FhirServiceAuthenticationException, FhirServiceApiException
from app.services.cron import CronService
import json
import hl7

api = Namespace("patient", description="Patient related operations")

patient_data_model = api.model('PatientData', {
    "patient": fields.Raw(required=True, description="Patient Data as returned from the EPIC /Patient endpoint"),
    "medication_statement": fields.Raw(required=True, description="Patient Data as returned from the EPIC /MedicalStatement endpoint"),
})

patient = api.model(
    "Patient",
    {
        "id": fields.String(required=True, description="The Patient Identifier"),
        "data": fields.Nested(patient_data_model, required=False, description="EPIC Data"),
    },
)

patient_list_model = api.model('PatientList', {
    'totalCount': fields.Integer(description='Total number of items'),
    'items': fields.List(fields.Nested(patient), description='List of items')
})

# Define a model for the HL7 ADT message input
hl7_adt_model = api.model('HL7ADTMessage', {
    'adt_message': fields.String(required=True, description='The HL7 ADT message string')
})

PATIENTS = [
    {"id": "erXuFYUfucBZaryVksYEcMg3"},
    {"id": "eq081-VQEgP8drUUqCWzHfw3"},
    {"id": "eAB3mDIBBcyUKviyzrxsnAw3"},
    {"id": "egqBHVfQlt4Bw3XGXoxVxHg3"},
    {"id": "eIXesllypH3M9tAA5WdJftQ3"}
]


@api.route("/list")
class PatientList(Resource):
    @api.doc("list_patients")
    #@api.marshal_list_with(patient_list_model)
    def get(self):
        """List of patients via HL7 with their Patient IDs"""
        return {
            "totalCount": len(PATIENTS),
            "items": PATIENTS
        }


@api.route("/<id>")
@api.param("id", "The Patient Identifier")
@api.response(404, "Patient not Found")
@api.response(500, "An unexpected error against the EPIC API")
class Patient(Resource):
    @api.doc("get_patient")
    @api.marshal_with(patient)
    def get(self, id):
        """Fetch a patient given his Patient ID"""

        try:
            fs = FhirService()
            return {
                "id": id,
                "data": fs.get_aggregate_patient_data(id)
            }
        except FhirServiceAuthenticationException as auth_exp:
            print(auth_exp)
            return auth_exp.to_dict(), api_exp.status_code
        except FhirServiceApiException as api_exp:
            return api_exp.to_dict(), api_exp.status_code


@api.route("/adtmessage/<patient_id>")
@api.param("patient_id", "The Patient Identifier")
@api.response(404, "Patient not Found")
@api.response(500, "An unexpected error against the EPIC API")
class PatientEncounters(Resource):
    @api.doc("get_patient_encounters")
    def get(self, patient_id):
        """Get JSON formatted ADT message, by searching a patient's Encounters, given the Patient ID"""
        try:
            cs = CronService()
            encounters = cs.parse_partient_encounters(id)  # Assuming you have a method for this
            return encounters
        except FhirServiceAuthenticationException as auth_exp:
            print(auth_exp)
            return auth_exp.to_dict(), auth_exp.status_code
        except FhirServiceApiException as api_exp:
            print(api_exp)
            return api_exp.to_dict(), api_exp.status_code


@api.route("/adtmessage/hl7")
@api.expect(hl7_adt_model)
@api.response(400, "Invalid HL7 ADT message")
@api.response(500, "An unexpected error occurred")
class HL7ADTHandler(Resource):
    @api.doc("process_hl7_adt")
    def post(self):
        """Receive raw ADT message, process it and return JSON formatted ADT message (from patient encounters, fetched using patient ID)"""
        try:
            # Get the HL7 ADT message from the JSON payload
            data = request.json
            adt_message = data.get('adt_message')
            if not adt_message:
                return {"error": "ADT message is required"}, 400
            
            # Replace escaped newline characters with actual newline characters
            adt_message = adt_message.replace("\\n", "\n")
            
            # Parse the HL7 message
            hl7_message = hl7.parse(adt_message)

            # Debug: Print all segments
            print("All Segments:")
            for segment in hl7_message:
                print(segment)
                print("Segment Type:",segment[0])
            
            # Extract the patient ID (assuming PID segment and patient ID is in a specific field, e.g., PID-3)
            pid_segment = hl7_message.segment('PID')
            if pid_segment is None:
                return {"error": "PID segment not found in the HL7 message"}, 400
            patient_id = pid_segment[3][0]
            
            # Debug: Print the extracted patient ID
            print("Extracted Patient ID:", patient_id)
            
            # Call the existing patient encounters endpoint with the patient ID
            encounters_resource = PatientEncounters()
            return encounters_resource.get(patient_id)
        except Exception as e:
            print(e)
            return {"error": str(e)}, 500

