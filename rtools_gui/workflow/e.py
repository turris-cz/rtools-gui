"Module implementing steps for E module"
from .generic import Step, ExpansionDetection


class EExpansionDetection(ExpansionDetection):
    "Expansion detection for MOX E"

    def run(self):
        self._boot_and_detect('Peridot Switch Module (8-port)')


# All steps for MOX D in order
ESTEPS = (
    EExpansionDetection,
)
