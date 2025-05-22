import pytest
import sys
from goaliebot.core.models import Command
from goaliebot.rotation_entry import validate_inputs


def test_validate_slack_channels_passes_with_required_channels(monkeypatch):
    commands = [Command.SEND_SLACK_MESSAGE]
    slack_channels = "C123 C456"
    # Should not raise or exit
    validate_inputs(commands, slack_channels)


def test_validate_slack_channels_passes_when_no_commands():
    # If no commands are passed, it should pass regardless of slack_channels
    validate_inputs([], None)


def test_validate_slack_channels_exits_if_channels_missing(monkeypatch):
    commands = [Command.UPDATE_TOPIC_DESCRIPTION]
    with pytest.raises(SystemExit) as exit_info:
        validate_inputs(commands, None)
    assert exit_info.type == SystemExit
    assert exit_info.value.code == 1
