__author__ = "Nicola Esposito"
class SampleEntry:
    """
    Represents an entry in a sample.

    Attributes:
    - record_id (str): The ID of the record.
    - record_type (str): The type of the record.
    - body (str): The body of the record.
    - model_category (str): The model category of the record.
    - protocollo (str): The protocol of the record.
    - sample_id (str): The ID of the sample.
    """

    def __init__(self, record_id, record_type, body, model_category, protocollo, sample_id):
        self.record_id = record_id
        self.record_type = record_type
        self.body = body
        self.model_category = model_category
        self.protocollo = protocollo
        self.sample_id = sample_id

    def get_attribute_names(self):
        return [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

    def to_dict(self):
        return {attr: getattr(self, attr) for attr in self.get_attribute_names()}