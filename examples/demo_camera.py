import os
import sys
from typing import Any

from gst.pipeline import GstPipelineGenerator
from utils.model_info import get_model_input_dims
from utils.user_input import get_inp_src_info


INPUT_WIDTH = 640
INPUT_HEIGHT = 480
CAMERA = "AUTO"
MODEL = "/usr/share/synap/models/object_detection/coco/model/yolov8s-640x384/model.synap"
INFERENCE_SKIP = 0
INFERENCE_DELAY = 0
FULLSCREEN = True


# ===========================
# RUNNER CODE: DO NOT MODIFY
# ===========================

def main():
    camera, _, _ = get_inp_src_info(2, INPUT_WIDTH, INPUT_HEIGHT, CAMERA, None)
    if not camera:
        sys.exit(1)
    model_inp_w, model_inp_h = get_model_input_dims(MODEL)
    if not model_inp_w or not model_inp_h:
        sys.exit(1)
    gst_params: dict[str, Any] = {
        "inp_type": 2,
        "inp_w": INPUT_WIDTH,
        "inp_h": INPUT_HEIGHT,
        "inp_src": camera,
        "inf_model": MODEL,
        "inf_w": model_inp_w,
        "inf_h": model_inp_h,
        "inf_skip": INFERENCE_SKIP,
        "inf_delay": INFERENCE_DELAY,
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
