from flask import current_app as app
from flask_restx import Namespace, Resource, fields, reqparse
from app.services.fhir import (
    FhirService,
    FhirServiceAuthenticationException,
    FhirServiceApiException,
)

api = Namespace("organization", description="Organization related operations")

parser = reqparse.RequestParser()
parser.add_argument("_id")


@api.route("/search")
class OrganizationSearch(Resource):
    @api.doc(params={"_id": "The configured ID of the organization"})
    # @api.marshal_list_with(patient_list_model)
    def get(self):
        """Search List of patient Organizations"""
        data = parser.parse_args()
        fs = FhirService()
        return fs.search_organization(data)


@api.route("/<id>")
@api.param("id", "The Organization Identifier")
@api.response(404, "Organization not Found")
@api.response(500, "An unexpected error against the EPIC API")
class Organization(Resource):
    # @api.marshal_with(patient)
    def get(self, id):
        """Fetch an encouter given its identifier"""

        try:
            fs = FhirService()
            return fs.get_organization(id)
        except FhirServiceAuthenticationException as auth_exp:
            print(auth_exp)
            return auth_exp.to_dict(), api_exp.status_code
        except FhirServiceApiException as api_exp:
            return api_exp.to_dict(), api_exp.status_code
