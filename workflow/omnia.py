# TODO create a proper workflow
class Workflow(object):
    def __init__(self, name):
        self.name = name

WORKFLOW = (
    Workflow("POWER"),
    Workflow("ATSHA"),
    Workflow("UBOOT"),
    Workflow("REBOOT"),
    Workflow("REFLASH"),
    Workflow("RTC"),
)

