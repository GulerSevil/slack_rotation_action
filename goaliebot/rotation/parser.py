from .models import SlackUser


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
