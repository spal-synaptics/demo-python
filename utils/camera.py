from gst.validator import GstInputValidator

DEV_PREFIX = "/dev/video"
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480


def find_valid_camera_devices(
    inp_w: int = DEFAULT_WIDTH,
    inp_h: int = DEFAULT_HEIGHT,
) -> list[str]:
    """
    Attempts to find a connected camera.

    Only works for devices with format "dev/videoX".
    """
    if not inp_w > 0 or not inp_h > 0:
        raise ValueError("Invalid camera input dimensions")
    val = GstInputValidator(inp_type=2, verbose=0)
    valid_devs: list[str] = []
    for i in range(10):
        if val.validate_input(DEV_PREFIX + str(i), "", inp_w=inp_w, inp_h=inp_h):
            valid_devs.append(DEV_PREFIX + str(i))
    return valid_devs
