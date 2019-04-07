
#----------------------------
# Hardware Abstraction Layer
#----------------------------

# Hardware settings
HW_SUPPORTS_DEEPSLEEP  = False
HW_SUPPORTS_RESETCAUSE = False
HW_SUPPORTS_LED        = False
HW_SUPPORTS_WLAN       = False
HW_SUPPORTS_SSL        = False
HW_SUPPORTS_ENCRYPTION = True
HW_WEBSETUP_RESETCAUSES = []

# Hardware initialization (i.e. put PWMs to zero)
def init():
    pass

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

# Back compatibility
def is_os_frozen():
    return is_frozen()
from pal import get_traceback
import ure as re
fspath='/'
def reset_cause():
    return 0
HARD_RESET=4