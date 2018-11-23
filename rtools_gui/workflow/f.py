"Module implementing steps for F module"
from .generic import ExpansionDetection


class FExpansionDetection(ExpansionDetection):
    "Expansion detection for MOX F"

    def run(self):
        self._boot_and_detect(r'USB 3.0 Module \(4 ports\)')


# All steps for MOX F in order
FSTEPS = (
    FExpansionDetection,
)
