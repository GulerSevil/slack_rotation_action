from goaliebot.core.models import Command


def print_success_summary(
    next_goalie, next_deputy, slack_channels, user_group_id, commands, cadence
):
    print("\n✅ Goalie rotation complete!")
    print(f"ℹ️ Cadence: {cadence}")
    print(f"👮 Goalie      : {next_goalie.handle} (<@{next_goalie.user_id}>)")
    if next_deputy:
        print(f"🛡️ Deputy      : {next_deputy.handle} (<@{next_deputy.user_id}>)")
    else:
        print("🛡️ Deputy      : None")
    print(f"📢 Channels    : {', '.join(slack_channels)}")
    print(f"👥 User Group  : {user_group_id}")

    updates = ["user group updated"]

    if commands:
        if Command.UPDATE_TOPIC_DESCRIPTION in commands:
            updates.append("channel topic updated")
        if Command.SEND_SLACK_MESSAGE in commands:
            updates.append("message sent")

    print(f"🎯 Slack updates: {', '.join(updates)}.")
