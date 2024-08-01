from flask import current_app as app
from flask_restx import Namespace, Resource, fields, reqparse
from app.services.fhir import FhirService, FhirServiceAuthenticationException, FhirServiceApiException
from app.services.cron import CronService

api = Namespace("careplan", description="CarePlan related operations")

parser = reqparse.RequestParser()
parser.add_argument('patient', required=False, location='args', type=str, help="Please provide the patient ID as a string")
parser.add_argument('category', required=True, location='args')

@api.route("/search")
class CarePlanSearch(Resource):
    #@api.marshal_list_with(patient_list_model)
    @api.doc(params={
        'category': 'Type of plan. 38717003 should be used to search for longitudinal care plans',
        'patient': 'The ID of the patient',
    })
    def get(self):
        try:

            fs = FhirService()
            return fs.search_careplan(parser.parse_args(strict=True))
        except FhirServiceAuthenticationException as auth_exp:
            print(auth_exp)
            return auth_exp.to_dict(), api_exp.status_code
        except FhirServiceApiException as api_exp:
            return api_exp.to_dict(), api_exp.status_code


@api.route("/<id>")
@api.param("id", "The CarePlan Identifier")
@api.response(404, "CarePlan not Found")
@api.response(500, "An unexpected error against the EPIC API")
class CarePlan(Resource):
    #@api.marshal_with(patient)
    def get(self, id):
        """Fetch a care plan given its identifier"""

        try:
            fs = FhirService()
            return fs.get_careplan(id)
        except FhirServiceAuthenticationException as auth_exp:
            print(auth_exp)
            return auth_exp.to_dict(), api_exp.status_code
        except FhirServiceApiException as api_exp:
            return api_exp.to_dict(), api_exp.status_code

