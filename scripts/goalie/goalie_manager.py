import sys
import argparse
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from utils.file_ops import get_goalie_and_users, get_next_goalie_and_deputy, update_goalie_file
from utils.slack_api import get_user_group_id, send_goalie_notification, update_usergroup_with_goalie_and_deputy, update_channel_description


def notify_in_slack(slack_token, slack_channels, next_goalie, next_deputy, user_group_id):
    """Send message to multiple Slack channels and update user group."""
    client = WebClient(token=slack_token)

    goalie_notification = (
        f"🎉 <@{next_goalie.user_id}> is the goalie today! "
        f"👮‍♂️ Your trusty deputy is <@{next_deputy.user_id}> 🙌. "
        f"Give the team a nudge with <!subteam^{user_group_id}>! 🎉"
    ) if next_deputy else (
        f"🎉 <@{next_goalie.user_id}> is the goalie today! No deputy assigned. "
        f"Use <!subteam^{user_group_id}> to reach out. 🎯"
    )

    try:
        update_usergroup_with_goalie_and_deputy(client, user_group_id, next_goalie, next_deputy)
        update_channel_description(client, slack_channels, goalie_notification)
        send_goalie_notification(client, slack_channels, goalie_notification)

        # ✅ Success summary
        print("\n✅ Goalie rotation complete!")
        print(f"👮 Goalie      : {next_goalie.handle} (<@{next_goalie.user_id}>)")
        if next_deputy:
            print(f"🛡️ Deputy      : {next_deputy.handle} (<@{next_deputy.user_id}>)")
        else:
            print("🛡️ Deputy      : None")
        print(f"📢 Channels    : {', '.join(slack_channels)}")
        print(f"👥 User Group  : {user_group_id}")
        print("🎯 Slack user group updated, channel description refreshed, and message sent.")

    except SlackApiError as e:
        print("❌ Failed to update Slack state (user group, channel description, or goalie notification).")
        print(f"Error: {e.response['error']}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Notify Slack about the goalie.')
    parser.add_argument('--file-path', required=True, help='Path to the text file with users')
    parser.add_argument('--slack-token', required=True, help='Slack API token')
    parser.add_argument('--slack-channels', required=True, help='Space-separated list of Slack channels to notify')
    parser.add_argument('--user-group-handle', required=True, help='Slack user group handle')
    parser.add_argument('--mode', default='next_as_deputy', choices=['next_as_deputy', 'former_goalie_is_deputy', 'no_deputy', 'fixed_full'], help='Mode of deputy assignment')

    args = parser.parse_args()

    current_goalie, users = get_goalie_and_users(args.file_path, mode=args.mode)

    if not current_goalie:
        print("❌ No current goalie marked with '**' in the file.")
        sys.exit(1)

    # Step 2: Calculate the next goalie and deputy
    next_goalie, next_deputy = get_next_goalie_and_deputy(args.file_path, users, current_goalie, mode=args.mode)

    user_group_id = "get_user_group_id(args.slack_token, args.user_group_handle)"
    if not user_group_id:
        print(f"❌ Could not find Slack user group ID for handle: {args.user_group_handle}")
        sys.exit(1)

    # Step 4: Slack channels
    slack_channels = args.slack_channels.split()

    # Step 5: Notify and update
    notify_in_slack(
        slack_token=args.slack_token,
        slack_channels=slack_channels,
        next_goalie=next_goalie,
        next_deputy=next_deputy,
        user_group_id=user_group_id
    )

    update_goalie_file(file_path=args.file_path,
                       next_goalie=next_goalie,
                       deputy=next_deputy,
                       mode= args.mode
                       )


if __name__ == "__main__":
    main()
