from os import environ
from typing import Any
import subprocess


def get_env() -> dict[str, str]:
    env = environ.copy()
    env["XDG_RUNTIME_DIR"] = "/var/run/user/0"
    env["WESTON_DISABLE_GBM_MODIFIERS"] = "true"
    env["WAYLAND_DISPLAY"] = "wayland-1"
    env["QT_QPA_PLATFORM"] = "wayland"
    return env


class GstPipeline:

    def __init__(self) -> None:
        self._elems: list[str, list[str]] = []
        self._pipeline: list[str] = []

    def __repr__(self) -> str:
        self._format_pipeline()
        pipeline_str = ""
        for elem in self._pipeline:
            pipeline_str += elem + " "
            if elem == "!":
                pipeline_str += "\\\n"
        return pipeline_str

    def _format_pipeline(self) -> None:
        self._pipeline.clear()
        self._pipeline.extend(self._elems[0])
        for elem in self._elems[1:]:
            if isinstance(elem, list):
                self._pipeline.extend(["!", *elem])
            else:
                if elem != "t_data.":
                    self._pipeline.append("!")
                self._pipeline.append(elem)

    def add_elements(self, *elements: str | list[str]) -> None:
        self._elems.extend(elements)

    def reset(self) -> None:
        self._elems.clear()
        self._pipeline.clear()

    def run(
        self,
        run_prompt: str = "Running pipeline...",
        print_err: bool = True,
    ) -> bool:
        self._format_pipeline()
        process = None
        try:
            if run_prompt:
                print(run_prompt)
            process = subprocess.Popen(
                ["gst-launch-1.0", *self._pipeline],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=get_env(),
            )
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode, process.args, output=stdout, stderr=stderr
                )
        except subprocess.CalledProcessError as e:
            if print_err:
                print(f"Pipeline failed with error: {e.stderr.decode()}")
            return False
        except KeyboardInterrupt:
            print("\nShutting down pipeline...")
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print("Shutdown failed, forcefully killing pipeline...")
                    process.kill()
                    process.wait()
        return True


class GstPipelineGenerator:

    def __init__(
        self,
        gst_params: dict[str, Any],
    ) -> None:
        self._inp_type: int = gst_params["inp_type"]
        self._inp_w: int = gst_params.get("inp_w", None)
        self._inp_h: int = gst_params.get("inp_h", None)
        self._inp_src: str = gst_params["inp_src"]
        self._inp_codec: str = gst_params.get("inp_codec", None)
        self._codec_elems: tuple[str, str] = gst_params.get("codec_elems", None)
        self._inf_model: str = gst_params["inf_model"]
        self._inf_w: int = gst_params["inf_w"]
        self._inf_h: int = gst_params["inf_h"]
        self._inf_skip: int = gst_params["inf_skip"]
        self._fullscreen: bool = gst_params["fullscreen"]
        self._pipeline: GstPipeline = GstPipeline()

    @property
    def pipeline(self) -> GstPipeline:
        return self._pipeline

    def _infer_elements(self) -> list[str, list[str]]:
        return [
            "videoconvert",
            ["tee", "name=t_data"],
            "t_data.",
            "queue",
            "videoconvert",
            "videoscale",
            f"video/x-raw,width={self._inf_w},height={self._inf_h},format=RGB",
            [
                "synapinfer",
                "mode=detector",
                f"model={self._inf_model}",
                f"frameinterval={self._inf_skip}",
                "name=infer",
            ],
            "overlay.inference_sink",
            "t_data.",
            "queue",
            [
                "synapoverlay",
                "name=overlay",
                "label=/usr/share/synap/models/object_detection/coco/info.json",
            ],
            "videoconvert",
            ["waylandsink", f"fullscreen={str(self._fullscreen).lower()}"],
        ]

    def make_file_pipeline(self, video_file: str, codec_elems: tuple[str, str]) -> None:
        self._pipeline.reset()
        if not codec_elems:
            raise SystemExit(
                "Fatal: codec information not provided to pipeline generator"
            )
        self._pipeline.add_elements(
            ["filesrc", f'location="{video_file}"'],
            ["qtdemux", "name=demux", "demux.video_0"],
            "queue",
            *codec_elems,
            *self._infer_elements(),
        )

    def make_cam_pipeline(self, cam_device: str) -> None:
        self._pipeline.reset()
        if not self._inp_w or not self._inp_h:
            raise SystemExit(
                "Fatal: input width or height not provided to pipeline generator"
            )
        self._pipeline.add_elements(
            ["v4l2src", f"device={cam_device}"],
            f"video/x-raw,framerate=30/1,format=YUY2,width={self._inp_w},height={self._inp_h}",
            *self._infer_elements(),
        )

    def make_rtsp_pipeline(
        self, rtsp_url: str, inp_codec: str, codec_elems: tuple[str, str]
    ) -> None:
        self._pipeline.reset()
        if not self._inp_w or not self._inp_h:
            raise SystemExit(
                "Fatal: input width or height not provided to pipeline generator"
            )
        if not inp_codec or not codec_elems:
            raise SystemExit(
                "Fatal: codec information not provided to pipeline generator"
            )
        self._pipeline.add_elements(
            ["rtspsrc", f'location="{rtsp_url}"', "latency=2000"],
            "rtpjitterbuffer",
            ["rtph264depay", "wait-for-keyframe=true"],
            f"video/x-{inp_codec},width={self._inp_w},height={self._inp_h}",
            *codec_elems,
            *self._infer_elements(),
        )

    def make_pipeline(self) -> None:
        try:
            if self._inp_type == 1:
                self.make_file_pipeline(self._inp_src, self._codec_elems)
            elif self._inp_type == 2:
                self.make_cam_pipeline(self._inp_src)
            elif self._inp_type == 3:
                self.make_rtsp_pipeline(
                    self._inp_src,
                    self._inp_codec,
                    self._codec_elems,
                )
            else:
                raise SystemExit("Fatal: invalid code - shouldn't reach here")
        except KeyError as e:
            raise SystemError(f'Fatal: missing pipeline paramemeter "{e.args[0]}"')
