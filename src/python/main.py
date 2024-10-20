from serial import Serial
from time import sleep

COM_PORT: str = "COM4"
BAUD_RATE: str = "600"


def send_message(message: str, serial: Serial) -> None:
    embed = f"{message}".encode(encoding="ascii")
    print(embed)
    serial.write(embed)


def main() -> None:
    with Serial(port=COM_PORT, baudrate=BAUD_RATE) as arduino:
        arduino.flush()
        send_message(message="t", serial=arduino)


if __name__ == "__main__":
    main()
