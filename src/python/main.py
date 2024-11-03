from tomllib import load
from time import time, sleep

import cv2
from serial import Serial

from vision import get_frame_data, Target


# load configuration data
with open("./config.toml", "rb") as config_file:
    CONFIG_DICT: dict = load(config_file)


def send_command(arduino: Serial, *, angle: tuple[int, int] = None, home: bool = False, trigger: bool = False) -> None:
    
    if trigger:
        arduino.write("trigger\n".encode())
    
    elif home:
        arduino.write("home\n".encode())
    
    elif angle is not None:
        dx, dy = angle
        angle_command = f"r{dx},{dy}\n"
        arduino.write(angle_command.encode())


def calculate_rotation(dx: int, dy: int) -> tuple[int, int]:
    
    return -dx, -dy


def ensure_target_order(unsorted_targets: list[Target], old_order: list[int]) -> tuple[list, list]:
    sorted_targets = []
    new_order = []
    
    # for every target id in order, remove the target with the same track_id from the unsorted list and add it to the
    # sorted list
    for target_id in old_order:
        target_index = next((i for i, target in enumerate(unsorted_targets) if target.track_id == target_id), None)
        if target_index is not None:
            sorted_targets.append(unsorted_targets.pop(target_index))
            new_order.append(target_id)
    
    # add remaining (new) target ids to sorted list
    sorted_targets += unsorted_targets
    new_order = [target.track_id for target in sorted_targets]
    
    return sorted_targets, new_order


def main():
    
    # establish arduino connection and give the microcontroller time to initialize
    # running in context manager such that the connection gets closed properly if an exception is raised during runtime
    with Serial(port=CONFIG_DICT["com-port"], baudrate=CONFIG_DICT["baud-rate"]) as arduino:
        sleep(2)
        
        running = True
        key_released = True
        
        trigger_ready = True
        trigger_cooldown_start = time()
        
        target_order = []
        
        while running:
            trigger = False
            
            # wait until arduino is ready for next command
            if not arduino.readline().strip() == b"ready":
                continue
            
            frame_data = get_frame_data()
            frame_data.targets, target_order = ensure_target_order(frame_data.targets, target_order)
            
            # ----- recording key presses -----
            
            keypress = cv2.waitKey(1) & 0xFF
            
            # if user presses "q": end the program
            if keypress == ord("q"):
                running = False
            
            # if users presses ",": move first target to end of list
            elif keypress == ord(",") and key_released:
                frame_data.targets.append(frame_data.targets.pop(0))
                target_order.append(target_order.pop(0))
                key_released = False
            
            # if user presses ".": move last target to beginning of list
            elif keypress == ord(".") and key_released:
                frame_data.targets.insert(0, frame_data.targets.pop(-1))
                target_order.insert(0, target_order.pop(-1))
                key_released = False
            
            # cv2.waitKey() returns 255 if no key is pressed
            elif keypress == 255:
                key_released = True
            
            # ----- determining command to send to arduino -----
            
            if time() - trigger_cooldown_start >= CONFIG_DICT["trigger-cooldown-seconds"]:
                trigger_ready = True
            
            if frame_data.targets:
                dx = frame_data.targets[0].hitbox_center_x - CONFIG_DICT["video-width"] // 2
                dy = frame_data.targets[0].hitbox_center_y - CONFIG_DICT["video-height"] // 2
                
                if (
                    abs(dx) <= int(frame_data.targets[0].size_x * CONFIG_DICT["hitbox-size-fraction"]) and
                    abs(dy) <= int(frame_data.targets[0].size_y * CONFIG_DICT["hitbox-size-fraction"]) and
                    trigger_ready
                ):
                    trigger = True
                    trigger_ready = False
                    trigger_cooldown_start = time()
            else:
                dx = dy = 0
            angles = calculate_rotation(dx=dx, dy=dy)
            send_command(arduino=arduino, angle=angles, trigger=trigger)
            
            # ----- drawing and annotating frame -----
            
            for i, target in enumerate(frame_data.targets):
                box_colour = 255, 0, 0  # blue
                if not i:
                    box_colour = 0, 255, 255  # yellow
                    frame_data.frame = cv2.rectangle(
                        img=frame_data.frame,
                        pt1=(target.hitbox1_x, target.hitbox1_y),
                        pt2=(target.hitbox2_x, target.hitbox2_y),
                        color=box_colour,
                        thickness=2
                    )
                frame_data.frame = cv2.rectangle(
                    img=frame_data.frame,
                    pt1=(target.corner1_x, target.corner1_y),
                    pt2=(target.corner2_x, target.corner2_y),
                    color=box_colour,
                    thickness=2
                )
                frame_data.frame = cv2.circle(
                    img=frame_data.frame,
                    center=(CONFIG_DICT["video-width"] // 2, CONFIG_DICT["video-height"] // 2),
                    radius=2,
                    color=(0, 0, 255),   # red
                    thickness=-1
                )
            
            cv2.imshow(winname="vision", mat=frame_data.frame)
        
        send_command(arduino=arduino, home=True)
            
        
# only call main() main when this file is ran directly as opposed to imported
if __name__ == "__main__":
    main()
