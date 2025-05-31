from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class SlackUser:
    handle: str
    user_id: str


class Command(Enum):
    UPDATE_TOPIC_DESCRIPTION = "update_topic_description"
    SEND_SLACK_MESSAGE = "send_slack_message"
    UPDATE_USER_GROUP = "update_user_group"

    def __str__(self):
        return self.value


class Cadence(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

    def __str__(self):
        return self.value
