"Module implementing steps for E module"
from .generic import ExpansionDetection


class EExpansionDetection(ExpansionDetection):
    "Expansion detection for MOX E"

    def run(self):
        self._boot_and_detect(r'Peridot Switch Module \(8-port\)')


# All steps for MOX E in order
ESTEPS = (
    EExpansionDetection,
)
