import pytest
import sys
from goaliebot.core.models import Command
from goaliebot.rotation_entry import resolve_effective_commands, validate_required_inputs


# ✅ Tests for resolve_effective_commands

def test_resolve_effective_commands_returns_input_if_provided():
    commands = [Command.SEND_SLACK_MESSAGE]
    assert resolve_effective_commands(commands) == commands

def test_resolve_effective_commands_returns_all_if_none():
    commands = None
    result = resolve_effective_commands(commands)
    assert set(result) == set(Command)


# ✅ Tests for validate_required_inputs

def test_validate_required_inputs_passes_when_channels_and_user_group_provided():
    commands = [Command.SEND_SLACK_MESSAGE, Command.UPDATE_USER_GROUP]
    slack_channels = "C123"
    user_group_handle = "goaliebot"
    validate_required_inputs(commands, slack_channels, user_group_handle)  # should not exit


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
