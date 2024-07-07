import jwt
import time
import uuid
import requests
from config import Config

class FhirService(object):

    auth_token = None

        
    def authenticate(self):
        payload = {
            "iss": Config.EPIC_CLIENT_ID,
            "sub": Config.EPIC_CLIENT_ID,
            "aud": f"{Config.EPIC_API_URL}/oauth2/token",
            "exp": int(time.time()) + 300,
            "jti": str(uuid.uuid4())
        }

        with open(Config.EPIC_API_PRIVATE_KEY_PATH, "r") as key_file:
            private_key = key_file.read()

        token = jwt.encode(payload, private_key, algorithm="RS256")

        url = f"{Config.EPIC_API_URL}/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": token,
            "scope": "patient/*" 
        }

        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            raise FhirServiceAuthenticationException(response.content, response.status_code)

        res = response.json()
        return res.get('access_token')
    
    def get_auth_token(self):
        if self.auth_token is None:
            self.auth_token = self.authenticate()
        
        return self.auth_token

    def get_request_headers(self):
        return {
            "Authorization": f"Bearer {self.get_auth_token()}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_aggregate_patient_data(self, patient_id):
        patient_data = {}

        patient = self.get_patient(patient_id)
        if patient:
            patient_data['patient'] = patient
        
        medication_statement = self.get_medication_statement(patient_id)
        if medication_statement:
            patient_data['medication_statement'] = medication_statement
        
        return patient_data
        

    def get_patient(self, patient_id):
        url = f"{Config.EPIC_API_URL}/api/FHIR/R4/Patient/{patient_id}"
        headers = self.get_request_headers()

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            # @TODO Log error
            raise FhirServiceApiException(f"Error fetching data from {response.url}: {response.status_code}", response.status_code)

    def get_medication_statement(self, patient_id):
        url = f"{Config.EPIC_API_URL}/api/FHIR/STU3/MedicationStatement?patient={patient_id}"
        headers = self.get_request_headers()

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise FhirServiceApiException(f"Error fetching data from {response.url}: {response.status_code}", response.status_code)


# Service Exception Classes

class FhirServiceException(Exception):
    status_code = 500

    def __init__(self, message, status_code=None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        self.message = message

    def to_dict(self):
        return {"message": self.message}

class FhirServiceAuthenticationException(FhirServiceException):
    pass

class FhirServiceApiException(FhirServiceException):
    pass
