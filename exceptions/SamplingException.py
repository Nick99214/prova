__author__ = "Nicola Esposito"
from utility import Constants


class SamplingException(Exception):
    def __init__(self, message=Constants.EXCEPTION_SAMPLING_ERROR_MESSAGE):
        self.message = message
        self.type = Constants.EXCEPTION_SAMPLING_TYPE
        super().__init__(message)
