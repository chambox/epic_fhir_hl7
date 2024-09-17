from flask import current_app as app
from flask_restx import Namespace, Resource, fields, reqparse
from app.services.fhir import (
    FhirService,
    FhirServiceAuthenticationException,
    FhirServiceApiException,
)

api = Namespace("location", description="Location related operations")


@api.route("/<id>")
@api.param("id", "The Location Identifier")
@api.response(404, "Location not Found")
@api.response(500, "An unexpected error against the EPIC API")
class Location(Resource):
    # @api.marshal_with(patient)
    def get(self, id):
        """Fetch an encouter given its identifier"""

        try:
            fs = FhirService()
            return fs.get_location(id)
        except FhirServiceAuthenticationException as auth_exp:
            print(auth_exp)
            return auth_exp.to_dict(), api_exp.status_code
        except FhirServiceApiException as api_exp:
            return api_exp.to_dict(), api_exp.status_code
