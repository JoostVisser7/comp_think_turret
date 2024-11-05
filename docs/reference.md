# comp_think_turret code reference

## Function and class reference

### main.py

#### main()

Main program loop. The high level operations of the loop are: Waiting for the arduino to be ready; getting and sorting 
the detected targets; detecting and responding to user input; constructing and sending commands to arduino; annotating 
and displaying camera view; repeat.

#### ensure_target_order(unsorted_targets: list[Target], old_sequence: list[int])

Each loop the ML model might return potential targets in any arbitrary sequence. The primary target is selected as the 
first entry in the target list. To ensure consistency for selecting the primary target and switching targets, this 
function matches the sequence of the new targets to the sequence of the old targets. Old targets no longer present in 
the new list are removed, new targets that weren't present in the old sequence are appended to the end.

Parameters
: - unsorted_targets (list[target]) - list of the new targets
: - old_sequence (list[int]) - list of previous sequence

Returns
: the list of targets in the correct sequence and a list containing the new sequence

Return type
: tuple[list[Target], list[int]]

#### calculate_rotation(dx: int, dy: int)

Takes the difference from frame center to the hitbox center in pixels and converts it to degrees to send to the arduino. 
This function can be changed to any conversion operation to tune the behaviour of the turret.

Parameters
: - dx (int) - pixel difference between frame center and target hitbox center in x
: - dy (int) - pixel difference between frame center and target hitbox center in y

Returns
: the amount of degrees in the x and y direction that the servos need to turn

Return type
: tuple[int, int]

#### send_command(arduino: Serial, *, rotate: tuple[int, int] = None, home: bool = False, trigger: bool = False)

Interface with the arduino, converts function arguments to commands. If multiple arguments are given, it will send the 
highest priority command. Command priority is as follows: trigger > home > rotate.

Parameters
: arduino (Serial) - the arduino to send the command to
: rotate (tuple[int, int]) - degrees of x and degrees of y to turn
: home (bool) - set to True if the turret must return to configured home position
: trigger (bool) - set to True if the turret must fire a dart

Raises
: ValueError - no rotation values were given and both `home` and `trigger` are set to `False`, no command can be sent.

### vision.py

#### get_frame_data()

Gets the most recent frame from the configured camera, uses a pretrained model to identify objects in the image, makes a 
list of all Target objects that fit the configured constraints.

Returns
: A list of Target object that were dectected and passed the detection criteria and the raw frame captured by the camera

Return type
: tuple[list[Target], numpy.ndarray]

#### class Target:

A class that stores all the relevant data for a target as classified by the YOLO model.

Constructor parameters
: c1x (float) - the x-coordinate of corner 1 of the target box
: c1y (float) - the y-coordinate of corner 1 of the target box
: c2x (float) - the x-coordinate of corner 2 of the target box
: c2y (float) - the y-coordinate of corner 2 of the target box
: track_id (float | None) - the target ID given by the YOLO model
: confidence (float) - the confidence in the target classification by the YOLO model
: classification (float) - the classification of the target by the YOLO model

Attributes
: c1x (int) - the pixel x-coordinate of corner 1 of the target box
: c1y (int) - the pixel y-coordinate of corner 1 of the target box
: c2x (int) - the pixel x-coordinate of corner 2 of the target box
: c2y (int) - the pixel y-coordinate of corner 2 of the target box
: center_x (int) - the pixel x-coordinate of the center of the target box
: center_y (int) - the pixel y-coordinate of the center of the target box
: size_x (int) - the pixel size of the target box along the x-axis
: size_y (int) - the pixel size of the target box along the y-axis
: hitbox_center_x (int) - the pixel x-coordinate of the center of the target hitbox
: hitbox_center_y (int) - the pixel y-coordinate of the center of the target hitbox
: hitbox1_x (int) - the pixel x-coordinate of corner 1 of the target hitbox
: hitbox1_y (int) - the pixel y-coordinate of corner 1 of the target hitbox
: hitbox2_x (int) - the pixel x-coordinate of corner 2 of the target hitbox
: hitbox2_y (int) - the pixel y-coordinate of corner 2 of the target hitbox
: track_id (int | None) - the target ID given by the YOLO model
: confidence (float) - the confidence in the target classification by the YOLO model
: classification (int) - the classification of the target by the YOLO model


### arduino.ino

#### clamp_angle(int current, int adjustment, int min, int max)

Make sure the new target angle does not exceed allowable values.

Parameters
: current (int) - the current angle of the servo on a given axis
: adjustment (int) - the amount that the angle is requested to change
: min (int) - the minimum angle the servo is allowed to assume
: max (int) - the maximum angle the servo is allowed to assume

Returns
: The adjusted angle, clamped between the min and max angles

Return type
: int

#### adjust_rotation(char axis, int adjustment)

Wrapper for clamp_angle() to adjust the angle on a given axis.

Parameters
: axis (char) - accepts 'x' or 'y' for the axis to just the rotation for
: adjustment (int) - the amount of degrees to adjust the axis by

#### message_parser(String message)

Interprets the incoming messages, calls the appropriate functions and sets the appropriate states.

Parameters
: message (String) - the command received by the serial port

---
## Style guide and coding conventions
Both Python and Arduino are written according to the PEP8 style guide. 

#### Variables
Variable conventions are as follows:
- variable_name
- _private_variable_name
- CONSTANT_NAME

#### Multi-line code
Multi-line function definitions, function calls, if/else-statements, etc. are written in the Kernighan & Ritchie (K&R) 
style. Example below:
```python
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
    ...  # some code
```

#### Type hinting
Function definitions always have type hints for their arguments, as well as a return type. Example below:
```python
def ensure_target_order(unsorted_targets: list[Target], old_sequence: list[int]) -> tuple[list[Target], list[int]]:
    ...  # some code
```