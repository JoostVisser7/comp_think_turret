import cv2
from ultralytics import YOLO
from webcam import Webcam
import numpy as np

_FRAME_WIDTH: int = 640
_FRAME_HEIGHT: int = 480

_PERSON_CLASS_ID: int = 0
_MIN_CONFIDENCE: float = 0.8

_model = YOLO("./yolo_models/640x480_100epoch.pt")
_webcam = Webcam(src=0, w=_FRAME_WIDTH, h=_FRAME_HEIGHT)

#hallo mensen
#hi
#hi2

def draw_cross(
        frame: np.ndarray,
        center: tuple[int, int],
        size: int = 20,
        color: tuple[float, float, float] = (0., 0., 0.),
        thickness: int = 2
) -> np.ndarray:
    add_vert = cv2.line(
        img=frame,
        pt1=(center[0], center[1] - size // 2),
        pt2=(center[0], center[1] + size // 2),
        color=color,
        thickness=thickness
    )
    add_hor = cv2.line(
        img=add_vert,
        pt1=(center[0] - size // 2, center[1]),
        pt2=(center[0] + size // 2, center[1]),
        color=color,
        thickness=thickness
    )
    return add_hor


def main():
    
    # initial model training
    # train_results = _model.train(
    #     data="coco8.yaml",
    #     epochs=100,
    #     imgsz=_FRAME_WIDTH,
    #     device="cpu"
    # )
    #
    # metrics = _model.val()
    
    for frame in _webcam:
        # swap colour channels because cv2 works with BGR instead of RGB values for some reason
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # track object and copy tracking data to cpu memory
        results = _model.track(frame, persist=True)[0].cpu()
        
        # create annotated frame with detection boxes, labels and confidence values
        annotated_frame = results.plot()
        
        # get all the relevant data of all boxes stored in a list of lists containing
        # [corner 1 x, corner 1 y, corner 2 x, corner 2 y, track id, confidence, classification]
        boxes = results.boxes.data.tolist()
        
        # go over all the boxes, check if they are classified as person and put a crosshair if the confidence is greater
        # than specified by _MIN_CONFIDENCE
        for box in boxes:
            c1x, c1y, c2x, c2y, track_id, conf, cls = tuple(box)
            box_center = int((c1x + c2x) / 2), int((c1y + c2y) / 2)
            
            if int(cls) == _PERSON_CLASS_ID and conf >= _MIN_CONFIDENCE:
                annotated_frame = draw_cross(frame=annotated_frame, center=box_center, color=(255., 0., 0.))
                annotated_frame = cv2.putText(
                    img=annotated_frame,
                    text=f"dx = {box_center[0] - _FRAME_WIDTH // 2}; dy {box_center[1] - _FRAME_HEIGHT // 2}",
                    org=(10, _FRAME_HEIGHT - 10),
                    fontFace=cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1,
                    color=(0., 255., 0.),
                    thickness=1,
                    lineType=cv2.LINE_AA,
                    bottomLeftOrigin=False,
                )
        
        # draw center crosshair
        annotated_frame = draw_cross(
            frame=annotated_frame,
            center=(_FRAME_WIDTH // 2, _FRAME_HEIGHT // 2),
            color=(0., 255., 0.)
        )
        
        cv2.imshow("Webcam Frame", annotated_frame)
        
        # exit loop if user presses q
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    

if __name__ == "__main__":
    main()
