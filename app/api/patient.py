from flask import current_app as app
from flask_restx import Namespace, Resource, fields
from app.services.fhir import FhirService, FhirServiceAuthenticationException, FhirServiceApiException
from app.services.cron import CronService
import json

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
        """Fetch a patient given its identifier"""

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



@api.route("/encounters/<id>")
@api.param("id", "The Patient Identifier")
@api.response(404, "Patient not Found")
@api.response(500, "An unexpected error against the EPIC API")
class PatientEncounters(Resource):
    @api.doc("get_patient_ecounters")
    # @api.marshal_with(patient)
    def get(self, id):
        """Fetch a patient given its identifier"""

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

