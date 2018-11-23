"Module implementing steps for B module"
from .generic import ExpansionDetection


class BExpansionDetection(ExpansionDetection):
    "Expansion detection for MOX B"

    def run(self):
        self._boot_and_detect('Mini-PCIe Module')


# All steps for MOX B in order
BSTEPS = (
    BExpansionDetection,
)
