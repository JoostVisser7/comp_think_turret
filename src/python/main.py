from tomllib import load
from time import time, sleep

import cv2
from serial import Serial
import numpy as np

from vision import get_frame_data, Target


# load configuration data
with open("./config.toml", "rb") as config_file:
    CONFIG_DICT: dict = load(config_file)


def send_command(arduino: Serial, *, rotate: tuple[int, int] = None, home: bool = False, trigger: bool = False) -> None:
    
    """
    Interface with the arduino, converts function arguments to commands. If multiple arguments are given,
    it will send the highest priority command. Command priority is as follows: trigger > home > rotate.

    :param arduino: (Serial) the arduino to send the command to.
    :param rotate: (tuple[int, int]) degrees of x and degrees of y to turn.
    :param home: (bool) set to True if the turret must return to configured home position.
    :param trigger: (bool) set to True if the turret must fire a dart.
    :return: (None)
    """
    
    if trigger:
        arduino.write("trigger\n".encode())
    
    elif home:
        arduino.write("home\n".encode())
    
    elif rotate is not None:
        dx, dy = rotate
        angle_command = f"r{dx},{dy}\n"
        arduino.write(angle_command.encode())
    
    else:
        raise ValueError("At least one command must be given")


def calculate_rotation(dx: int, dy: int) -> tuple[int, int]:
    
    """
    Takes the difference from frame center to the hitbox center in pixels and converts it to degrees to send to the
    arduino. This function can be changed to any conversion operation to tune the behaviour of the turret.
    
    :param dx: (int) pixel difference between frame center and target hitbox center in x
    :param dy: (int) pixel difference between frame center and target hitbox center in y
    :return: (tuple[int, int]) degrees to turn the horizontal direction and vertical direction
    """
    
    dx = -np.sign(dx)
    dy = np.sign(dy)
    
    return dx, dy


def ensure_target_order(unsorted_targets: list[Target], old_sequence: list[int]) -> tuple[list[Target], list[int]]:
    
    """
    Each loop the ML model might return potential targets in any arbitrary sequence. The primary target is selected as
    the first entry in the target list. To ensure consistency for selecting the primary target and switching targets,
    this function matches the sequence of the new targets to the sequence of the old targets. Old targets no longer
    present in the new list are removed, new targets that weren't present in the old sequence are appended to the end.
    
    :param unsorted_targets: (list[Target]) list of the new targets
    :param old_sequence: (list[int]) list of previous sequence
    :return: (tuple[list[Target], list[int]]) ordered sequence of targets, new sequence IDs
    """
    
    sorted_targets = []
    new_order = []
    
    # for every target id in order, remove the target with the same track_id from the unsorted list and add it to the
    # sorted list
    for target_id in old_sequence:
        target_index = next((i for i, target in enumerate(unsorted_targets) if target.track_id == target_id), None)
        if target_index is not None:
            sorted_targets.append(unsorted_targets.pop(target_index))
            new_order.append(target_id)
    
    # add remaining (new) target ids to sorted list
    sorted_targets += unsorted_targets
    new_order = [target.track_id for target in sorted_targets]
    
    return sorted_targets, new_order


def main():
    
    """
    Main loop. The high level operations of the loop are: Waiting for the arduino to be ready getting and sorting the
    detected targets; detecting and responding to user input; constructing and sending commands to arduino; annotating
    and displaying camera view; repeat.
    
    :return: (None)
    """
    
    # establish arduino connection and give the microcontroller time to initialize
    # running in context manager so that the connection gets closed properly if an exception is raised during runtime
    with Serial(port=CONFIG_DICT["com-port"], baudrate=CONFIG_DICT["baud-rate"]) as arduino:
        sleep(2)
        
        # setting up runtime states
        running = True
        key_released = True
        arm_trigger = True
        trigger_cooldown_start = time()
        
        target_sequence = []
        
        while running:
            trigger = False
            home = False
            
            # wait until arduino is ready for next command
            if not arduino.readline().strip() == b"ready":
                continue
            
            targets, frame = get_frame_data()
            targets, target_sequence = ensure_target_order(targets, target_sequence)
            
            # ----- recording key presses -----
            
            keypress = cv2.waitKey(1) & 0xFF
            
            # if user presses "q": end the program
            if keypress == ord("q"):
                running = False
            
            # if users presses ",": move first target to end of list
            elif keypress == ord(",") and key_released and targets:
                targets.append(targets.pop(0))
                target_sequence.append(target_sequence.pop(0))
                key_released = False
            
            # if user presses ".": move last target to beginning of list
            elif keypress == ord(".") and key_released and targets:
                targets.insert(0, targets.pop(-1))
                target_sequence.insert(0, target_sequence.pop(-1))
                key_released = False
            
            # if user presses "h" turret moves to its home position
            elif keypress == ord("h") and key_released:
                home = True
                key_released = False
            
            # cv2.waitKey() returns 255 if no key is pressed
            elif keypress == 255:
                key_released = True
            
            # ----- determining command to send to arduino -----
            
            # check whether cooldown is finished and arm trigger if this is the case.
            if time() - trigger_cooldown_start >= CONFIG_DICT["trigger-cooldown-seconds"]:
                arm_trigger = True
            
            if targets:
                
                # get pixel difference between target hitbox and center of frame
                dx = targets[0].hitbox_center_x - CONFIG_DICT["video-width"] // 2
                dy = targets[0].hitbox_center_y - CONFIG_DICT["video-height"] // 2
                
                # check if firing conditions apply and fire trigger
                if (
                    abs(dx) <= int(targets[0].size_x * CONFIG_DICT["hitbox-size-fraction"]) and
                    abs(dy) <= int(targets[0].size_y * CONFIG_DICT["hitbox-size-fraction"]) and
                    arm_trigger
                ):
                    trigger = True
                    arm_trigger = False
                    trigger_cooldown_start = time()
            else:
                dx = dy = 0
            angles = calculate_rotation(dx=dx, dy=dy)
            
            send_command(arduino=arduino, rotate=angles, trigger=trigger, home=home)
            
            # ----- annotating frame -----
            
            for i, target in enumerate(targets):
                # set box colour to blue
                box_colour = 255, 0, 0  # blue
                
                # check if target is primary target
                if not i:
                    # set box colour to yellow and draw hitbox on primary target
                    box_colour = 0, 255, 255  # yellow
                    frame = cv2.rectangle(
                        img=frame,
                        pt1=(target.hitbox1_x, target.hitbox1_y),
                        pt2=(target.hitbox2_x, target.hitbox2_y),
                        color=box_colour,
                        thickness=2
                    )
                
                # draw target box around target
                frame = cv2.rectangle(
                    img=frame,
                    pt1=(target.corner1_x, target.corner1_y),
                    pt2=(target.corner2_x, target.corner2_y),
                    color=box_colour,
                    thickness=2
                )
                
            # draw red dot at center of frame
            frame = cv2.circle(
                img=frame,
                center=(CONFIG_DICT["video-width"] // 2, CONFIG_DICT["video-height"] // 2),
                radius=2,
                color=(0, 0, 255),   # red
                thickness=-1
            )
            
            # display image
            cv2.imshow(winname="vision", mat=frame)
        
        # turret return to home on shutdown
        send_command(arduino=arduino, home=True)
            
        
# only call main() main when this file is ran directly as opposed to imported
if __name__ == "__main__":
    main()
