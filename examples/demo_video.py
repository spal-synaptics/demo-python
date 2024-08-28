# ============================================================================== #
# IMPORTS: DO NOT MODIFY                                                         #
# ============================================================================== #

import os
import sys
from typing import Any

from gst.pipeline import GstPipelineGenerator
from utils.model_info import get_model_input_dims
from utils.user_input import get_inp_src_info

# ============================================================================== #


# Path to a video file on the board.
# Leaving this empty will prompt the script to ask for a file when run.
VIDEO_FILE = ""

# The codec used to compress the video file.
# Must be one of: av1, h264, h265
# Try using a different codec if the demo fails to run
VIDEO_CODEC = "h264"

# The path to the inference model to use. Must be a vaild SyNAP model with a ".synap" file extension.
MODEL = "/usr/share/synap/models/object_detection/coco/model/yolov8s-640x384/model.synap"

# How many frames to skip between sucessive inferences.
# Increasing this number may result in better performance but can look worse visually.
INFERENCE_SKIP = 1

# Whether to launch the demo in fullscreen.
FULLSCREEN = True


# ============================================================================== #
# RUNNER CODE: DO NOT MODIFY                                                     #
# ============================================================================== #

def main():
    inp_src_info = get_inp_src_info(1, None, None, VIDEO_FILE, VIDEO_CODEC)
    if not inp_src_info:
        sys.exit(1)
    model_inp_dims = get_model_input_dims(MODEL)
    if not model_inp_dims:
        sys.exit(1)
    gst_params: dict[str, Any] = {
        "inp_type": 1,
        "inp_src": inp_src_info[0],
        "inp_codec": inp_src_info[1],
        "codec_elems": inp_src_info[2],
        "inf_model": MODEL,
        "inf_w": model_inp_dims[0],
        "inf_h": model_inp_dims[1],
        "inf_skip": INFERENCE_SKIP,
        "fullscreen": FULLSCREEN,
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
    main()

# ============================================================================== #
