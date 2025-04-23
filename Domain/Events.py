from dataclasses import dataclass
import time

@dataclass
class Event:
    timestamp: float
    type: str
    description: str

def create_event(event_type, description):
    return Event(
        timestamp=time.time(),
        type=event_type,
        description=description
    )
