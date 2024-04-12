import traceback
from utility import Constants


class ExceptionHandler:
    def __init__(self, exception):
        self.exception = exception
        self.message, self.stacktrace = self.manageException()

    def manageException(self):
        if hasattr(self.exception, "type"):
            return self.exception.message,  traceback.format_exc()
        else:
            return Constants.GENERAL_ERROR_MESSAGE, traceback.format_exc()



