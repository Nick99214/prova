from pydantic import BaseModel



class Response(BaseModel):
    """
    Represents the response of the Sampler API.

    Attributes:
    - result (str): The result of the Sampling process.
    - sample_id (str): The ID of the sample created.
    - response_message (str): The message containing further information about the sampling process.
    """

    result: str
    sample_id: str
    response_message: str
