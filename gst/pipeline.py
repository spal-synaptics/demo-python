from typing import Any, Optional
import subprocess


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
        run_env: Optional[dict[str, str]] = None,
    ) -> bool:
        self._format_pipeline()
        process = None
        try:
            print(run_prompt)
            process = subprocess.Popen(
                ["gst-launch-1.0", *self._pipeline],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=run_env,
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
        inp_w: Optional[int],
        inp_h: Optional[int],
        inf_model: str,
        inf_w: int,
        inf_h: int,
        inf_skip: int,
        inf_delay: int,
    ) -> None:
        self._inp_w = inp_w
        self._inp_h = inp_h
        self._inf_model = inf_model
        self._inf_w = inf_w
        self._inf_h = inf_h
        self._inf_skip = inf_skip
        self._inf_delay = inf_delay
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
                # f"startdelay={self._inf_delay}", # temporarily disabled for compatibility
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
            "waylandsink",
        ]

    def make_file_pipeline(self, video_file: str, codec_elems: tuple[str, str]) -> None:
        self._pipeline.reset()
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
                "Fatal: input width and height not provided to pipeline generator"
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
                "Fatal: input width and height not provided to pipeline generator"
            )
        self._pipeline.add_elements(
            ["rtspsrc", f'location="{rtsp_url}"', "latency=2000"],
            "rtpjitterbuffer",
            ["rtph264depay", "wait-for-keyframe=true"],
            f"video/x-{inp_codec},width={self._inp_w},height={self._inp_h}",
            *codec_elems,
            *self._infer_elements(),
        )

    def make_pipeline(self, gst_params: dict[str, Any]) -> None:
        try:
            inp_type: int = gst_params["inp_type"]
            if inp_type == 1:
                self.make_file_pipeline(
                    gst_params["inp_src"], gst_params["codec_elems"]
                )
            elif inp_type == 2:
                self.make_cam_pipeline(gst_params["inp_src"])
            elif inp_type == 3:
                self.make_rtsp_pipeline(
                    gst_params["inp_src"],
                    gst_params["inp_codec"],
                    gst_params["codec_elems"],
                )
            else:
                raise SystemExit("Fatal: invalid code - shouldn't reach here")
        except KeyError as e:
            raise SystemError(f'Fatal: missing pipeline paramemeter "{e.args[0]}"')
