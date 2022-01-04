
class WorkflowException(Exception):
    "Gemeric exception from workflow"
    pass

class RandomErrorException(Exception):
    "Random Error - try again"
    pass

class InvalidBoardNumberException(WorkflowException):
    "Provided serial number is not valid serial number for Turris Mox board"
    pass


class FatalWorkflowException(WorkflowException):
    "Exception that breaks workflow"
    pass
