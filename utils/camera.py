from gst.validator import GstInputValidator

DEV_PREFIX = "/dev/video"
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480


def find_valid_camera_devices(dev_prefix: str = DEV_PREFIX, inp_w: int = DEFAULT_WIDTH, inp_h: int = DEFAULT_HEIGHT) -> list[str]:
    val = GstInputValidator(
        inp_type=2,
        verbose=0
    )
    valid_devs: list[str] = []
    for i in range(10):
        if val.validate_input(dev_prefix + str(i), "", inp_w=inp_w, inp_h=inp_h):
            valid_devs.append(dev_prefix + str(i))
    return valid_devs
