import pytest
import tempfile
import os
from goaliebot.core.file_ops import (
    get_goalie_and_users,
    get_next_goalie_and_deputy,
    update_goalie_file,
    _find_current_goalie_index,
    _find_target_line_index,
    _line_matches_goalie,
)
from goaliebot.core.models import SlackUser


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    fd, path = tempfile.mkstemp(suffix=".txt")
    yield path
    os.close(fd)
    os.unlink(path)


def create_test_file(content, file_path):
    """Helper to create test file with content."""
    with open(file_path, "w") as f:
        f.write(content)


class TestGetGoalieAndUsers:
    """Test get_goalie_and_users function."""

    def test_simple_rotation_with_current_goalie(self, temp_file):
        """Test basic rotation file parsing."""
        content = """Alice, U123
Bob **, U456
Charlie, U789"""
        create_test_file(content, temp_file)

        current_goalie, users, current_index = get_goalie_and_users(temp_file)

        assert current_goalie.handle == "Bob"
        assert current_goalie.user_id == "U456"
        assert current_index == 1
        assert len(users) == 3
        assert users[0].handle == "Alice"
        assert users[1].handle == "Bob"
        assert users[2].handle == "Charlie"

    def test_duplicate_names_bug_scenario(self, temp_file):
        """Test the specific bug scenario reported - duplicate names with correct selection."""
        content = """User A, ID001 | User B, ID002
User C, ID003 | User A, ID001
User D, ID004 | User C, ID003
User E, ID005 | User D, ID004
User B, ID002 | User E, ID005
User A **, ID001 | User B, ID002
User F, ID006 | User A, ID001
User B, ID002 | User F, ID006
User E, ID005 | User B, ID002
User C, ID003 | User A, ID001
User F, ID006 | User C, ID003"""
        create_test_file(content, temp_file)

        current_goalie, users, current_index = get_goalie_and_users(
            temp_file, mode="fixed_full"
        )

        # Should find the User A marked with **, not the first one
        assert current_goalie.handle == "User A"
        assert current_goalie.user_id == "ID001"
        assert current_index == 5  # 6th entry (0-indexed)
        assert len(users) == 11

        # Verify the sequence is correct
        assert users[0].handle == "User A"  # First occurrence
        assert users[5].handle == "User A"  # Marked occurrence (current)
        assert users[6].handle == "User F"  # Should be next

    def test_no_current_goalie_marked(self, temp_file):
        """Test when no goalie is marked with **."""
        content = """Alice, U123
Bob, U456
Charlie, U789"""
        create_test_file(content, temp_file)

        current_goalie, users, current_index = get_goalie_and_users(temp_file)

        assert current_goalie is None
        assert current_index == -1
        assert len(users) == 3

    def test_fixed_full_mode_parsing(self, temp_file):
        """Test fixed_full mode parsing with goalie|deputy format."""
        content = """Alice, U123 | Bob, U456
Bob **, U456 | Charlie, U789
Charlie, U789 | Alice, U123"""
        create_test_file(content, temp_file)

        current_goalie, users, current_index = get_goalie_and_users(
            temp_file, mode="fixed_full"
        )

        assert current_goalie.handle == "Bob"
        assert current_goalie.user_id == "U456"
        assert current_index == 1
        assert len(users) == 3

    def test_comments_and_empty_lines_ignored(self, temp_file):
        """Test that comments and empty lines are properly ignored."""
        content = """# This is a comment
Alice, U123

# Another comment
Bob **, U456

Charlie, U789
# Final comment"""
        create_test_file(content, temp_file)

        current_goalie, users, current_index = get_goalie_and_users(temp_file)

        assert current_goalie.handle == "Bob"
        assert current_index == 1
        assert len(users) == 3


class TestGetNextGoalieAndDeputy:
    """Test get_next_goalie_and_deputy function."""

    def test_next_as_deputy_mode(self, temp_file):
        """Test next_as_deputy mode rotation."""
        content = """Alice, U123
Bob **, U456
Charlie, U789
David, U000"""
        create_test_file(content, temp_file)

        current_goalie, users, current_index = get_goalie_and_users(temp_file)
        next_goalie, next_deputy = get_next_goalie_and_deputy(
            temp_file, users, current_goalie, current_index, mode="next_as_deputy"
        )

        assert next_goalie.handle == "Charlie"
        assert next_deputy.handle == "David"

    def test_duplicate_names_correct_next_selection(self, temp_file):
        """Test the bug fix - correct next selection with duplicate names."""
        content = """User A, ID001 | User B, ID002
User C, ID003 | User A, ID001
User D, ID004 | User C, ID003
User E, ID005 | User D, ID004
User B, ID002 | User E, ID005
User A **, ID001 | User B, ID002
User F, ID006 | User A, ID001
User B, ID002 | User F, ID006
User E, ID005 | User B, ID002
User C, ID003 | User A, ID001
User F, ID006 | User C, ID003"""
        create_test_file(content, temp_file)

        current_goalie, users, current_index = get_goalie_and_users(
            temp_file, mode="fixed_full"
        )
        next_goalie, next_deputy = get_next_goalie_and_deputy(
            temp_file, users, current_goalie, current_index, mode="fixed_full"
        )

        # Should select User F (index 6), NOT User C (index 1)
        assert next_goalie.handle == "User F"
        assert next_goalie.user_id == "ID006"
        assert next_deputy.handle == "User A"
        assert next_deputy.user_id == "ID001"

    def test_wrap_around_to_beginning(self, temp_file):
        """Test rotation wraps around to beginning when at end."""
        content = """Alice, U123
Bob, U456
Charlie **, U789"""
        create_test_file(content, temp_file)

        current_goalie, users, current_index = get_goalie_and_users(temp_file)
        next_goalie, next_deputy = get_next_goalie_and_deputy(
            temp_file, users, current_goalie, current_index, mode="next_as_deputy"
        )

        assert next_goalie.handle == "Alice"
        assert next_deputy.handle == "Bob"

    def test_former_goalie_is_deputy_mode(self, temp_file):
        """Test former_goalie_is_deputy mode."""
        content = """Alice, U123
Bob **, U456
Charlie, U789"""
        create_test_file(content, temp_file)

        current_goalie, users, current_index = get_goalie_and_users(temp_file)
        next_goalie, next_deputy = get_next_goalie_and_deputy(
            temp_file,
            users,
            current_goalie,
            current_index,
            mode="former_goalie_is_deputy",
        )

        assert next_goalie.handle == "Charlie"
        assert next_deputy.handle == "Bob"  # Former goalie becomes deputy
        assert next_deputy.user_id == "U456"

    def test_no_deputy_mode(self, temp_file):
        """Test no_deputy mode."""
        content = """Alice, U123
Bob **, U456
Charlie, U789"""
        create_test_file(content, temp_file)

        current_goalie, users, current_index = get_goalie_and_users(temp_file)
        next_goalie, next_deputy = get_next_goalie_and_deputy(
            temp_file, users, current_goalie, current_index, mode="no_deputy"
        )

        assert next_goalie.handle == "Charlie"
        assert next_deputy is None

    def test_single_user_rotation(self, temp_file):
        """Test rotation with only one user."""
        content = """Alice **, U123"""
        create_test_file(content, temp_file)

        current_goalie, users, current_index = get_goalie_and_users(temp_file)
        next_goalie, next_deputy = get_next_goalie_and_deputy(
            temp_file, users, current_goalie, current_index, mode="next_as_deputy"
        )

        assert next_goalie.handle == "Alice"  # Wraps to self
        assert next_deputy.handle == "Alice"  # Deputy is also self

    def test_invalid_current_goalie_index(self, temp_file):
        """Test error handling for invalid current goalie index."""
        content = """Alice, U123
Bob, U456"""
        create_test_file(content, temp_file)

        current_goalie, users, current_index = get_goalie_and_users(temp_file)

        with pytest.raises(ValueError, match="Current goalie index not found"):
            get_next_goalie_and_deputy(
                temp_file, users, current_goalie, -1, mode="next_as_deputy"
            )

    def test_unknown_mode(self, temp_file):
        """Test error handling for unknown mode."""
        content = """Alice, U123
Bob **, U456"""
        create_test_file(content, temp_file)

        current_goalie, users, current_index = get_goalie_and_users(temp_file)

        with pytest.raises(ValueError, match="Unknown mode"):
            get_next_goalie_and_deputy(
                temp_file, users, current_goalie, current_index, mode="invalid_mode"
            )

    def test_duplicate_names_index_bug_fix(self, temp_file):
        """
        Test for the bug where duplicate names caused wrong next selection.
        When User1 ** is current (position 5), next should be User6 (position 6), NOT User2 (position 1).
        """
        # Rotation data with duplicate names to reproduce the bug scenario
        content = """User1, ID001 | User2, ID002
User2, ID002 | User3, ID003
User3, ID003 | User4, ID004
User4, ID004 | User5, ID005
User5, ID005 | User1, ID001
User1 **, ID001 | User2, ID002
User6, ID006 | User1, ID001
User2, ID002 | User6, ID006
User4, ID004 | User2, ID002
User3, ID003 | User1, ID001
User6, ID006 | User3, ID003"""
        create_test_file(content, temp_file)

        # Parse the current state
        current_goalie, users, current_index = get_goalie_and_users(
            temp_file, mode="fixed_full"
        )

        # Verify we found the correct current goalie (the one with **)
        assert current_goalie.handle == "User1"
        assert current_index == 5  # Should be the 6th entry (0-indexed)

        # Get the next goalie
        next_goalie, next_deputy = get_next_goalie_and_deputy(
            temp_file, users, current_goalie, current_index, mode="fixed_full"
        )

        # CRITICAL TEST: Should be User6, NOT User2
        assert next_goalie.handle == "User6"
        assert next_goalie.user_id == "ID006"

        # Verify the bug is fixed: should NOT select User2 (who appears earlier in the list)
        assert next_goalie.handle != "User2"

        # Additional verification: ensure we're getting position 6 (User6), not position 1 (User2)
        assert users[current_index + 1].handle == "User6"  # Position after current


class TestHelperFunctions:
    """Test helper functions."""

    def test_find_current_goalie_index(self):
        """Test _find_current_goalie_index function."""
        lines = ["Alice, U123", "Bob **, U456", "Charlie, U789"]
        assert _find_current_goalie_index(lines) == 1

        lines_no_current = ["Alice, U123", "Bob, U456", "Charlie, U789"]
        assert _find_current_goalie_index(lines_no_current) == -1

    def test_line_matches_goalie(self):
        """Test _line_matches_goalie function."""
        assert _line_matches_goalie("Bob, U456", "Bob")
        assert _line_matches_goalie("Bob **, U456", "Bob")
        assert _line_matches_goalie("Bob, U456 | Alice, U123", "Bob")
        assert not _line_matches_goalie("Alice, U123", "Bob")
        assert not _line_matches_goalie("# Comment", "Bob")
        assert not _line_matches_goalie("", "Bob")

    def test_find_target_line_index(self):
        """Test _find_target_line_index function."""
        lines = ["User A, ID001", "User B, ID002", "User A **, ID001", "User C, ID003"]

        current_index = 2  # User A ** is at index 2
        target_index = _find_target_line_index(lines, current_index, "User C")
        assert target_index == 3

        # Test wrap around
        target_index = _find_target_line_index(lines, 3, "User A")
        assert target_index == 0  # Should find first User A


class TestUpdateGoalieFile:
    """Test update_goalie_file function."""

    def test_update_goalie_file_standard_mode(self, temp_file):
        """Test updating goalie file in standard mode."""
        content = """Alice, U123
Bob **, U456
Charlie, U789"""
        create_test_file(content, temp_file)

        new_goalie = SlackUser("Charlie", "U789")
        new_deputy = SlackUser("Alice", "U123")

        update_goalie_file(temp_file, new_goalie, new_deputy, mode="next_as_deputy")

        # Read updated file
        with open(temp_file, "r") as f:
            updated_content = f.read()

        assert "Bob, U456" in updated_content  # ** removed from Bob
        assert "Charlie **, U789" in updated_content  # ** added to Charlie
        assert "Alice, U123" in updated_content

    def test_update_goalie_file_fixed_full_mode(self, temp_file):
        """Test updating goalie file in fixed_full mode."""
        content = """Alice, U123 | Bob, U456
Bob **, U456 | Charlie, U789
Charlie, U789 | Alice, U123"""
        create_test_file(content, temp_file)

        new_goalie = SlackUser("Charlie", "U789")
        new_deputy = SlackUser("Alice", "U123")

        update_goalie_file(temp_file, new_goalie, new_deputy, mode="fixed_full")

        # Read updated file
        with open(temp_file, "r") as f:
            updated_content = f.read()

        assert "Bob, U456 | Charlie, U789" in updated_content  # ** removed from Bob
        assert (
            "Charlie **, U789 | Alice, U123" in updated_content
        )  # ** added to Charlie
