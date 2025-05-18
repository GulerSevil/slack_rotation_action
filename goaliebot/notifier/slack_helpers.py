from goaliebot.slack_api import (
    update_usergroup_with_goalie_and_deputy,
    update_channel_description,
    send_goalie_notification,
)


def compose_goalie_notification(next_goalie, next_deputy, user_group_id):
    if next_deputy:
        return (
            f"🎉 <@{next_goalie.user_id}> is the goalie today! "
            f"👮‍♂️ Your trusty deputy is <@{next_deputy.user_id}> 🙌. "
            f"Give the team a nudge with <!subteam^{user_group_id}>! 🎉"
        )
    return (
        f"🎉 <@{next_goalie.user_id}> is the goalie today! No deputy assigned. "
        f"Use <!subteam^{user_group_id}> to reach out. 🎯"
    )


def update_slack_state(
    client, slack_channels, user_group_id, next_goalie, next_deputy, message
):
    update_usergroup_with_goalie_and_deputy(
        client, user_group_id, next_goalie, next_deputy
    )
    update_channel_description(client, slack_channels, message)
    send_goalie_notification(client, slack_channels, message)
