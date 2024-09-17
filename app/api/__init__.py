from flask_restx import Api

from app.api.patient import api as patient_api
from app.api.encounter import api as encounter_api
from app.api.organization import api as organization_api
from app.api.location import api as location_api
from app.api.careplan import api as careplan_api
from app.api.adtmessage import api as adtmessage_api

# Define API object with entry point
api = Api(
    title="Data Fetch from EPIC (POC)",
    version="1.0",
    description="Fetch data from EPIC and transfer to TnT",
    prefix="/api",
)

# Register namespaces
api.add_namespace(patient_api)
api.add_namespace(encounter_api)
api.add_namespace(organization_api)
api.add_namespace(location_api)
api.add_namespace(careplan_api)
api.add_namespace(adtmessage_api)
