from serial import Serial
from dataclasses import dataclass


@dataclass(slots=True)
class Message:
    message_id: int
    request_kind: str
    request_type: type
    payload: int | float | str | bool


class API:
    
    __slots__ = ["message_array", ]
        
        
def main():
    pass


if __name__ == "__main__":
    main()
