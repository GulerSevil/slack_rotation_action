from .parser import parse_goalie_line, parse_fixed_full_line


def get_goalie_and_users(file_path, mode="next_as_deputy"):
    current_goalie = None
    users = []

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line:
                continue

            if mode == "fixed_full":
                goalie, _, is_current_goalie = parse_fixed_full_line(line)
                if is_current_goalie:
                    current_goalie = goalie
                users.append(goalie)
            else:
                user = parse_goalie_line(line)
                if "**" in line:
                    current_goalie = user
                users.append(user)

    return current_goalie, users


def get_next_goalie_and_deputy(file_path, users, current_goalie, mode="next_as_deputy"):
    """Rotate to next goalie and determine deputy based on mode."""
    all_handles = [user.handle for user in users]
    current_index = all_handles.index(current_goalie.handle)
    next_index = (current_index + 1) % len(users)
    next_goalie = users[next_index]

    if mode == "no_deputy":
        return next_goalie, None
    elif mode == "former_goalie_is_deputy":
        return next_goalie, current_goalie
    elif mode == "next_as_deputy":
        deputy_index = (next_index + 1) % len(users)
        return next_goalie, users[deputy_index]
    elif mode == "fixed_full":
        # Re-parse the file to find the deputy line for the new goalie
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if line.startswith(next_goalie.handle):
                    _, deputy, _ = parse_fixed_full_line(line)
                    return next_goalie, deputy
        return next_goalie, None
    else:
        raise ValueError(f"Unknown mode: {mode}")


def _find_current_goalie_index(lines):
    """Find the index of the line containing the current goalie (marked with **)."""
    for i, line in enumerate(lines):
        if "**" in line.strip():
            return i
    return -1


def _find_target_line_index(lines, current_goalie_index, next_goalie_handle):
    """Find the index of the next line to mark with ** for the next goalie."""
    if current_goalie_index < 0:
        return -1

    # Search after current goalie first
    for i in range(current_goalie_index + 1, len(lines)):
        if _line_matches_goalie(lines[i], next_goalie_handle):
            return i

    # If not found, wrap around to beginning
    for i in range(0, current_goalie_index):
        if _line_matches_goalie(lines[i], next_goalie_handle):
            return i

    return -1


def _line_matches_goalie(line, goalie_handle):
    """Check if a line matches the given goalie handle."""
    line = line.strip()
    if not line or line.startswith("#"):
        return False

    parts = [p.strip() for p in line.split("|")]
    if len(parts) == 0:
        return False

    goalie_info = parts[0].replace("**", "").strip()
    if not goalie_info:
        return False

    current_handle = goalie_info.split(",")[0].strip()
    return current_handle == goalie_handle


def _process_fixed_full_line(line, line_index, target_line_index, next_goalie, deputy, goalie_marked):
    """Process a single line for fixed_full mode."""
    parts = [p.strip() for p in line.split("|")]
    goalie_info = parts[0].replace("**", "").strip()
    deputy_info = parts[1].strip() if len(parts) > 1 else ""

    goalie_handle, goalie_id = map(str.strip, goalie_info.split(","))

    should_mark = (line_index == target_line_index and not goalie_marked)

    if should_mark:
        goalie_info = f"{goalie_handle} **, {goalie_id}"
        deputy_info = f"{deputy.handle}, {deputy.user_id}" if deputy else deputy_info
        goalie_marked = True
    else:
        goalie_info = f"{goalie_handle}, {goalie_id}"

    return f"{goalie_info} | {deputy_info}", goalie_marked


def _process_standard_line(line, next_goalie, goalie_marked):
    """Process a single line for standard modes (not fixed_full)."""
    handle, user_id = map(str.strip, line.replace("**", "").split(","))
    is_goalie = (handle == next_goalie.handle and user_id == next_goalie.user_id)

    if is_goalie and not goalie_marked:
        updated_line = f"{handle} **, {user_id}"
        goalie_marked = True
    else:
        updated_line = f"{handle}, {user_id}"

    return updated_line, goalie_marked


def update_goalie_file(file_path, next_goalie, deputy=None, mode="next_as_deputy"):
    """Update the goalie file to mark the next goalie and deputy."""
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        target_line_index = -1
        if mode == "fixed_full":
            current_goalie_index = _find_current_goalie_index(lines)
            target_line_index = _find_target_line_index(lines, current_goalie_index, next_goalie.handle)

        updated_lines = []
        goalie_marked = False

        for i, line in enumerate(lines):
            original = line.strip()
            if not original:
                updated_lines.append("")
                continue

            if mode == "fixed_full":
                updated_line, goalie_marked = _process_fixed_full_line(
                    original, i, target_line_index, next_goalie, deputy, goalie_marked
                )
            else:
                updated_line, goalie_marked = _process_standard_line(
                    original, next_goalie, goalie_marked
                )

            updated_lines.append(updated_line)

        with open(file_path, "w") as f:
            f.writelines(f"{line}\n" for line in updated_lines)

        print(
            f"✅ Goalie file updated: Goalie = {next_goalie.handle}, Deputy = {deputy.handle if deputy else 'None'}"
        )

    except Exception as e:
        print(f"❌ Error updating goalie file: {e}")
