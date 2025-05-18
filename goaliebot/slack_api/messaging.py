from slack_sdk.errors import SlackApiError


def send_goalie_notification(client, slack_channels, message):
    """
    Send a notification to Slack channels announcing the new goaliebot and deputy.

    Parameters:
    - client: An instance of the Slack WebClient.
    - slack_channels: A list of Slack channel IDs or names to send the notification to.
    - next_goalie: The next User object to be assigned as the goaliebot.
    - deputy: The current goaliebot User object who becomes the deputy.
    - user_group_id: The Slack user group ID that represents the team or group.
    """

    for channel in slack_channels:
        try:
            response = client.chat_postMessage(
                type="mrkdown", channel=channel, text=message
            )
            print(f"Message sent to {channel}. Response: {response}")

        except SlackApiError as e:
            print(
                f"Error sending message to Slack channel {channel}: {e.response['error']}"
            )
