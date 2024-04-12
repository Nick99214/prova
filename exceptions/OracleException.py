__author__ = "Nicola Esposito"
from utility import Constants


class OracleException(Exception):
    def __init__(self, message=Constants.EXCEPTION_ORACLE_ERROR_MESSAGE):
        self.message = message
        self.type = Constants.EXCEPTION_ORACLE_TYPE
        super().__init__(message)
