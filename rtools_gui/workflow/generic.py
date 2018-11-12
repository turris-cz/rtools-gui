
class Step():
    "Abstract class for signle step"

    def __init__(self, moxtester, resources, set_progress):
        self.moxtester = moxtester
        self.resources = resources
        self.set_progress = set_progress

    def run(self):
        "Run this step"
        raise NotImplementedError()

    @staticmethod
    def name():
        "Returns name of this test. In Czech of course."
        raise NotImplementedError()

    @staticmethod
    def description():
        "Returns description of this step. In Czech of course."
        raise NotImplementedError()
