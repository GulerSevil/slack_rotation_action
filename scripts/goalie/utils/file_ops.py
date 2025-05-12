from goalie.utils.types import SlackUser


def parse_goalie_line(line):
    """Parse a goalie line and return a SlackUser. Strips '**' if present."""
    handle, user_id = map(str.strip, line.replace('**', '').split(','))
    return SlackUser(handle, user_id)


def parse_fixed_full_line(line):
    """Parse a fixed_full line and return (goalie, deputy), with goalie possibly marked with **."""
    goalie_part, deputy_part = map(str.strip, line.split('|'))
    goalie_handle, goalie_id = map(str.strip, goalie_part.replace('**', '').split(','))
    deputy_handle, deputy_id = map(str.strip, deputy_part.split(','))
    goalie = SlackUser(goalie_handle, goalie_id)
    deputy = SlackUser(deputy_handle, deputy_id)
    is_current_goalie = '**' in goalie_part
    return goalie, deputy, is_current_goalie


def get_goalie_and_users(file_path, mode='next_as_deputy'):
    """Return current goalie and full list of users from file."""
    users = []
    current_goalie = None

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue

            if mode == 'fixed_full':
                goalie, _, is_current_goalie = parse_fixed_full_line(line)
                if is_current_goalie:
                    current_goalie = goalie
                users.append(goalie)
            else:
                user = parse_goalie_line(line)
                if '**' in line:
                    current_goalie = user
                users.append(user)

    return current_goalie, users


def get_next_goalie_and_deputy(file_path, users, current_goalie, mode='next_as_deputy'):
    """Rotate to next goalie and determine deputy based on mode."""
    all_handles = [user.handle for user in users]
    current_index = all_handles.index(current_goalie.handle)
    next_index = (current_index + 1) % len(users)
    next_goalie = users[next_index]

    if mode == 'no_deputy':
        return next_goalie, None
    elif mode == 'former_goalie_is_deputy':
        return next_goalie, current_goalie
    elif mode == 'next_as_deputy':
        deputy_index = (next_index + 1) % len(users)
        return next_goalie, users[deputy_index]
    elif mode == 'fixed_full':
        # Re-parse the file to find the deputy line for the new goalie
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                if line.startswith(next_goalie.handle):
                    _, deputy, _ = parse_fixed_full_line(line)
                    return next_goalie, deputy
        return next_goalie, None
    else:
        raise ValueError(f"Unknown mode: {mode}")


def update_goalie_file(file_path, next_goalie, deputy=None, mode='next_as_deputy'):
    """Update the goalie file to mark the new goalie (and deputy in fixed_full mode)."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        updated_lines = []

        for line in lines:
            original = line.strip()
            if not original:  # Skip only blank lines
                updated_lines.append(original)
                continue

            if mode == 'fixed_full':
                # Clean old ** and update if it's the new goalie
                parts = [part.strip() for part in original.split('|')]
                goalie_handle, goalie_id = map(str.strip, parts[0].replace('**', '').split(','))
                deputy_part = parts[1].strip() if len(parts) > 1 else ""

                if goalie_handle == next_goalie.handle:
                    goalie_part = f"{goalie_handle} **, {goalie_id}"
                    deputy_part = f"{deputy.handle}, {deputy.user_id}" if deputy else deputy_part
                else:
                    goalie_part = f"{goalie_handle}, {goalie_id}"

                updated_line = f"{goalie_part} | {deputy_part}"

            else:
                # Non-fixed mode: clean old ** and set new goalie
                handle, user_id = map(str.strip, original.replace('**', '').split(','))
                if handle == next_goalie.handle:
                    updated_line = f"{handle} **, {user_id}"
                else:
                    updated_line = f"{handle}, {user_id}"

            updated_lines.append(updated_line)

        with open(file_path, 'w') as f:
            f.writelines(f"{line}\n" for line in updated_lines)

        print(f"✅ Goalie file updated: Goalie = {next_goalie.handle}, Deputy = {deputy.handle if deputy else 'None'}")

    except Exception as e:
        print(f"❌ Error updating goalie file: {e}")
