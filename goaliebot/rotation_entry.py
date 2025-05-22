import sys
import argparse
from goaliebot.core.parser import parse_commands
from goaliebot.core.models import Command

from goaliebot.core.file_ops import (
    get_goalie_and_users,
    get_next_goalie_and_deputy,
    update_goalie_file,
)
from goaliebot.slack_orchestrator.command_runner import run_slack_commands
from goaliebot.slack_api.usergroup import get_user_group_id


def parse_args():
    parser = argparse.ArgumentParser(description="Notify Slack about the goalie.")
    parser.add_argument(
        "--file-path", required=True, help="Path to the text file with users"
    )
    parser.add_argument("--slack-token", required=True, help="Slack API token")
    parser.add_argument(
        "--slack-channels",
        required=False,
        help="Space-separated list of Slack channels to notify (required if using channel-based commands)",
    )
    parser.add_argument(
        "--user-group-handle",
        required=False,
        help="Slack user group handle to update (required if using update_user_group command)",
    )

    parser.add_argument(
        "--commands",
        required=False,
        type=parse_commands,
        help=(
            "Pipe-separated list of commands to run. "
            "If not set, all optional Slack commands will be executed."
        ),
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
    return parser.parse_args()


def validate_inputs(commands, slack_channels, user_group_handle):
    # Validate slack_channels if any relevant command is used
    requires_channels = {Command.SEND_SLACK_MESSAGE, Command.UPDATE_TOPIC_DESCRIPTION}
    if any(cmd in commands for cmd in requires_channels):
        if not slack_channels:
            print(
                "❌ '--slack-channels' must be set if using 'send_slack_message' or 'update_topic_description' commands."
            )
            sys.exit(1)

    # Validate user_group_handle if user group update is included
    if Command.UPDATE_USER_GROUP in commands:
        if not user_group_handle:
            print(
                "❌ '--user-group-handle' must be set if using 'update_user_group' command."
            )
            sys.exit(1)


def resolve_goalie_rotation(file_path, mode):
    current_goalie, users = get_goalie_and_users(file_path, mode=mode)
    if not current_goalie:
        print("❌ No current goalie marked with '**' in the file.")
        sys.exit(1)
    next_goalie, next_deputy = get_next_goalie_and_deputy(
        file_path, users, current_goalie, mode=mode
    )
    return next_goalie, next_deputy


def resolve_user_group_id(slack_token, handle):
    user_group_id = get_user_group_id(slack_token, handle)
    if not user_group_id:
        print(f"❌ Could not find Slack user group ID for handle: {handle}")
        sys.exit(1)
    return user_group_id


def main():
    args = parse_args()

    validate_inputs(args.commands, args.slack_channels, args.user_group_handle)

    next_goalie, next_deputy = resolve_goalie_rotation(args.file_path, args.mode)
    print(f"✅ Next goalie: {next_goalie.handle} ({next_goalie.user_id})")

    user_group_id = resolve_user_group_id(args.slack_token, args.user_group_handle)

    slack_channels = args.slack_channels.split() if args.slack_channels else []

    commands = args.commands or list(Command)  # Default to all commands

    run_slack_commands(
        slack_token=args.slack_token,
        slack_channels=slack_channels,
        next_goalie=next_goalie,
        next_deputy=next_deputy,
        user_group_id=user_group_id,
        commands=commands,
    )

    update_goalie_file(
        file_path=args.file_path,
        next_goalie=next_goalie,
        deputy=next_deputy,
        mode=args.mode,
    )


if __name__ == "__main__":
    main()
