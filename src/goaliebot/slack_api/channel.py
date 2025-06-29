from slack_sdk.errors import SlackApiError


def update_channel_description(client, slack_channels, new_description):
    """
    Update the description of a Slack channel.

     Parameters:
    - client: An instance of the Slack WebClient.
    - slack_channels: A list of Slack channel IDs or names to send the notification to.
    - new_description: The new description to set for the channel.
    """
    for channel in slack_channels:
        print(f"Updating description for channel: {channel}")
        try:
            channel_id = get_channel_id(client, channel)
            response = client.conversations_setTopic(
                channel=channel_id, topic=new_description
            )
            print(
                f"Channel description updated to: {new_description}. Response: {response}"
            )

        except SlackApiError as e:
            print(f"Error updating channel description: {e.response['error']}")


def get_channel_id(client, channel_handle):
    """Fetch the channel ID from the channel handle."""
    try:
        cursor = None
        while True:
            response = client.conversations_list(cursor=cursor)
            for channel in response["channels"]:
                if channel["name"] == channel_handle.strip("#"):
                    return channel["id"]

            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        print(f"Channel {channel_handle} not found.")
        return None

    except SlackApiError as e:
        print(f"Error fetching channels: {e.response['error']}")
        return None
