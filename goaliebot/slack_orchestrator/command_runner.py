from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .slack_helpers import (
    compose_goalie_notification,
    perform_slack_rotation_updates,
)
from .summary import print_success_summary
import sys


def run_slack_commands(
    slack_token, slack_channels, next_goalie, next_deputy, user_group_id, commands
):
    client = WebClient(token=slack_token)
    message = compose_goalie_notification(next_goalie, next_deputy, user_group_id)

    try:
        perform_slack_rotation_updates(
            client,
            slack_channels,
            user_group_id,
            next_goalie,
            next_deputy,
            message,
            commands,
        )
        print_success_summary(
            next_goalie, next_deputy, slack_channels, user_group_id, commands
        )
    except SlackApiError as e:
        print(
            "❌ Failed to update Slack state (user group, channel description, or goaliebot notification)."
        )
        print(f"Error: {e.response['error']}")
        sys.exit(1)
