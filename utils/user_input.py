from typing import Optional
import subprocess

from gst.validator import GstInputValidator
from utils.camera import find_valid_camera_devices


__all__ = [
    "get_dims",
    "get_bool_prop",
    "get_int_prop",
    "get_inp_type",
    "get_inp_src_info",
    "get_inf_model",
]

CODECS: dict[str, tuple[str, str]] = {
    "av1": ("av1parse", "v4l2av1dec"),
    "h264": ("h264parse", "v4l2h264dec"),
    "h265": ("h265parse", "v4l2h265dec"),
}


def get_dims(prompt: str, inp_dims: Optional[str]) -> tuple[int, int]:
    while True:
        try:
            if not inp_dims:
                inp_dims = input(f"{prompt} (widthxheight): ")
            inp_w, inp_h = [int(d) for d in inp_dims.split("x")]
            if inp_w > 0 and inp_h > 0:
                return inp_w, inp_h
            print("\nDimensions must be positive integers\n")
            inp_dims = None
        except (ValueError, TypeError):
            print(f'\nInvalid dimensions "{inp_dims}"\n')
            inp_dims = None


def get_bool_prop(prompt: str) -> bool:
    while True:
        try:
            val = input(f"{prompt} (Y/n): ").lower()
            if val not in ("y", "n"):
                raise ValueError
            return val == "y"
        except (TypeError, ValueError):
            print(f"\nInvalid input\n")


def get_int_prop(prompt: str, prop_val: Optional[int], default: int) -> int:
    while True:
        try:
            if prop_val is None:
                prop_val = int(input(f"{prompt} (default: {default}): ") or default)
            if prop_val >= 0:
                return prop_val
            print("\nValue must be >= 0\n")
            prop_val = None
        except (TypeError, ValueError):
            print(f"\nInvalid input\n")
            prop_val = None


def get_inp_type(inp_type: Optional[str]) -> int:
    while (
        inp_type := inp_type
        or input("Input type:\n[1] File\n[2] Camera\n[3] RTSP\nChoose type: ")
    ) not in ("1", "2", "3"):
        print("\nInvalid choice.\n")
        inp_type = None
    return int(inp_type)


def get_inp_src_info(
    inp_type: int,
    inp_w: Optional[int],
    inp_h: Optional[int],
    inp_src: Optional[str],
    inp_codec: Optional[str],
) -> Optional[tuple[str, str, tuple[str, str]]]:
    gst_val: GstInputValidator = GstInputValidator(inp_type)
    codec_elems: Optional[tuple[str, str]] = None
    try:
        if inp_type == 1:
            inp_src: str = inp_src or input("Video file path: ")
            inp_codec = inp_codec or (
                input("[Optional] Codec [av1 / h264 (default) / h265]: ") or "h264"
            )
            codec_elems = CODECS[inp_codec]
            msg_on_error: str = (
                f'ERROR: Invalid input video file "{inp_src}", check source and codec'
            )
        elif inp_type == 2 and inp_w and inp_h:
            inp_codec = None
            inp_src: str = inp_src or input("Camera device (default: CAM): ") or "CAM"
            if inp_src == "CAM":
                print("Finding valid camera device...")
                valid_devs = find_valid_camera_devices(inp_w=inp_w, inp_h=inp_h)
                if not valid_devs:
                    print("\nNo camera connected to board\n")
                    return None
                inp_src = valid_devs[0]
                print(f"Found {inp_src}")
                return inp_src, inp_codec, codec_elems
            msg_on_error: str = (
                f'ERROR: Invalid camera "{inp_src}", use `v4l2-ctl --list-devices` to verify device'
            )
        elif inp_type == 3 and inp_w and inp_h:
            inp_src: str = inp_src or input("RTSP stream URL: ")
            inp_codec = inp_codec or (
                input("[Optional] Codec [av1 / h264 (default) / h265]: ") or "h264"
            )
            codec_elems = CODECS[inp_codec]
            msg_on_error: str = (
                f'ERROR: Invalid RTSP stream "{inp_src}", check URL and codec'
            )
        else:
            raise SystemExit("Fatal: invalid input parameters")

        if gst_val.validate_input(
            inp_src,
            msg_on_error,
            inp_w=inp_w,
            inp_h=inp_h,
            inp_codec=inp_codec,
            codec_elems=codec_elems,
        ):
            return inp_src, inp_codec, codec_elems
    except KeyError:
        print(
            f'\nERROR: Invalid codec "{inp_codec}", choose from [av1 / h264 / h265]\n'
        )


def get_inf_model(model: Optional[str]) -> str:
    while True:
        try:
            if not model:
                model: str = input("Model file path: ")
            print("Validating model...")
            # fmt: off
            subprocess.run(
                [
                    "synap_cli",
                    "-m", model,
                    "random"
                ],
                check=True,
                capture_output=True
            )
            # fmt: on
            print("Model OK")
            return model
        except subprocess.CalledProcessError as e:
            print("\n" + e.stderr.decode())
            print(f'\nERROR: Invalid SyNAP model "{model}"\n')
            model = None
