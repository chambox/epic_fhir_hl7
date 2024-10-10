def sanitize_adt_message(encounter):
        default_date = "1900-01-01T00:00:00Z"  # TODO: Replace with actual default date from EPIC
        default_string = "NA"  # TODO: Replace with actual default string from EPIC
        default_id = "default_id"  # Temporary placeholder for non-nullable identifiers like bed and room, to be replaced with actual data from EPIC (TODO)

        date_fields = ['from_at', 'until_at', 'starts_at']  # Add any other date fields here
        string_fields = ['version']  # Add any other string fields that should not be null

        # Process top-level date fields
        for field in date_fields:
            if field in encounter and (encounter[field] is None or encounter[field] == ''):
                encounter[field] = default_date

        # Process top-level string fields
        for field in string_fields:
            if field in encounter and encounter[field] is None:
                encounter[field] = default_string

        # Process 'patient' fields
        if 'patient' in encounter:
            if 'date_of_birth' in encounter['patient'] and (encounter['patient']['date_of_birth'] is None or encounter['patient']['date_of_birth'] == ''):
                encounter['patient']['date_of_birth'] = default_date

        # Process 'hospital_stay' fields
        if 'hospital_stay' in encounter:
            # Process 'hospital_stay' date fields
            for field in date_fields:
                if field in encounter['hospital_stay'] and (encounter['hospital_stay'][field] is None or encounter['hospital_stay'][field] == ''):
                    encounter['hospital_stay'][field] = default_date
            # Process 'hospital_stay' string fields
            for field in string_fields:
                if field in encounter['hospital_stay'] and encounter['hospital_stay'][field] is None:
                    encounter['hospital_stay'][field] = default_string

        # Process 'department_stays'
        if 'department_stays' in encounter:
            for stay in encounter['department_stays']:
                # Process date fields in 'department_stays'
                for field in date_fields:
                    if field in stay and (stay[field] is None or stay[field] == ''):
                        stay[field] = default_date
                # Process string fields in 'department_stays'
                for field in string_fields:
                    if field in stay and stay[field] is None:
                        stay[field] = default_string
                if 'location' in stay:
                    if 'room' in stay['location'] and (stay['location']['room']['id'] is None or stay['location']['room']['id'] == ''):
                        stay['location']['room']['id'] = default_id  # TODO: Replace with actual room ID from EPIC
                    if 'bed' in stay['location'] and (stay['location']['bed']['id'] is None or stay['location']['bed']['id'] == ''):
                        stay['location']['bed']['id'] = default_id  # TODO: Replace with actual bed ID from EPIC
                    # Remove 'id' key if it's directly under 'location'
                    if 'id' in stay['location']:
                        del stay['location']['id']

        return encounter