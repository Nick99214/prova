import uuid
import datetime
from utility import Constants

class SampleRecord:
    """
    Represents a record of a sample.

    Attributes:
    - sample_id (str): The ID of the sample.
    - type (str): The type of the sample.
    - size_sample (int): The size of the sample.
    - feedback (str): Feedback message for the sampling process.
    - feedback_table (str): The distribution of classes in the sample vs the number of records per class expected.
    - annotator_1 (str): The first annotator.
    - annotator_2 (str): The second annotator.
    - created_at (datetime): The timestamp when the sample was created.
    - start_date (datetime): The start date for sampling.
    - end_date (datetime): The end date for sampling.
    - distribuzione_classi (str): The distribution of classes in the sample.
    - distribuzione_abi (str): The distribution of ABI in the sample.
    - evaluation_completed (bool): Indicates if the evaluation is completed.
    - status (str): The status of the sample.
    """
    def __init__(self, request, sampling_feedback_message,feedback_table, sample_entries):
        self.sample_id = str(uuid.uuid4())
        self.type = request.type
        self.size_sample = request.sample_size
        self.feedback = sampling_feedback_message
        self.feedback_table = feedback_table
        self.annotator_1 = request.annotator_1
        self.annotator_2 = request.annotator_2
        self.created_at = datetime.datetime.now()
        self.start_date = request.start_sampling_date
        self.end_date = request.end_sampling_date
        self.distribuzione_classi = ", ".join(f"{value}: {count}" for value, count in sample_entries[Constants.CLASS_COLUMN].value_counts().items())
        self.distribuzione_abi = ", ".join(f"{value}: {count}" for value, count in sample_entries[Constants.ABI_COLUMN].value_counts().items())
        self.evaluation_completed = False
        self.status = Constants.SAMPLE_STATUS_CREATED


    def get_attribute_names(self):
        return [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

    def to_dict(self):
        return {attr: getattr(self, attr) for attr in self.get_attribute_names()}