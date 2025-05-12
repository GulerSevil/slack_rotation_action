import tempfile
import os
import pytest

from goalie.utils.file_ops import get_goalie_and_users, get_next_goalie_and_deputy, \
    update_goalie_file
from goalie.utils.types import SlackUser



def write_temp_file(content: str):
    tmp = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    tmp.write(content.strip() + '\n')
    tmp.flush()
    return tmp.name

def read_file_lines(path):
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]


def test_next_as_deputy_rotation_and_update():
    content = """
alice, U111
bob **, U222
charlie, U333
"""
    file_path = write_temp_file(content)
    current_goalie, users = get_goalie_and_users(file_path, mode='next_as_deputy')
    assert current_goalie == SlackUser("bob", "U222")

    next_goalie, next_deputy = get_next_goalie_and_deputy(file_path, users, current_goalie, mode='next_as_deputy')
    assert next_goalie == SlackUser("charlie", "U333")
    assert next_deputy == SlackUser("alice", "U111")

    update_goalie_file(file_path, next_goalie, next_deputy, mode='next_as_deputy')
    updated = read_file_lines(file_path)
    assert "charlie **, U333" in updated
    assert all("**" not in line or "charlie" in line for line in updated)

    os.remove(file_path)


def test_fixed_full_rotation_and_update():
    content = """
alice **, U111 | bob, U222
charlie, U333 | diana, U444
"""
    file_path = write_temp_file(content)
    current_goalie, users = get_goalie_and_users(file_path, mode='fixed_full')
    assert current_goalie == SlackUser("alice", "U111")

    next_goalie, next_deputy = get_next_goalie_and_deputy(file_path, users, current_goalie, mode='fixed_full')
    assert next_goalie == SlackUser("charlie", "U333")
    assert next_deputy == SlackUser("diana", "U444")

    update_goalie_file(file_path, next_goalie, next_deputy, mode='fixed_full')
    updated = read_file_lines(file_path)
    assert "charlie **, U333 | diana, U444" in updated
    assert all("**" not in line or "charlie" in line for line in updated)

    os.remove(file_path)


def test_former_goalie_is_deputy():
    users = [
        SlackUser("alice", "U111"),
        SlackUser("bob", "U222"),
        SlackUser("charlie", "U333")
    ]
    current_goalie = SlackUser("bob", "U222")
    next_goalie, deputy = get_next_goalie_and_deputy("ignored.txt", users, current_goalie, mode='former_goalie_is_deputy')
    assert next_goalie == SlackUser("charlie", "U333")
    assert deputy == SlackUser("bob", "U222")


def test_no_deputy():
    users = [
        SlackUser("alice", "U111"),
        SlackUser("bob", "U222"),
        SlackUser("charlie", "U333")
    ]
    current_goalie = SlackUser("charlie", "U333")
    next_goalie, deputy = get_next_goalie_and_deputy("ignored.txt", users, current_goalie, mode='no_deputy')
    assert next_goalie == SlackUser("alice", "U111")
    assert deputy is None
