from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def get_user_group_id(slack_token, user_group_handle):
    """Fetch the user group ID from the user group handle."""
    client = WebClient(token=slack_token)
    try:
        response = client.usergroups_list()
        for group in response['usergroups']:
            if group['handle'] == user_group_handle:
                return group['id']
    except SlackApiError as e:
        print(f"Error fetching user groups: {e.response['error']}")
    return None

def update_usergroup_with_goalie_and_deputy(client, user_group_id, next_goalie, deputy):
    """
    Update the Slack user group with the next goalie and the current deputy.

    Parameters:
    - client: An instance of the Slack WebClient.
    - user_group_id: The ID of the Slack user group to update.
    - next_goalie: The next User object to be assigned as the goalie.
    - deputy: The current goalie User object who becomes the deputy.
    """
    try:
        # Update the user group with the next goalie and current deputy
        response = client.usergroups_users_update(
            usergroup=user_group_id,
            users=f"{next_goalie.user_id},{deputy.user_id}" 
        )
        
        print(f"User {next_goalie.handle} (ID: {next_goalie.user_id}) is now the goalie and added to group {user_group_id}.")
        print(f"Deputy is {deputy.handle} (ID: {deputy.user_id}). Response: {response}")

    except SlackApiError as e:
        print(f"Error updating user group in Slack: {e.response['error']}")

def send_goalie_notification(client, slack_channels, message):
    """
    Send a notification to Slack channels announcing the new goalie and deputy.

    Parameters:
    - client: An instance of the Slack WebClient.
    - slack_channels: A list of Slack channel IDs or names to send the notification to.
    - next_goalie: The next User object to be assigned as the goalie.
    - deputy: The current goalie User object who becomes the deputy.
    - user_group_id: The Slack user group ID that represents the team or group.
    """
    
    for channel in slack_channels:
        try:
            response = client.chat_postMessage(
                channel=channel,
                text=message
            )
            print(f"Message sent to {channel}. Response: {response}")

        except SlackApiError as e:
            print(f"Error sending message to Slack channel {channel}: {e.response['error']}")

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
                channel=channel_id,
                topic=new_description
            )
            print(f"Channel description updated to: {new_description}. Response: {response}")

        except SlackApiError as e:
            print(f"Error updating channel description: {e.response['error']}")

def get_channel_id(client, channel_handle):
    """Fetch the channel ID from the channel handle."""
    try:
        cursor = None
        while True:
            response = client.conversations_list(cursor=cursor)
            for channel in response['channels']:
                if channel['name'] == channel_handle.strip('#'):
                    return channel['id']
            
            cursor = response.get('response_metadata', {}).get('next_cursor')
            if not cursor:
                break

        print(f"Channel {channel_handle} not found.")
        return None

    except SlackApiError as e:
        print(f"Error fetching channels: {e.response['error']}")
        return None
