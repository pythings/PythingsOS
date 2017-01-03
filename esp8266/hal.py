
#----------------------------
# Hardware Abstraction Layer
#----------------------------

# Hardware settings
HW_SUPPORTS_DEEPSLEEP  = False
HW_SUPPORTS_RESETCAUSE = True
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = True
HW_SUPPORTS_SSL        = False
HW_SUPPORTS_ENCRYPTION = True
HW_RESETCAUSE_HARD     = 6

# Hardware initialization (i.e. put PWMs to zero)
def init():
    pass

# Hardware-dependent platform objects and routines which can
# (or might have to) be overwritten here. Note that if you
# overwrite them here, they won't be OTA-updatable anymore.
from sal import LED
from sal import WLAN
from sal import Chronos
from sal import get_tuuid
from sal import get_reset_cause
from sal import is_frozen
from sal import reboot

# Back compatibility
def is_os_frozen():
    return is_frozen()
from sal import get_traceback
import ure as re
fspath='/'
def reset_cause():
    import machine
    return machine.reset_cause()
HARD_RESET=4
