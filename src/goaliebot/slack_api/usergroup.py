from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import re


def get_user_group_id(slack_token, user_group_handle):
    """Fetch the user group ID from the user group handle."""
    client = WebClient(token=slack_token)
    try:
        response = client.usergroups_list()
        for group in response["usergroups"]:
            if group["handle"] == user_group_handle:
                return group["id"]
    except SlackApiError as e:
        print(f"Error fetching user groups: {e.response['error']}")
    return None


def is_valid_user_id(user_id):
    """Validate Slack user ID format (must start with U or W and be alphanumeric)."""
    return bool(user_id) and re.match(r"^[UW][A-Z0-9]{2,}$", user_id)


def update_usergroup_with_goalie_and_deputy(client, user_group_id, next_goalie, deputy):
    """
    Update the Slack user group with the next goaliebot and optionally a deputy.

    Parameters:
    - client: An instance of the Slack WebClient.
    - user_group_id: The ID of the Slack user group to update.
    - next_goalie: The next User object to be assigned as the goaliebot.
    - deputy: The current goaliebot User object who becomes the deputy (can be None).
    """
    try:
        user_ids = []

        if is_valid_user_id(next_goalie.user_id):
            user_ids.append(next_goalie.user_id)
        else:
            raise ValueError(f"Invalid goaliebot user_id: {next_goalie.user_id}")

        if deputy:
            if is_valid_user_id(deputy.user_id):
                user_ids.append(deputy.user_id)
            else:
                raise ValueError(f"Invalid deputy user_id: {deputy.user_id}")

        response = client.usergroups_users_update(
            usergroup=user_group_id, users=",".join(user_ids)
        )

        print(
            f"✅ User {next_goalie.handle} (ID: {next_goalie.user_id}) is now the goaliebot and added to group {user_group_id}."
        )
        if deputy:
            print(f"✅ Deputy is {deputy.handle} (ID: {deputy.user_id}).")
        print(f"Slack API response: {response}")

    except (SlackApiError, ValueError) as e:
        print(f"❌ Error updating user group in Slack: {e}")
