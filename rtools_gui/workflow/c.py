"Module implementing steps for C module"
from .generic import ExpansionDetection


class CExpansionDetection(ExpansionDetection):
    "Expansion detection for MOX C"

    def run(self):
        self._boot_and_detect(r'Topaz Switch Module \(4-port\)')
        # TODO
        # Err: SMI read ready timeout
        # Check of switch MDIO address failed for 0x02


# All steps for MOX C in order
CSTEPS = (
    CExpansionDetection,
)
