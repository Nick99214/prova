__author__ = "Nicola Esposito"



class CustomException(Exception):
    def __init__(self, message, exception_type):
        self.message = message
        self.type = exception_type
        super().__init__(message)