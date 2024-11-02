import cv2
from serial import Serial
from time import sleep
from vision import get_frame_data


COM_PORT: str = "COM4"
BAUD_RATE: int = 9600


def send_command(arduino: Serial, *, angle: tuple[int, int] = None, home: bool = False, trigger: bool = False) -> None:
    
    if trigger:
        arduino.write("trigger\n".encode())
    
    elif home:
        arduino.write("home\n".encode())
    
    elif angle is not None:
        angle_command = "r"
        dx, dy = angle
        angle_command += f"{dx},{dy}\n"
        print(angle_command)
        arduino.write(angle_command.encode())


def calculate_rotation(dx: int, dy: int) -> tuple[int, int]:
    return -dx, -dy


def main():
    
    # establish arduino connection and give time it time to initialize
    # running in context manager such that the connection gets closed properly if an exception is raised during runtime
    with Serial(port=COM_PORT, baudrate=BAUD_RATE) as arduino:
        sleep(2)
        
        running = True
        
        while running:
            
            # wait until arduino is ready for next command
            if not arduino.readline().strip() == b"ready":
                continue
            
            frame_data = get_frame_data()
            
            if frame_data.targets:
                dx = frame_data.targets[0].center_x - frame_data.frame_width // 2
                dy = frame_data.targets[0].center_y - frame_data.frame_height // 2
                angles = calculate_rotation(dx=dx, dy=dy)
                send_command(arduino=arduino, angle=angles)
            
            cv2.imshow(winname="vision", mat=frame_data.annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord("q"):
                running = False
            
        
# only call main() main when this file is ran directly as opposed to imported
if __name__ == "__main__":
    main()
