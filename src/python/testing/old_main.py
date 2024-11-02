from serial import Serial
from time import sleep

COM_PORT: str = "COM4"
BAUD_RATE: int = 9600


def send_message(message: str, serial: Serial) -> None:
    embed = f"{message}".encode(encoding="ascii")
    serial.write(embed)


def main() -> None:
    arduino = Serial(port=COM_PORT, baudrate=BAUD_RATE, timeout=1)
    sleep(2)
    arduino.write("test".encode())
    
    sleep(2)
    if arduino.in_waiting > 0:
        response = arduino.readline().decode().strip()
        print("Arduino response: ", response)
    
    # while True:
    #     try:
    #         # sleep(1)
    #         arduino.write(b"t")
    #     except KeyboardInterrupt:
    #         break
    # arduino.close()


if __name__ == "__main__":
    main()
