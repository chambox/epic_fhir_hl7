import os
import random
import string
import logging

logger = logging.getLogger(__name__)

def randomize_encounter(encounter):
    # Check if the DEV environment variable is set to 'on', 'true', etc.
   
    # Randomly generate patient names
    first_names = ['John', 'Jane', 'Alex', 'Emily', 'Michael', 'Sarah', 'David', 'Laura', 'Chris', 'Olivia']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    
    random_first_name = random.choice(first_names)
    random_last_name = random.choice(last_names)
    
    # Function to generate a random ID
    def random_id(length=24):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    # Modify patient details

    logger.info(f"Before randomization: {encounter['patient']}")
    encounter['patient']['first_name'] = random_first_name
    encounter['patient']['last_name'] = random_last_name
    logger.info(f"After randomization: {encounter['patient']}")
    new_patient_id = random_id()
    encounter['patient']['id'] = new_patient_id
    encounter['hospital_stay']['patient']['id'] = new_patient_id
    
    # Modify hospital stay ID

    new_hospital_stay_id = random_id()
    encounter['hospital_stay']['id'] = new_hospital_stay_id
    for stay in encounter['department_stays']:
        stay['hospital_stay']['id'] = new_hospital_stay_id
    
    # Modify department stays IDs and location IDs
    if 'department_stays' in encounter:
        for stay in encounter['department_stays']:
            stay['id'] = random_id()

            stay['location']['department']['id'] = random_id()
            stay['location']['room']['id'] = random_id()
            stay['location']['bed']['id'] = random_id()

    
    # Modify alternative IDs if necessary
    encounter['patient']['alternative_ids'] = [random_id(16) for _ in range(len(encounter['patient']['alternative_ids']))]
        
    return encounter
