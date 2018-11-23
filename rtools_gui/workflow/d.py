"Module implementing steps for D module"
from .generic import ExpansionDetection


class DExpansionDetection(ExpansionDetection):
    "Expansion detection for MOX D"

    def run(self):
        self._boot_and_detect('SFP Module')


# All steps for MOX D in order
DSTEPS = (
    DExpansionDetection,
)
