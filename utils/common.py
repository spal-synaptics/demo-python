from enum import Enum, auto
from typing import Final

# synap metadata file
INF_META_FILE: Final = "0/model.json"

# camera specific constants
CAM_DEV_PREFIX = "/dev/video"
CAM_DEFAULT_WIDTH = 640
CAM_DEFAULT_HEIGHT = 480


class InputType(Enum):
    CAMERA = auto()
    FILE = auto()
    RTSP = auto()
