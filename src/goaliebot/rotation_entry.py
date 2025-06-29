import sys
import click
from goaliebot.core.parser import parse_commands
from goaliebot.core.models import Command
from goaliebot.core.models import Cadence

from goaliebot.core.file_ops import (
    get_goalie_and_users,
    get_next_goalie_and_deputy,
    update_goalie_file,
)
from goaliebot.operations.command_runner import run_slack_commands
from goaliebot.slack_api.usergroup import get_user_group_id


def validate_commands(ctx, param, value):
    """Click callback to parse commands."""
    if value is None:
        return None
    return parse_commands(value)


def validate_cadence(ctx, param, value):
    """Click callback to convert string to Cadence enum."""
    if isinstance(value, Cadence):
        return value
    return Cadence(value)


def resolve_effective_commands(commands):
    return commands or list(Command)


def validate_required_inputs(effective_commands, slack_channels, user_group_handle):
    requires_channels = {Command.SEND_SLACK_MESSAGE, Command.UPDATE_TOPIC_DESCRIPTION}
    if any(cmd in effective_commands for cmd in requires_channels):
        if not slack_channels:
            print(
                "❌ '--slack-channels' must be set if using 'send_slack_message' or 'update_topic_description' commands."
            )
            sys.exit(1)

    if Command.UPDATE_USER_GROUP in effective_commands:
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


@click.command()
@click.option(
    "--file-path",
    required=True,
    help="Path to the text file with users",
)
@click.option(
    "--slack-token",
    required=True,
    help="Slack API token",
)
@click.option(
    "--slack-channels",
    help="Space-separated list of Slack channels to notify (required if using channel-based commands)",
)
@click.option(
    "--user-group-handle",
    help="Slack user group handle to update (required if using update_user_group command)",
)
@click.option(
    "--commands",
    callback=validate_commands,
    help="Pipe-separated list of commands to run. If not set, all optional Slack commands will be executed.",
)
@click.option(
    "--mode",
    default="next_as_deputy",
    type=click.Choice(
        [
            "next_as_deputy",
            "former_goalie_is_deputy",
            "no_deputy",
            "fixed_full",
        ]
    ),
    help="Mode of deputy assignment",
)
@click.option(
    "--cadence",
    default="week",
    type=click.Choice([c.value for c in Cadence]),
    callback=validate_cadence,
    help="Cadence of rotation: day, week, month (default: week)",
)
def main(
    file_path, slack_token, slack_channels, user_group_handle, commands, mode, cadence
):
    """Notify Slack about the goalie rotation."""
    effective_commands = resolve_effective_commands(commands)
    validate_required_inputs(effective_commands, slack_channels, user_group_handle)

    next_goalie, next_deputy = resolve_goalie_rotation(file_path, mode)
    print(f"✅ Next goalie: {next_goalie.handle} ({next_goalie.user_id})")

    user_group_id = resolve_user_group_id(slack_token, user_group_handle)

    slack_channels_list = slack_channels.split() if slack_channels else []

    run_slack_commands(
        slack_token=slack_token,
        slack_channels=slack_channels_list,
        next_goalie=next_goalie,
        next_deputy=next_deputy,
        user_group_id=user_group_id,
        commands=effective_commands,
        cadence=cadence,
    )

    update_goalie_file(
        file_path=file_path,
        next_goalie=next_goalie,
        deputy=next_deputy,
        mode=mode,
    )


if __name__ == "__main__":
    main()
