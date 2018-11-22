"Module implementing steps for C module"
from .generic import Step, ExpansionDetection


class CExpansionDetection(ExpansionDetection):
    "Expansion detection for MOX C"

    def run(self):
        self._boot_and_detect('Topaz Switch Module \(4-port\)')
        # TODO
        # Err: SMI read ready timeout
        # Check of switch MDIO address failed for 0x02


# All steps for MOX D in order
CSTEPS = (
    CExpansionDetection,
)
