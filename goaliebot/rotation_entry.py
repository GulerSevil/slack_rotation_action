import sys
import argparse

from goaliebot.rotation.file_ops import (
    get_goalie_and_users,
    get_next_goalie_and_deputy,
    update_goalie_file,
)
from goaliebot.notifier.notify import notify_in_slack
from goaliebot.slack_api.usergroup import get_user_group_id


def main():
    parser = argparse.ArgumentParser(description="Notify Slack about the goalie.")
    parser.add_argument(
        "--file-path", required=True, help="Path to the text file with users"
    )
    parser.add_argument("--slack-token", required=True, help="Slack API token")
    parser.add_argument(
        "--slack-channels",
        required=True,
        help="Space-separated list of Slack channels to notify",
    )
    parser.add_argument(
        "--user-group-handle", required=True, help="Slack user group handle"
    )
    parser.add_argument(
        "--mode",
        default="next_as_deputy",
        choices=[
            "next_as_deputy",
            "former_goalie_is_deputy",
            "no_deputy",
            "fixed_full",
        ],
        help="Mode of deputy assignment",
    )

    args = parser.parse_args()

    current_goalie, users = get_goalie_and_users(args.file_path, mode=args.mode)

    if not current_goalie:
        print("❌ No current goalie marked with '**' in the file.")
        sys.exit(1)

    next_goalie, next_deputy = get_next_goalie_and_deputy(
        args.file_path, users, current_goalie, mode=args.mode
    )

    print(f"Next goalie: {next_goalie.handle} ({next_goalie.user_id})")

    user_group_id = get_user_group_id(args.slack_token, args.user_group_handle)
    if not user_group_id:
        print(
            f"❌ Could not find Slack user group ID for handle: {args.user_group_handle}"
        )
        sys.exit(1)

    slack_channels = args.slack_channels.split()

    notify_in_slack(
        slack_token=args.slack_token,
        slack_channels=slack_channels,
        next_goalie=next_goalie,
        next_deputy=next_deputy,
        user_group_id=user_group_id,
    )

    update_goalie_file(
        file_path=args.file_path,
        next_goalie=next_goalie,
        deputy=next_deputy,
        mode=args.mode,
    )


if __name__ == "__main__":
    main()
