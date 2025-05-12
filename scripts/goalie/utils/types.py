from dataclasses import dataclass

@dataclass(frozen=True)
class SlackUser:
    handle: str
    user_id: str

