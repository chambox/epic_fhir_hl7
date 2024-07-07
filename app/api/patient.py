from flask import current_app as app
from flask_restx import Namespace, Resource, fields
from app.services.fhir_service import FhirService, FhirServiceAuthenticationException, FhirServiceApiException

api = Namespace("patient", description="Patient related operations")

patient = api.model(
    "Patient",
    {
        "id": fields.String(required=True, description="The Patient Identifier"),
        "name": fields.String(required=True, description="The name of the Patient"),
    },
)

PATIENTS = [
    {"id": "eyjSDlddsd-xssf45gg", "name": "Test Patient"},
]


@api.route("/")
class PatientList(Resource):
    @api.doc("list_patients")
    @api.marshal_list_with(patient)
    def get(self):
        """List of patients via HL7 with their Patient IDs"""
        return PATIENTS


@api.route("/<id>")
@api.param("id", "The Patient Identifier")
@api.response(404, "Patient not Found")
@api.response(500, "An unexpected error against the EPIC API")
class Patient(Resource):
    @api.doc("get_patient")
    #@api.marshal_with(patient)
    def get(self, id):
        """Fetch a patient given its identifier"""

        try:
            fs = FhirService()
            return fs.get_aggregate_patient_data(id)
        except FhirServiceAuthenticationException as auth_exp:
            print(auth_exp)
            return auth_exp.to_dict(), api_exp.status_code
        except FhirServiceApiException as api_exp:
            return api_exp.to_dict(), api_exp.status_code

