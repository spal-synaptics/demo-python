# ============================================================================== #
# IMPORTS: DO NOT MODIFY                                                         #
# ============================================================================== #

import argparse
import os
import sys
from typing import Any

from gst.pipeline import GstPipelineGenerator
from utils.model_info import get_model_input_dims
from utils.user_input import get_inp_src_info, validate_inp_dims

# ============================================================================== #


# RTSP stream URL.
# Leaving this empty will prompt the script to ask for a URL when run.
RTSP_URL = ""

# RTSP stream's input width.
INPUT_WIDTH = 1920

# RTSP stream's input height.
INPUT_HEIGHT = 1080

# The codec used to compress the RTSP stream.
# Must be one of: av1, h264, h265
# Try using a different codec if the demo fails to run
VIDEO_CODEC = "h264"

# The path to the inference model to use. Must be a vaild SyNAP model with a ".synap" file extension.
MODEL = "/usr/share/synap/models/object_detection/coco/model/yolov8s-640x384/model.synap"

# How many frames to skip between sucessive inferences.
# Increasing this number may result in better performance but can look worse visually.
INFERENCE_SKIP = 1

# Whether to launch the demo in fullscreen.
FULLSCREEN = False


# ============================================================================== #
# RUNNER CODE: DO NOT MODIFY                                                     #
# ============================================================================== #

def main():
    inp_w, inp_h = [int(d) for d in args.input_dims.split("x")]
    inp_src_info = get_inp_src_info(3, inp_w, inp_h, args.input, args.input_codec)
    if not inp_src_info:
        sys.exit(1)
    model_inp_dims = get_model_input_dims(args.model)
    if not model_inp_dims:
        sys.exit(1)
    gst_params: dict[str, Any] = {
        "inp_type": 3,
        "inp_w": inp_w,
        "inp_h": inp_h,
        "inp_src": inp_src_info[0],
        "inp_codec": inp_src_info[1],
        "codec_elems": inp_src_info[2],
        "inf_model": args.model,
        "inf_w": model_inp_dims[0],
        "inf_h": model_inp_dims[1],
        "inf_skip": args.inference_skip,
        "fullscreen": args.fullscreen,
    }

    env = os.environ.copy()
    env["XDG_RUNTIME_DIR"] = "/var/run/user/0"
    env["WESTON_DISABLE_GBM_MODIFIERS"] = "true"
    env["WAYLAND_DISPLAY"] = "wayland-1"
    env["QT_QPA_PLATFORM"] = "wayland"

    gen: GstPipelineGenerator = GstPipelineGenerator(gst_params)

    gen.make_pipeline()
    gen.pipeline.run(run_env=env)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input",
        type=str,
        default=RTSP_URL,
        metavar="URL",
        help="RTSP stream URL (default: %(default)s)"
    )
    parser.add_argument(
        "-d", "--input_dims",
        type=validate_inp_dims,
        default=f"{INPUT_WIDTH}x{INPUT_HEIGHT}",
        metavar="WIDTHxHEIGHT",
        help="RTSP stream's input size (widthxheight) (default: %(default)s)"
    )
    parser.add_argument(
        "-c", "--input_codec",
        type=str,
        default=VIDEO_CODEC,
        metavar="CODEC",
        help="RTSP stream input codec (default: %(default)s)",
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default=MODEL,
        metavar="FILE",
        help="SyNAP model file location (default: %(default)s)"
    )
    parser.add_argument(
        "-s", "--inference_skip",
        type=int,
        default=INFERENCE_SKIP,
        metavar="FRAMES",
        help="How many frames to skip between sucessive inferences (default: %(default)s)"
    )
    parser.add_argument(
        "--fullscreen",
        action="store_true",
        default=FULLSCREEN,
        help="Launch demo in fullscreen (default: %(default)s)",
    )
    args = parser.parse_args()
    main()

# ============================================================================== #
