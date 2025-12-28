# Change Detector

A Python-based webpage change detector that monitors a webpage for changes and sends notifications via Discord webhook.

## Features

- 🔍 Monitor any webpage for content changes
- 🎯 Target specific elements using CSS selectors
- 🔔 Discord webhook notifications with rich embeds
- 🕐 Configurable check intervals with randomization
- 🐳 Docker-ready for easy deployment
- 🦊 Firefox browser impersonation via curl_cffi

## Requirements

- Python 3.13+
- UV package manager (or Docker)

## Configuration

All configuration is done via environment variables. Copy `.env.example` to `.env` and adjust the values:

| Variable | Description | Default |
|----------|-------------|---------|
| `WEBHOOK_DISCORD` | Discord webhook URL | (required) |
| `WEBPAGE_URL` | URL to monitor | (required) |
| `WEBPAGE_ELEMENT` | CSS selector path (pipe-separated) | (entire body) |
| `WEBPAGE_RELOAD_TIME` | Check interval in ms | `60000` |
| `WEBPAGE_RELOAD_STD` | Random delay std dev (in ms) | `500` |
| `TIMEZONE` | Timezone for logs | `UTC` |

### CSS Selector Path

The `WEBPAGE_ELEMENT` variable uses a pipe-separated format to navigate through nested elements:

```
#main|.content|#target-element
```

This is equivalent to selecting `#main`, then finding `.content` inside it, then finding `#target-element` inside that.

## Installation

### Local Development

```bash
# Clone the repository
git clone <repository-url>
cd page-change-notifier

# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Install dependencies and run
uv sync
uv run python main.py
```

## Docker Deployment

### Using Docker Run

```bash
# Build the image
docker buildx build -t page-change-notifier .

# Run with environment variables
docker run -d \
  --name page-change-notifier \
  --restart unless-stopped \
  --dns 1.1.1.1 \
  --dns 1.0.0.1 \
  --dns 8.8.8.8 \
  --dns 8.8.4.4 \
  -e WEBHOOK_DISCORD="https://discord.com/api/webhooks/xxx/yyy" \
  -e WEBPAGE_URL="https://example.com/page" \
  -e WEBPAGE_ELEMENT="#main|.content" \
  -e WEBPAGE_RELOAD_TIME="60000" \
  -e WEBPAGE_RELOAD_STD="500" \
  -e TIMEZONE="Europe/Paris" \
  page-change-notifier
```

### Using Docker Compose

1. Create a `.env` file with your configuration:

```bash
cp .env.example .env
# Edit .env with your values
```

2. Start the service:

```bash
docker compose up -d
```

3. View logs:

```bash
docker compose logs -f
```

4. Stop the service:

```bash
docker compose down
```

### Docker Compose with Inline Configuration

You can also create a `docker-compose.override.yml` for custom configurations:

```yaml
services:
  page-change-notifier:
    environment:
      - WEBHOOK_DISCORD=https://discord.com/api/webhooks/xxx/yyy
      - WEBPAGE_URL=https://example.com/page
      - WEBPAGE_ELEMENT=#main|.content
      - WEBPAGE_RELOAD_TIME=30000
      - TIMEZONE=Europe/Paris
```

## Log Format

Logs follow this format:

```
[DD-MM-YYYY HH:MM:SS] - LEVEL - Message
```

Example output:

```
[28-12-2025 14:30:00] - INFO - Starting change detector for https://example.com/page
[28-12-2025 14:30:00] - INFO - Element selector: #main|.content
[28-12-2025 14:30:00] - INFO - Reload interval: 60000ms (std: 0.5s)
[28-12-2025 14:30:01] - INFO - Initial content stored. Success: 1, Errors: 0
[28-12-2025 14:31:02] - DEBUG - Time since last request: 61.23s
[28-12-2025 14:31:02] - INFO - No change. Success: 2, Errors: 0
[28-12-2025 14:32:01] - DEBUG - Time since last request: 59.87s
[28-12-2025 14:32:01] - INFO - CHANGE DETECTED! Success: 3, Errors: 0
[28-12-2025 14:32:01] - INFO - Notification sent to Discord
```

## Architecture

```
page-change-notifier/
├── config.py           # Environment variable loading
├── main.py             # Main application loop
├── page_tracker.py     # HTML extraction utilities
├── notifiers/
│   ├── __init__.py
│   ├── base.py         # Abstract notifier base class
│   └── discord.py      # Discord webhook implementation
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Extending Notifiers

To add a new notification backend:

1. Create a new file in `notifiers/` (e.g., `slack.py`)
2. Inherit from `BaseNotifier`
3. Implement `send_notification()` and `close()` methods

```python
from notifiers.base import BaseNotifier

class SlackNotifier(BaseNotifier):
    async def send_notification(self, title: str, message: str, url: str):
        # Implementation here
        pass

    async def close(self):
        # Cleanup here
        pass
```

## License

MIT License

