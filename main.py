"""
Run a GStreamer demo.

Requires a valid input source (video / camera / RTSP) and SyNAP inference model.
"""

from typing import Any
import argparse
import os
import sys

from gst.pipeline import GstPipelineGenerator
from utils.input import *


def main(args: argparse.Namespace) -> None:
    gst_params: dict[str, Any] = {}

    try:
        gst_params["inp_type"] = get_inp_type(args.inp_type)
        if gst_params["inp_type"] != 1:
            gst_params["inp_w"], gst_params["inp_h"] = get_dims(
                "Input dimensions", args.inp_dims
            )

        if not (
            inp_src_info := get_inp_src_info(
                gst_params["inp_type"],
                gst_params.get("inp_w", None),
                gst_params.get("inp_h", None),
                args.inp_src,
                args.inp_codec if args.inp_src else None,
            )
        ):
            sys.exit(1)
        gst_params["inp_src"], gst_params["inp_codec"], gst_params["codec_elems"] = (
            inp_src_info
        )

        gst_params["inf_model"] = get_inf_model(args.inf_model)
        gst_params["inf_w"], gst_params["inf_h"] = get_dims(
            "Model input dimensions", args.inf_dims
        )
        gst_params["inf_skip"] = get_int_prop(
            "How many frames to skip between each inference",
            args.inf_skip if (args.inf_model and args.inf_dims) else None,
            1,
        )
        gst_params["inf_delay"] = get_int_prop(
            "How many frames to delay start of inference by",
            args.inf_delay if (args.inf_model and args.inf_dims) else None,
            0,
        )
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()

    env = os.environ.copy()
    env["XDG_RUNTIME_DIR"] = "/var/run/user/0"
    env["WESTON_DISABLE_GBM_MODIFIERS"] = "true"
    env["WAYLAND_DISPLAY"] = "wayland-1"
    env["QT_QPA_PLATFORM"] = "wayland"

    gen: GstPipelineGenerator = GstPipelineGenerator(
        gst_params.get("inp_w", None),
        gst_params.get("inp_h", None),
        gst_params["inf_model"],
        gst_params["inf_w"],
        gst_params["inf_h"],
        gst_params["inf_skip"],
        gst_params["inf_delay"],
    )

    gen.make_pipeline(gst_params)
    gen.pipeline.run(run_env=env)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="NOTE: The script will interactively ask for necessary info not provided via command line.",
    )
    parser.add_argument(
        "-t",
        "--inp_type",
        type=str,
        metavar="TYPE",
        help="Input type ([1] File, [2] Camera, [3] RTSP)",
    )
    parser.add_argument(
        "-d",
        "--inp_dims",
        type=str,
        metavar="WIDTHxHEIGHT",
        help="Input dimensions (widthxheight)",
    )
    parser.add_argument(
        "-i",
        "--inp_src",
        type=str,
        metavar="SRC",
        help="Input source (file / camera / RTSP)",
    )
    parser.add_argument(
        "--inp_codec",
        type=str,
        default="h264",
        help="Input codec for file/RTSP (default: %(default)s)",
    )

    inf_group = parser.add_argument_group("Inference parameters")
    inf_group.add_argument(
        "--inf_model", type=str, metavar="FILE", help="SyNAP model file location"
    )
    inf_group.add_argument(
        "--inf_dims",
        type=str,
        metavar="WIDTHxHEIGHT",
        help="Model input dimensions (widthxheight)",
    )
    inf_group.add_argument(
        "--inf_skip",
        type=int,
        metavar="N_FRAMES",
        default=1,
        help="How many frames to skip between each inference (default: %(default)s)",
    )
    inf_group.add_argument(
        "--inf_delay",
        type=int,
        metavar="N_FRAMES",
        default=0,
        help="How many frames to delay start of inference by (default: %(default)s)",
    )
    args = parser.parse_args()

    main(args)
