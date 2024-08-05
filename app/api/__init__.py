from flask_restx import Api

from .patient import api as patient_api
from .encounter import api as encounter_api
from .organization import api as organization_api
from .location import api as location_api
from .careplan import api as careplan_api

# Define API object with entry point
api = Api(
    title="Data Fetch from EPIC (POC)",
    version="1.0",
    description="Fetch data from EPIC and transfer to TnT",
    prefix="/api"
)

# Register namespaces
api.add_namespace(patient_api)
api.add_namespace(encounter_api)
api.add_namespace(organization_api)
api.add_namespace(location_api)
api.add_namespace(careplan_api)
