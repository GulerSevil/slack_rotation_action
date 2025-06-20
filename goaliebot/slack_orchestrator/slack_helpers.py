from goaliebot.slack_api import (
    update_usergroup_with_goalie_and_deputy,
    update_channel_description,
    send_goalie_notification,
)
from goaliebot.core.models import Command


def format_cadence_text(cadence):
    cadence_str = cadence.value if hasattr(cadence, "value") else cadence
    if cadence_str == "day":
        return "today"
    elif cadence_str == "week":
        return "this week"
    elif cadence_str == "month":
        return "this month"
    else:
        return f"this {cadence_str}"


def compose_goalie_notification(next_goalie, next_deputy, user_group_id, cadence):
    cadence_text = format_cadence_text(cadence)
    if next_deputy:
        return (
            f"🎉 <@{next_goalie.user_id}> is the goalie {cadence_text}! "
            f"👮‍♂️ Your trusty deputy is <@{next_deputy.user_id}> 🙌. "
            f"Give the team a nudge with <!subteam^{user_group_id}>! 🎉"
        )
    return (
        f"🎉 <@{next_goalie.user_id}> is the goalie today! No deputy assigned. "
        f"Use <!subteam^{user_group_id}> to reach out. 🎯"
    )


def perform_slack_rotation_updates(
    client, slack_channels, user_group_id, next_goalie, next_deputy, message, commands
):
    if Command.UPDATE_USER_GROUP in commands:
        update_usergroup_with_goalie_and_deputy(
            client, user_group_id, next_goalie, next_deputy
        )

    if Command.UPDATE_TOPIC_DESCRIPTION in commands:
        update_channel_description(client, slack_channels, message)

    if Command.SEND_SLACK_MESSAGE in commands:
        send_goalie_notification(client, slack_channels, message)
