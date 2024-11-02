from dataclasses import dataclass
import numpy as np
from webcam import Webcam
import cv2
from ultralytics import YOLO


_VIDEO_SOURCE: int = 0
_VIDEO_WIDTH: int = 640
_VIDEO_HEIGHT: int = 480

_PERSON_CLASS_ID: int = 0
_MIN_CONFIDENCE: float = 0.8

_model = YOLO("640px_100epoch.pt")
_camera: Webcam = Webcam(src=_VIDEO_SOURCE, w=_VIDEO_WIDTH, h=_VIDEO_HEIGHT)


class Target:
    # __slots__ makes class attributes static, which increases performance and reduces chances of silent errors
    __slots__ = [
        "corner1_x",
        "corner1_y",
        "corner2_x",
        "corner2_y",
        "track_id",
        "confidence",
        "classification",
        "center_x",
        "center_y",
        "size_x",
        "size_y"
    ]
    
    def __init__(
            self,
            c1x: float,
            c1y: float,
            c2x: float,
            c2y: float,
            track_id: float,
            confidence: float,
            classification: float
    ) -> None:
        self.corner1_x: int = round(c1x)
        self.corner1_y: int = round(c1y)
        self.corner2_x: int = round(c2x)
        self.corner2_y: int = round(c2y)
        self.track_id: int | None = int(track_id) if track_id is not None else None
        self.confidence: float = confidence
        self.classification: int = int(classification)
        self.center_x: int = (self.corner1_x + self.corner2_x) // 2
        self.center_y: int = (self.corner1_y + self.corner2_y) // 2
        self.size_x: int = abs(self.corner1_x - self.center_x)
        self.size_y: int = abs(self.corner1_y - self.center_y)


@dataclass(slots=True)
class FrameData:
    targets: list[Target]
    frame_width: int
    frame_height: int
    annotated_frame: np.ndarray


def get_frame_data() -> FrameData:
    
    # get frame from camera and convert to BGR because cv2 works with BGR for some reason
    frame = _camera.read_next_frame()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # use machine learning model to classify objects in frame and save to cpu memory
    results = _model.track(frame, persist=True)[0].cpu()
    
    raw_targets = []
    for box in results.boxes.data.tolist():
        # get all the relevant data of all boxes stored in a list of lists containing
        # [corner 1 x, corner 1 y, corner 2 x, corner 2 y, track id, confidence, classification]
        
        # sometimes the tracking system won't return an ID, insert None if this is the case
        if len(box) == 6:
            box.insert(4, None)
        
        # if the object is classified as a person and the confidence is above the minimum threshold
        if int(box[6]) == _PERSON_CLASS_ID and box[5] > _MIN_CONFIDENCE:
            raw_targets.append(box)
    
    annotated_frame = results.plot()
    
    return FrameData(
        targets=[Target(*target) for target in raw_targets],
        frame_width=_VIDEO_WIDTH,
        frame_height=_VIDEO_HEIGHT,
        annotated_frame=annotated_frame
    )


def main() -> None:
    # this function is just for testing and is not used in prod
    while True:
        try:
            get_frame_data()
            
        except KeyboardInterrupt:
            break


# only call main() main when this file is ran directly as opposed to imported
if __name__ == "__main__":
    main()
