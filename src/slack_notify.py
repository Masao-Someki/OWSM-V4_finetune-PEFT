from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _default_host() -> str:
    try:
        return socket.gethostname()
    except Exception:
        return "unknown-host"


def post_slack_message(
    *,
    text: str,
    webhook_url: Optional[str] = None,
    username: str = "autoresearch-bot",
    icon_emoji: str = ":microscope:",
) -> bool:
    """Best-effort Slack notification via incoming webhook.

    Returns True when sent, False otherwise. Never raises.
    """
    url = (webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")).strip()
    if not url:
        return False

    payload = {
        "username": username,
        "icon_emoji": icon_emoji,
        "text": text,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10):
            return True
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return False
    except Exception:
        return False


def format_status_message(
    *,
    title: str,
    body_lines: list[str],
) -> str:
    lines = [f"*{title}*", f"- time: `{_now_iso()}`"]
    lines.extend(body_lines)
    return "\n".join(lines)
