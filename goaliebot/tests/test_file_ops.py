import pytest
from unittest.mock import patch
from goaliebot.core.file_ops import (
    get_goalie_and_users,
    get_next_goalie_and_deputy,
    update_goalie_file,
)

# Sample data
GOALIE_LINES = """
# Comment line
alice**, U12345
bob, U23456
carol, U34567
"""

FIXED_FULL_LINES = """
alice **, U12345 | bob, U23456
carol, U34567 | dave, U45678
alice, U12345 | sss, U23456
"""


@pytest.fixture
def create_file(tmp_path):
    def _create(content):
        f = tmp_path / "goalie.txt"
        f.write_text(content.strip())
        return str(f)

    return _create


@patch("goaliebot.core.file_ops.parse_goalie_line")
def test_get_goalie_and_users_next_as_deputy(mock_parse_goalie_line, create_file):
    class User:
        def __init__(self, handle, user_id):
            self.handle = handle
            self.user_id = user_id

    def side_effect(line):
        handle = line.replace("**", "").split(",")[0].strip()
        user_id = "U" + handle.upper()
        return User(handle, user_id)

    mock_parse_goalie_line.side_effect = side_effect

    file_path = create_file(GOALIE_LINES)

    current_goalie, users = get_goalie_and_users(file_path, mode="next_as_deputy")

    assert current_goalie.handle == "alice"
    assert len(users) == 3
    assert users[1].handle == "bob"


def test_get_next_goalie_and_deputy_modes(create_file):
    class User:
        def __init__(self, handle, user_id):
            self.handle = handle
            self.user_id = user_id

    users = [User("alice", "U1"), User("bob", "U2"), User("carol", "U3")]
    current_goalie = users[0]

    file_path = create_file(GOALIE_LINES)

    # next_as_deputy mode
    next_goalie, deputy = get_next_goalie_and_deputy(
        file_path, users, current_goalie, mode="next_as_deputy"
    )
    assert next_goalie.handle == "bob"
    assert deputy.handle == "carol"

    # no_deputy mode
    next_goalie, deputy = get_next_goalie_and_deputy(
        file_path, users, current_goalie, mode="no_deputy"
    )
    assert next_goalie.handle == "bob"
    assert deputy is None

    # former_goalie_is_deputy mode
    next_goalie, deputy = get_next_goalie_and_deputy(
        file_path, users, current_goalie, mode="former_goalie_is_deputy"
    )
    assert next_goalie.handle == "bob"
    assert deputy.handle == "alice"


@patch("goaliebot.core.file_ops.parse_fixed_full_line")
def test_get_next_goalie_and_deputy_fixed_full(mock_parse_fixed_full_line, create_file):
    class User:
        def __init__(self, handle, user_id):
            self.handle = handle
            self.user_id = user_id

    file_path = create_file(FIXED_FULL_LINES)
    users = [User("alice", "U12345"), User("carol", "U34567")]
    current_goalie = users[0]

    def side_effect(line):
        if line.startswith("carol"):
            return (User("carol", "U34567"), User("dave", "U45678"), False)
        return (User("alice", "U12345"), User("bob", "U23456"), True)

    mock_parse_fixed_full_line.side_effect = side_effect

    next_goalie, deputy = get_next_goalie_and_deputy(
        file_path, users, current_goalie, mode="fixed_full"
    )

    assert next_goalie.handle == "carol"
    assert deputy.handle == "dave"


def test_update_goalie_file(create_file):
    class User:
        def __init__(self, handle, user_id):
            self.handle = handle
            self.user_id = user_id

    initial_content = """
alice, U1
bob, U2
carol, U3
    """
    file_path = create_file(initial_content)

    next_goalie = User("bob", "U2")
    deputy = User("carol", "U3")

    update_goalie_file(file_path, next_goalie, deputy, mode="next_as_deputy")

    updated_lines = open(file_path).read().strip().splitlines()
    # bob should be marked with **
    assert any("bob **" in line for line in updated_lines)
    # others should not have **
    assert all(
        ("alice **" not in line and "carol **" not in line) for line in updated_lines
    )

def test_update_goalie_file_fixed_full_duplicate_names(create_file):
    class User:
        def __init__(self, handle, user_id):
            self.handle = handle
            self.user_id = user_id

    duplicate_content = """
alice, U1 | bob, U2
carol, U3 | dave, U4
carol, U3 | frank, U6
    """
    file_path = create_file(duplicate_content)

    next_goalie = User("carol", "U3")
    deputy = User("dave", "U4")

    update_goalie_file(file_path, next_goalie, deputy, mode="fixed_full")

    updated_lines = open(file_path).read().strip().splitlines()

    # Only one line should have "carol **"
    goalie_marked_lines = [line for line in updated_lines if "carol **" in line]
    assert len(goalie_marked_lines) == 1
    assert "dave" in goalie_marked_lines[0]
    # The second "carol" should not be marked
    other_lines = [line for line in updated_lines if "carol **" not in line]
    assert all("carol **" not in line for line in other_lines)
