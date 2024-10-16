## EPIC - TNT Bridge Development

### 1. Configure Environment Variables

```
# EPIC Api URL to fetch epic data
EPIC_API_URL="https://fhir.epic.com/interconnect-fhir-oauth"

# Public key as configured on the Epic App
EPIC_API_PRIVATE_KEY_PATH="/home/ctata/epic_fhir_hl7/.pem/tntpic.pem"

# Client ID of the EPIC App
EPIC_CLIENT_ID="65626506-c4ac-4ad6-a69e-c1f15c763ab7"

# TNT backend entry point URL to receive adt message
TNT_RECEIVE_ENDPOINT="https://httpbin.org/status/200"

# TNT Bearer Token to be generated on TNT backend
TNT_ACCESS_TOKEN="bearer_token"

# TNT environment being used ('development' or 'production')
# If set to 'production', the TNT_ACCESS_TOKEN must be configured
TNT_ENVIRONMENT="development"
```

### 2. Edit docker-compose file
- Check container name
- Check exposed ports

### 3. Build Docker Image and Run
```
sudo docker-compose up --build
```

### 4. Push image to repo
- Login to your docker repository
- Push image (maybe image needs to be tagged during buidling. By default it tags to 'latest')