"Module implementing steps for G module"
from .generic import ExpansionDetection


class GExpansionDetection(ExpansionDetection):
    "Expansion detection for MOX G"

    def run(self):
        self._boot_and_detect('Passthrough Mini-PCIe Module')


# All steps for MOX G in order
GSTEPS = (
    GExpansionDetection,
)
