# 🥅 Slack Goalie Rotation GitHub Action

A custom GitHub Action that automatically rotates your team's goalie (on-call lead) and optionally a deputy, updating a rotation file and posting to Slack.

---

## 🚀 Features

- Rotates goalie and deputy based on a flat file
- Supports multiple rotation modes: `next_as_deputy`, `former_goalie_is_deputy`, `no_deputy`, `fixed_full`
- Updates Slack user group
- Optionally sends Slack messages and updates channel topics
- Flexible command configuration via CLI or GitHub Actions

---

## 🧩 Inputs

| Name                | Description                                                                        | Required | Default           |
|---------------------|------------------------------------------------------------------------------------|----------|-------------------|
| `slack-token`       | Slack user token with permissions (see below)                                      | ✅       | —                 |
| `slack-channels`    | Comma-separated list of Slack channel IDs (required only for some commands , or if commands omitted)       | ❌       | —                 |
| `file-path`         | Path to the goalie rotation file                                                   | ✅       | —                 |
| `mode`              | Rotation mode (`next_as_deputy`, `fixed_full`, etc.)                               | ✅       | `next_as_deputy`  |
| `user-group-handle` | Slack user group handle (required for `update_user_group`, or if commands omitted) | ❌ | —          |
| `commands`          | Pipe-separated list of Slack commands to run (see below)                           | ❌       | All commands      |
| `cadence`           | Rotation cadence (`day`, `week`, `month`)                                  | ❌       | `week`            |

- `slack-channels` is required **if**:
    - `commands` is not provided (defaults to all commands)
    - `commands` includes `send_slack_message`
    - `commands` includes `update_topic_description`

- `user-group-handle` is required **if**:
    - `commands` is not provided (defaults to all commands)
    - `commands` includes `update_user_group`

---

## ⚙️ Supported Commands

The `commands` input accepts one or more of the following, separated by `|`:

| Command                    | Description                                      |
|----------------------------|--------------------------------------------------|
| `update_user_group`        | Updates the user group with current goalie/deputy |
| `update_topic_description` | Updates the Slack topic of the given channels   |
| `send_slack_message`       | Sends a message to the specified channels       |

If `commands` is not provided, **all commands will be executed by default**.

---

## 🧪 Supported Modes

- **`next_as_deputy`**: Next in line becomes goalie, the one after is deputy.
- **`former_goalie_is_deputy`**: The previous goalie becomes deputy.
- **`no_deputy`**: Only goalie is rotated.
- **`fixed_full`**: Goalie and deputy are pre-paired in the file.

---
## 📆 Supported Cadence

- **`day`**: Rotation happens daily.
- **`week`**: Rotation happens weekly (default).
- **`month`**: Rotation happens monthly.

> 📝 The cadence input controls how the rotation period is described in Slack notifications. Actual scheduling still depends on your CI/CD cron configuration.

---

## 📂 Example File Format

### For `next_as_deputy`, `no_deputy`, `former_goalie_is_deputy`:

```txt
alice, U123
bob **, U222
carol, U333
```

- `**` indicates current goalie

### For `fixed_full`:

```txt
alice, U123 | david, U999
bob **, U222 | erin, U888
carol, U333 | frank, U777
```

---

## ✅ Usage

### `.github/workflows/rotate-goalie.yml`

```yaml
name: Rotate Goalie

on:
  workflow_dispatch:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 09:00 UTC

# ⚠️ This grants write access to contents — needed for committing changes.
# In some cases, using a Personal Access Token (PAT) might be more reliable or secure,
# especially if you face permission issues with GITHUB_TOKEN.
permissions:
  contents: write

jobs:
  rotate-goalie:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Rotate and Notify
        uses: GulerSevil/slack_rotation_action@v1.0.3
        with:
          slack-token: ${{ secrets.SLACK_BOT_TOKEN }}
          file-path: 'scripts/goalie_rotation.txt'
          mode: 'next_as_deputy'
          slack-channels: 'test-slack-channel'
          commands: 'update_topic_description|send_slack_message'
          user-group-handle: 'goaliebot'
          cadence: 'week'

      - name: Configure Git
        run: |
          git config --local user.name "GitHub Actions"
          git config --local user.email "actions@github.com"

      - name: Commit Updated Goalie List
        run: |
          git add "${{github.workspace}}/goalie_schedule.txt"
          git commit -m "Update goalie list"
          git push origin main
        env:
          # ⚠️ You can replace this with a PAT (stored in secrets) if needed:
          # e.g., GITHUB_TOKEN: ${{ secrets.MY_PAT }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 🛠️ Slack App Setup

To use this GitHub Action (or any CI/CD pipeline), you'll need to set up a dedicated Slack app and token. Here's how:

### 🔧 Create a Dedicated Slack App

1. Go to [Slack API Apps](https://api.slack.com/apps) and create a new app in your workspace.
2. Under **OAuth & Permissions**, add the following **OAuth scopes**:

| Scope                  | Description                                              |
|------------------------|----------------------------------------------------------|
| `channels:read`        | View basic information about public channels             |
| `channels:write.topic` | Set the description (topic) of public channels           |
| `chat:write`           | Send messages on a user’s behalf                         |
| `usergroups:read`      | View user groups in a workspace                          |
| `usergroups:write`     | Create and manage user groups                            |

> 💡 We recommend using a **dedicated Slack user** for automation so actions don't show up as your personal account.

3. Install the app to your workspace and generate a **User OAuth Token** (starts with `xoxp-`).

---

## 🔐 Secrets

Store your Slack credentials in your GitHub repository's secrets:

| Secret Name     | Description                                 |
|------------------|---------------------------------------------|
| `SLACK_TOKEN`    | Your User OAuth Token from Slack            |

> 🛡️ These scripts can be used in **any CI/CD** system — not just GitHub Actions — by passing the same token and parameters to the Python script.

---

## 🔄 CI/CD Compatibility

This rotation script is platform-agnostic and works with any CI/CD tool (GitHub Actions, GitLab CI, Jenkins, CircleCI, etc.). Simply run:

```bash
python -m goaliebot.rotation_entry   --file-path path/to/goalie_schedule.txt ... ```

---

## 🧠 Tips

- Run this action weekly using cron to automate on-call rotations.
- Keep `goalie_schedule.txt` in version control for auditability.

---

## 👥 Contributing

Pull requests welcome! Please include tests.

---

## 📄 License

MIT
