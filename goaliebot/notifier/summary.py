def print_success_summary(next_goalie, next_deputy, slack_channels, user_group_id):
    print("\n✅ Goalie rotation complete!")
    print(f"👮 Goalie      : {next_goalie.handle} (<@{next_goalie.user_id}>)")
    if next_deputy:
        print(f"🛡️ Deputy      : {next_deputy.handle} (<@{next_deputy.user_id}>)")
    else:
        print("🛡️ Deputy      : None")
    print(f"📢 Channels    : {', '.join(slack_channels)}")
    print(f"👥 User Group  : {user_group_id}")
    print(
        "🎯 Slack user group updated, channel description refreshed, and message sent."
    )
