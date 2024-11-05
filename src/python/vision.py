from tomllib import load
from dataclasses import dataclass

import numpy as np
from webcam import Webcam
import cv2
from ultralytics import YOLO


# load configuration data
with open("./config.toml", "rb") as config_file:
    CONFIG_DICT: dict = load(config_file)

# initializes ML model and camera
_model: YOLO = YOLO(CONFIG_DICT["model-path"])
_camera: Webcam = Webcam(src=CONFIG_DICT["video-source"], w=CONFIG_DICT["video-width"], h=CONFIG_DICT["video-height"])


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
        "size_y",
        "hitbox_center_x",
        "hitbox_center_y",
        "hitbox1_x",
        "hitbox1_y",
        "hitbox2_x",
        "hitbox2_y"
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
        # defines the corners of the target box
        self.corner1_x: int = round(c1x)
        self.corner1_y: int = round(c1y)
        self.corner2_x: int = round(c2x)
        self.corner2_y: int = round(c2y)
        
        # defines the center and size of the target box
        self.center_x: int = (self.corner1_x + self.corner2_x) // 2
        self.center_y: int = (self.corner1_y + self.corner2_y) // 2
        self.size_x: int = abs(self.corner1_x - self.center_x)
        self.size_y: int = abs(self.corner1_y - self.center_y)
        
        # defines the center and corners of the target hitbox
        self.hitbox_center_x: int = self.center_x + int(self.size_x * CONFIG_DICT["hitbox-offset-x-fraction"])
        self.hitbox_center_y: int = self.center_y + int(self.size_y * CONFIG_DICT["hitbox-offset-y-fraction"])
        self.hitbox1_x: int = self.hitbox_center_x - int(self.size_x * CONFIG_DICT["hitbox-size-fraction"])
        self.hitbox1_y: int = self.hitbox_center_y - int(self.size_y * CONFIG_DICT["hitbox-size-fraction"])
        self.hitbox2_x: int = self.hitbox_center_x + int(self.size_x * CONFIG_DICT["hitbox-size-fraction"])
        self.hitbox2_y: int = self.hitbox_center_y + int(self.size_x * CONFIG_DICT["hitbox-size-fraction"])
        
        # the code expects something for track_id so if it is not
        self.track_id: int | None = int(track_id) if track_id is not None else None
        self.confidence: float = confidence
        self.classification: int = int(classification)


# old implementation
# @dataclass(slots=True)
# class FrameData:
#     targets: list[Target]
#     frame: np.ndarray


# function which allows the code to use the webcam
def get_frame_data() -> tuple[list[Target], np.ndarray]:
    
    """
    Gets the most recent frame from the configured camera, uses a pretrained model to identify objects in the image,
    makes a list of all Target objects that fit the configured constraints.
    
    :return: (tuple[list[Target], np.ndarray]) the list of targets and the raw frame
    """
    
    # get frame from camera and convert to BGR because cv2 works with BGR for some reason
    frame = _camera.read_next_frame()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # use machine learning model to classify objects in frame and save to cpu memory
    results = _model.track(frame, persist=True, verbose=False)[0].cpu()
    # creates an empty array for the recognized targets
    raw_targets = []
    for box in results.boxes.data.tolist():
        # get all the relevant data of all boxes stored in a list of lists containing
        # [corner 1 x, corner 1 y, corner 2 x, corner 2 y, track id, confidence, classification]
        
        # sometimes the tracking system won't return an ID, insert None if this is the case
        if len(box) == 6:
            box.insert(4, None)
        
        # if the object is not classified as a person start next iteration early
        if int(box[6]) != CONFIG_DICT["person-class-id"]:
            continue
        
        # if the confidence is below the minimum threshold start next iteration early
        if box[5] < CONFIG_DICT["min-confidence"]:
            continue
        
        # if the box is too small horizontally start next iteration early
        if abs(box[0] - box[2]) < CONFIG_DICT["min-target-size-x"]:
            continue
        
        # if the box is too small vertically start next iteration early
        if abs(box[1] - box[3]) < CONFIG_DICT["min-target-size-y"]:
            continue
            
        # adds the box to the target list, thus creates a list of lists
        raw_targets.append(box)
    
    # convert raw targets to Target objects, *target unpacks list into function arguments for __init__()
    return [Target(*target) for target in raw_targets], frame


def main() -> None:
    # this function is just for testing and is not used in prod
    pass


if __name__ == "__main__":
    main()
