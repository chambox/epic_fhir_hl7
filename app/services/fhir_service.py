import jwt
import time
import uuid
import requests
from flask import current_app as app

class FhirService(object):

    config = {}

    auth_token = None

    def __init__(self, config) -> None:
        self.config = config
        
    def authenticate(self):
        payload = {
            "iss": self.config['EPIC_CLIENT_ID'],
            "sub": self.config['EPIC_CLIENT_ID'],
            "aud": self.config['EPIC_API_URL'],
            "exp": int(time.time()) + 300,
            "jti": str(uuid.uuid4())
        }

        with open(self.config["EPIC_API_PRIVATE_KEY_PATH"], "r") as key_file:
            private_key = key_file.read()

        token = jwt.encode(payload, private_key, algorithm="RS256")

        url = self.config['EPIC_API_URL']
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": token,
            "scope": "patient/*" 
        }

        response = requests.post(url, headers=headers, data=data)
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
        url = f"{self.config['EPIC_API_URL']}/api/FHIR/R4/Patient/{patient_id}"
        headers = self.get_request_headers()

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            # @TODO raise exception
            # Log error
            print(f"Error fetching data from {response.url}: {response.status_code}")
            return None

    def get_medication_statement(self, patient_id):
        url = f"{self.config['EPIC_API_URL']}/api/FHIR/STU3/MedicationStatement?patient={patient_id}"
        headers = self.get_request_headers()

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data from {response.url}: {response.status_code}")
            return None
