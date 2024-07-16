from flask import current_app as app
from flask_restx import Namespace, Resource, fields, reqparse
from app.services.fhir_service import FhirService, FhirServiceAuthenticationException, FhirServiceApiException

api = Namespace("encounter", description="Encounter related operations")

parser = reqparse.RequestParser()
parser.add_argument('patient')
parser.add_argument('type')

@api.route("/search")
class EncounterSearch(Resource):
    @api.doc(params={
        'patient': 'The ID of the patient',
        'type': "enum {inpatient, outpatient}"
    })
    #@api.marshal_list_with(patient_list_model)
    def get(self):
        """Search List of patient encounters given patient id"""
        data = parser.parse_args()
        fs = FhirService()
        return fs.search_encounter(data)


@api.route("/<id>")
@api.param("id", "The Encounter Identifier")
@api.response(404, "Encounter not Found")
@api.response(500, "An unexpected error against the EPIC API")
class Encounter(Resource):
    @api.doc(params={
        'type': "enum {inpatient, outpatientt}",
    })
    #@api.marshal_with(patient)
    def get(self, id):
        """Fetch an encouter given its identifier"""

        try:
            fs = FhirService()
            return fs.get_encounter(id)
        except FhirServiceAuthenticationException as auth_exp:
            print(auth_exp)
            return auth_exp.to_dict(), api_exp.status_code
        except FhirServiceApiException as api_exp:
            return api_exp.to_dict(), api_exp.status_code

