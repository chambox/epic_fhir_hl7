from os import getenv

class Config:
    EPIC_API_URL=getenv('EPIC_API_URL')
    EPIC_API_PRIVATE_KEY_PATH=getenv('EPIC_API_PRIVATE_KEY_PATH')
    EPIC_CLIENT_ID=getenv('EPIC_CLIENT_ID')
    EPIC_FHIR_GROUP_ID=getenv('EPIC_FHIR_GROUP_ID')
    