import jwt
import time
import uuid
import requests

def authenticate():
    payload = {
        "iss": "65626506-c4ac-4ad6-a69e-c1f15c763ab7",
        "sub": "65626506-c4ac-4ad6-a69e-c1f15c763ab7",
        "aud": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token",
        "exp": int(time.time()) + 300,
        "jti": str(uuid.uuid4())
    }
    with open("./.pem/tntpic.pem", "r") as key_file:
        private_key = key_file.read()

    token = jwt.encode(payload, private_key, algorithm="RS256")

    url = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
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

def get_aggregate_patient_data(patient_id):
    jwt_token = authenticate()
    data_endpoints = [
        f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient/{patient_id}",
        f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/STU3/MedicationStatement?patient={patient_id}",
        # Add more FHIR endpoints here
    ]
    patient_data = {}
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    for endpoint in data_endpoints:
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            patient_data[endpoint.split('/')[-1]] = response.json()
        else:
            print(f"Error fetching data from {endpoint}: {response.status_code}")
    return patient_data
