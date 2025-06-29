from .models import SlackUser
from .models import Command
import argparse


def parse_goalie_line(line: str) -> SlackUser:
    """Parse line like 'handle, user_id' or '**handle, user_id'."""
    handle, user_id = map(str.strip, line.replace("**", "").split(","))
    return SlackUser(handle, user_id)


def parse_fixed_full_line(line: str):
    """Parse fixed mode line: 'goalie_handle, goalie_id | deputy_handle, deputy_id'."""
    goalie_part, deputy_part = map(str.strip, line.split("|"))
    goalie_handle, goalie_id = map(str.strip, goalie_part.replace("**", "").split(","))
    deputy_handle, deputy_id = map(str.strip, deputy_part.split(","))

    goalie = SlackUser(goalie_handle, goalie_id)
    deputy = SlackUser(deputy_handle, deputy_id)
    is_current_goalie = "**" in goalie_part
    return goalie, deputy, is_current_goalie


def parse_commands(value: str | None):
    if not value or not value.strip():
        # Default to all commands
        return list(Command)
    try:
        return [Command(cmd.strip()) for cmd in value.split("|") if cmd.strip()]
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid command in list: {e}")
