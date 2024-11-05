# Project Computational Thinking
This project aims to show our understanding of the programming world. The assignment is to write code which can interact with an arduino to achieve a certain goal.
The goal of our project is to make a self-aiming turret. This will be achieved by using a webcam, detecting the targets, aiming at the targets and finally pull the trigger.
For detecting the targets a 3rd party library is used. This library is called ultralytics, which uses the YOLO11n model. This library uses ML computer vision to identify persons in the frame of the webcam, this information is used to determine the vertical and horizontal distance between the target and the middle of the screen.
These distance variables are communicated to the arduino, which in turn controls the servos to rotate the setup. When the center of the frame touches the hitbox of the identified target, the trigger mechanism is activated. 
This mechanism makes sure that the servo which controls the trigger is contracted, finishing the procedure.

## Requirements to run the code
Before it is explained how to use the code, you need to make sure that you have the right packages installed. These packages can be found in ./requirements.txt. Furthermore, make sure to configure the code to your setup. You will need different values for the constants in the arduino file, which fit your setup.

## User guideline
To start the procedure, make sure that the arduino code is uploaded to the arduino. Then you can run the python code. Ones the code is running you can do a couple of actions as the user.
1. Q can be pressed to end the program
2. The comma key can be pressed to switch between target
3. The dot key can be pressed to switch back between targets
4. H can be pressed to command the setup to return to its home position

The selected target will show a yellow hitbox and the remaining targets will show a blue hitbox.

If there are any questions on how the code works, you can look up the documentation of the code in ./docs/reference.md or look at the commends above the code.

