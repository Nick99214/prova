from pydantic import BaseModel
from datetime import date

class Request(BaseModel):
    """
    Represents the request for Sampler API.

    Attributes:
    - sample_size (int): The size of the sample.
    - type (str): The type of the records to sample.
    - start_sampling_date (date): The start date for sampling.
    - end_sampling_date (date): The end date for sampling.
    - annotator_1 (str): The first annotator.
    - annotator_2 (str): The second annotator.
    """
    sample_size: int
    type: str
    start_sampling_date: date
    end_sampling_date: date
    annotator_1: str
    annotator_2: str