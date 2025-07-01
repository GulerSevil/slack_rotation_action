import pytest
from click.testing import CliRunner
from goaliebot.core.models import Command
from goaliebot.rotation_entry import (
    resolve_effective_commands,
    validate_required_inputs,
    main,
    validate_commands,
    validate_cadence,
)


def test_resolve_effective_commands_returns_input_if_provided():
    commands = [Command.SEND_SLACK_MESSAGE]
    assert resolve_effective_commands(commands) == commands


def test_resolve_effective_commands_returns_all_if_none():
    commands = None
    result = resolve_effective_commands(commands)
    assert set(result) == set(Command)


def test_validate_required_inputs_passes_when_channels_and_user_group_provided():
    commands = [Command.SEND_SLACK_MESSAGE, Command.UPDATE_USER_GROUP]
    slack_channels = "C123"
    user_group_handle = "goaliebot"
    validate_required_inputs(
        commands, slack_channels, user_group_handle
    )  # should not exit


def test_validate_required_inputs_fails_if_channels_missing():
    commands = [Command.SEND_SLACK_MESSAGE]
    slack_channels = None
    user_group_handle = None
    with pytest.raises(SystemExit) as e:
        validate_required_inputs(commands, slack_channels, user_group_handle)
    assert e.type == SystemExit
    assert e.value.code == 1


def test_validate_required_inputs_fails_if_user_group_handle_missing():
    commands = [Command.UPDATE_USER_GROUP]
    slack_channels = "C123"
    user_group_handle = None
    with pytest.raises(SystemExit) as e:
        validate_required_inputs(commands, slack_channels, user_group_handle)
    assert e.type == SystemExit
    assert e.value.code == 1


def test_validate_required_inputs_passes_if_no_channels_required():
    commands = [Command.UPDATE_USER_GROUP]
    slack_channels = None  # no channels needed
    user_group_handle = "goaliebot"
    validate_required_inputs(commands, slack_channels, user_group_handle)


def test_validate_required_inputs_fails_if_all_commands_but_inputs_missing():
    commands = list(Command)
    slack_channels = None
    user_group_handle = None
    with pytest.raises(SystemExit) as e:
        validate_required_inputs(commands, slack_channels, user_group_handle)
    assert e.type == SystemExit
    assert e.value.code == 1


def test_validate_commands_callback_with_none():
    result = validate_commands(None, None, None)
    assert result is None


def test_validate_commands_callback_with_value():
    result = validate_commands(None, None, "send_slack_message|update_user_group")
    assert Command.SEND_SLACK_MESSAGE in result
    assert Command.UPDATE_USER_GROUP in result


def test_validate_cadence_callback():
    from goaliebot.core.models import Cadence

    # Test with string value
    result = validate_cadence(None, None, "week")
    assert result == Cadence.WEEK

    # Test with Cadence enum (already converted)
    result = validate_cadence(None, None, Cadence.MONTH)
    assert result == Cadence.MONTH


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Notify Slack about the goalie rotation" in result.output
    assert "--file-path" in result.output
    assert "--slack-token" in result.output


def test_cli_missing_required_args():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code != 0
    assert "Missing option" in result.output


def test_cli_invalid_mode():
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--file-path", "test.txt", "--slack-token", "token", "--mode", "invalid_mode"],
    )
    assert result.exit_code != 0
    assert "Invalid value for '--mode'" in result.output


def test_cli_invalid_cadence():
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--file-path",
            "test.txt",
            "--slack-token",
            "token",
            "--cadence",
            "invalid_cadence",
        ],
    )
    assert result.exit_code != 0
    assert "Invalid value for '--cadence'" in result.output
