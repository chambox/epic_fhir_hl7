class hl7parser:

    def __init__(self) -> None:
        pass
    @staticmethod
    def parse(hl7_message):
        """
        Parses an HL7 message into its constituent segments.
        
        This static method takes a raw HL7 message string, removes any leading or trailing 
        whitespace, and splits it into individual segments based on newline characters. 
        It returns an instance of the `hl7message` class with the segments as its attribute.
        
        Args:
            hl7_message (str): The raw HL7 message string to be parsed.
        
        Returns:
            hl7message: An instance of the `hl7message` class with the parsed segments.
        
        Example:
            hl7_message = '''
            MSH|^~\&|HIS|RIH|EKG|EKG|202309010830||ADT^A01|MSG00001|P|2.3
            EVN|A01|202309010830|||^KOOL^BILL
            PID|1||123456^^^RIH^MR||DOE^JOHN^A||19800101|M|||123 MAIN ST^^METROPOLIS^IL^62960||555-1234|||M|NON|123456789|987-65-4321
            NK1|1|DOE^JANE|SPOUSE|||||||EC
            PV1|1|I|2000^2012^01||||004777^WHITE^STEPHEN^A|||SUR|||||||004777^WHITE^STEPHEN^A|MED|||||||||||||||||||202309010800
            '''
            parser = HL7Parser()
            parsed_message = parser.parse(hl7_message)
            print(parsed_message.segments)
        
        """
        segments = hl7_message.strip().split('\n')
        return hl7message(segments=segments)


class hl7message:

    def __init__(self, segments: list) -> None:
        self.segments = segments

    def get_segment(self, segment, update=True):
        if hasattr(self, segment):
            return getattr(self, segment)
        for s in self.segments:
            if s.startswith(segment):
                parts = s.split('|')
                parsed = [p.split('^') for p in parts]
                if update:
                    self.__dict__.update({segment: parsed})
                return parsed
    
    def get_segments(self):
        return self.segments
    
    def get_patient(self):
        pid_segment = self.get_segment('PID')
        if not pid_segment:
            return None
        else:
            return {
                'patient_id': self.get_field(pid_segment, 3, 0),
                'patient_name': ' '.join(self.get_field(pid_segment, 5, default=[])),
                'dob': self.get_field(pid_segment, 7, 0),
                'gender': self.get_field(pid_segment, 8, 0)
            }
    
    def get_field(self, fields, index, subindex=None, default=None):
        try:
            return fields[index][subindex] if subindex is not None else fields[index]
        except IndexError:
            return default

class hl7messageexception(Exception):
    pass
