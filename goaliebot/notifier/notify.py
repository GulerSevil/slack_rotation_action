from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .slack_helpers import (
    compose_goalie_notification,
    update_slack_state,
)
from .summary import print_success_summary
import sys


def notify_in_slack(
    slack_token, slack_channels, next_goalie, next_deputy, user_group_id
):
    client = WebClient(token=slack_token)
    message = compose_goalie_notification(next_goalie, next_deputy, user_group_id)

    try:
        update_slack_state(
            client, slack_channels, user_group_id, next_goalie, next_deputy, message
        )
        print_success_summary(next_goalie, next_deputy, slack_channels, user_group_id)
    except SlackApiError as e:
        print(
            "❌ Failed to update Slack state (user group, channel description, or goaliebot notification)."
        )
        print(f"Error: {e.response['error']}")
        sys.exit(1)
