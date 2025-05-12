
# 🥅 Slack Goalie Rotation GitHub Action

A custom GitHub Action that automatically rotates your team's goalie (on-call lead) and optionally a deputy, updating a rotation file and posting to Slack.

---

## 🚀 Features

- Rotates goalie and deputy based on a flat file
- Supports multiple rotation modes: `next_as_deputy`, `former_goalie_is_deputy`, `no_deputy`, `fixed_full`
- Posts current goalie to Slack
- Easy to integrate in CI via GitHub Actions

---

## 🧩 Inputs

| Name                | Description                                                       | Required | Default         |
|---------------------|-------------------------------------------------------------------|----------|-----------------|
| `slack-token`       | Slack bot token with chat permission                              | ✅       | —               |
| `slack-channels`    | A list of Slack channel IDs or names to send the notification to.                           | ✅       | —               |
| `file-path`         | Path to the goalie rotation file                                  | ✅       | —               |
| `mode`              | Rotation mode (`next_as_deputy`, `fixed_full`, etc.)              | ✅       | `next_as_deputy` |
| `user-group-handle` | Slack user group handle to update (e.g., `@goalie`)              | ✅  | —                 |

---

## 🧪 Supported Modes

- **`next_as_deputy`**: Next in line becomes goalie, the one after is deputy.
- **`former_goalie_is_deputy`**: The previous goalie becomes deputy.
- **`no_deputy`**: Only goalie is rotated.
- **`fixed_full`**: Goalie and deputy are pre-paired in the file.

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
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 09:00 UTC
  workflow_dispatch:

jobs:
  rotate-goalie:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Rotate and Notify
        uses: GulerSevil/slack_rotation_action@main
        with:
          slack-token: ${{ secrets.SLACK_BOT_TOKEN }}
          file-path: 'scripts/goalie_rotation.txt'
          mode: 'next_as_deputy'
          slack-channels: 'C01ABCD2345'
          user-group-handle: '@goalie'

```

---

## 🧪 Development & Testing

```bash
# Set up
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt

# Run tests
pytest scripts/tests
```

---

## 🔒 Secrets

Store your Slack credentials in GitHub Action secrets:

- `SLACK_TOKEN`: Your Slack bot token (starts with `xoxb-`)
- `SLACK_CHANNEL_ID`: The ID of the channel to post goalie updates

---

## 🧠 Tips

- Run this action weekly using cron to automate on-call rotations.
- Keep `goalie.txt` in version control for auditability.
- To dry-run locally, set environment variables and call `main.py`.

---

## 👥 Contributing

Pull requests welcome! Please include tests and follow the existing code structure.

---

## 📄 License

MIT
