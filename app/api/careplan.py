from flask import current_app as app
from flask_restx import Namespace, Resource, fields, reqparse
from app.services.fhir import (
    FhirService,
    FhirServiceAuthenticationException,
    FhirServiceApiException,
)
from app.dao.epic_careplan import EpicCarePlanDao

api = Namespace("careplan", description="CarePlan related operations")

parser = reqparse.RequestParser()
parser.add_argument(
    "patient",
    required=False,
    location="args",
    type=str,
    help="Please provide the patient ID as a string",
)
parser.add_argument("category", required=True, location="args")
parser.add_argument("encounter", location="args")


@api.route("/search")
class CarePlanSearch(Resource):
    # @api.marshal_list_with(patient_list_model)
    @api.doc(
        params={
            "category": {
                "required": True,
                "description": """Types of plan:
            - **care-path**: Care path 
            - **38717003**:  Longitudinal care plans. Patient: e0yyMZa5aqjpDhvmIODSJgw3
            - **738906000**: Dental plan. Patient: evsJR7wUkBvPXgtZSwj8jNQ3
            - **734163000**: Encounter Level care plan. Patient: erXuFYUfucBZaryVksYEcMg3 Encounter: elMz2mwjsRvKnZiR.0ceTUg3
            - **inpatient-pathway**: Inpatient pathway
            - **736353004**: Inpatient care plan (record artifact). Patient: eTRO.ZVFuhUxXw6HzTAjtfg3
            - **736378000**: Oncology care plan. Patient: ePGJfjiWayus47VRmNLCBcA3
            - **736271009**: Outpatient care plans. Patient: egxlDFt6t8n-cRqg1k0NObg3
            - **409073007**: Patient Education CarePlan. Patient: eTRO.ZVFuhUxXw6HzTAjtfg3
            """,
            },
            "patient": {"required": True, "description": "The ID of the patient"},
            "encounter": {
                "description": "Encounter ID in case of Encounter level careplan"
            },
        }
    )
    def get(self):
        try:
            return EpicCarePlanDao.search_data(parser.parse_args(strict=True))
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
    # @api.marshal_with(patient)
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
