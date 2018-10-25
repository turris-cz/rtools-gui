
class WorkflowException(Exception):
    "Gemeric exception from workflow"
    pass

class InvalidBoardNumberException(WorkflowException):
    "Provided serial number is not valid serial number for Turris Mox board"
    pass
