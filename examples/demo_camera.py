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


# Your camera's input width.
INPUT_WIDTH = 640

# Your camera's input height.
INPUT_HEIGHT = 480

# Your camera's device ID, typically has the format "/dev/videoX". "AUTO" means the script will attempt to find your camera.
# Note that "AUTO" might find the wrong camera if you have multiple cameras connected to the baord.
# Execute `v4l2-ctl --list-devices` to get a list of connected camera devices and their device IDs.
CAMERA = "AUTO"

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
    inp_src_info = get_inp_src_info(2, INPUT_WIDTH, INPUT_HEIGHT, CAMERA, None)
    if not inp_src_info:
        sys.exit(1)
    model_inp_dims = get_model_input_dims(MODEL)
    if not model_inp_dims:
        sys.exit(1)
    gst_params: dict[str, Any] = {
        "inp_type": 2,
        "inp_w": INPUT_WIDTH,
        "inp_h": INPUT_HEIGHT,
        "inp_src": inp_src_info[0],
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
