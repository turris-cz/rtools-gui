
class Step():
    "Abstract class for signle step"

    def __init__(self, moxtester):
        self.moxtester = moxtester

    @staticmethod
    def name():
        "Returns name of this test. In Czech of course."
        raise NotImplementedError()

    @staticmethod
    def description():
        "Returns description of this step. In Czech of course."
        raise NotImplementedError()

    @staticmethod
    def substeps():
        """Returns list of substeps. If there are none then return None."""
        raise NotImplementedError()
