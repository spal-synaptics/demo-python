from typing import Optional

from gst.pipeline import GstPipeline


class GstInputValidator:

    def __init__(
        self, inp_type: int, num_buffers: int = 10, verbose: int = 1
    ) -> None:
        self._inp_type = inp_type
        self._num_buffers = num_buffers
        self._verbose = verbose
        self._val_pipeline = GstPipeline()

    def validate_input(
        self,
        inp_src: str,
        msg_on_error: str,
        *,
        inp_w: Optional[int] = None,
        inp_h: Optional[int] = None,
        inp_codec: Optional[str] = None,
        codec_elems: Optional[tuple[str, str]] = None,
    ) -> bool:
        self._val_pipeline.reset()
        if self._inp_type == 1:
            self._val_pipeline.add_elements(
                ["filesrc", f'location="{inp_src}"'],
                ["qtdemux", "name=demux", "demux.video_0"],
                "queue",
                *codec_elems,
            )
        elif self._inp_type == 2:
            self._val_pipeline.add_elements(
                ["v4l2src", f"device={inp_src}"],
                f"video/x-raw,framerate=30/1,format=YUY2,width={inp_w},height={inp_h}",
            )
        elif self._inp_type == 3:
            self._val_pipeline.add_elements(
                ["rtspsrc", f'location="{inp_src}"', "latency=2000"],
                "rtpjitterbuffer",
                ["rtph264depay", "wait-for-keyframe=true"],
                f"video/x-{inp_codec},width={inp_w},height={inp_h}",
                *codec_elems,
            )
        self._val_pipeline.add_elements(
            ["fakesink", f"num-buffers={self._num_buffers}"]
        )
        if not self._val_pipeline.run("Validating input..." if self._verbose > 0 else "", self._verbose > 1):
            if self._verbose > 0:
                print("\n" + msg_on_error + "\n")
            return False
        if self._verbose > 0:
            print("Input OK")
        return True
