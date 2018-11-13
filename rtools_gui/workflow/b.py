"Module implementing steps for B module"
from .generic import Step, ExpansionDetection


class BExpansionDetection(ExpansionDetection):
    "Expansion detection for MOX B"

    def run(self):
        self._boot_and_detect('Mini-PCIe Module')


# All steps for MOX D in order
BSTEPS = (
    BExpansionDetection,
)
