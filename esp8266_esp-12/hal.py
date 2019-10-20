
#----------------------------
# Hardware Abstraction Layer
#----------------------------
import machine

# Hardware-dependent platform objects and routines which can
# (or might have to) be overwritten here. Note that if you
# overwrite them here, they won't be OTA-updatable anymore.
from pal import LED
from pal import WLAN
from pal import Chronos
from pal import get_tuuid
from pal import get_reset_cause
from pal import is_frozen
from pal import reboot

# Hardware settings
HW_SUPPORTS_DEEPSLEEP  = False
HW_SUPPORTS_RESETCAUSE = True
HW_SUPPORTS_LED        = True
HW_SUPPORTS_WLAN       = True
HW_SUPPORTS_SSL        = is_frozen()
HW_SUPPORTS_ENCRYPTION = is_frozen()
HW_WEBSETUP_RESETCAUSES = [machine.PWRON_RESET, machine.HARD_RESET, machine.WDT_RESET]

# Hardware initialization (i.e. put PWMs to zero)
def init():
    pass

# Back compatibility
def is_os_frozen():
    return is_frozen()
from pal import get_traceback
import ure as re
fspath='/'
def reset_cause():
    import machine
    return machine.reset_cause()
HARD_RESET=4
