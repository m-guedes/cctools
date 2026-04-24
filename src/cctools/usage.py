"""Claude subscription usage: fetch and render.

The endpoint is the internal JSON call the console's usage page makes:
`https://claude.ai/api/organizations/<org>/usage`. It is unversioned and can
change without notice, so this module stays deliberately small.
"""

from __future__ import annotations

from dataclasses import dataclass
from http.cookiejar import CookieJar
from typing import Any

from curl_cffi import requests

_USAGE_URL = "https://claude.ai/api/organizations/{org}/usage"
_TIMEOUT_S = 15

# The endpoint rejects non-browser clients with 403. These headers mirror what
# Firefox sends from the usage page; `anthropic-client-platform` appears to be
# the gating check, but a browser-shaped User-Agent and Referer are included
# defensively since the backend is free to tighten at any time.
_BROWSER_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0"),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://claude.ai/settings/usage",
    "anthropic-client-platform": "web_claude_ai",
}

# (payload key, human label) in display order. Top-level blocks not listed here
# are ignored; `extra_usage` is handled separately because its shape differs.
_WINDOWS: tuple[tuple[str, str], ...] = (
    ("five_hour", "5-hour window"),
    ("seven_day", "7-day overall"),
    ("seven_day_sonnet", "7-day Sonnet"),
    ("seven_day_opus", "7-day Opus"),
)


@dataclass(frozen=True)
class UsageRow:
    label: str
    utilization: float
    resets_at: str | None


def fetch(org_id: str, cookies: CookieJar) -> dict[str, Any]:
    response = requests.get(
        _USAGE_URL.format(org=org_id),
        cookies=cookies,
        headers=_BROWSER_HEADERS,
        timeout=_TIMEOUT_S,
        impersonate="firefox135",
    )
    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:500]}")
    return response.json()


def rows(payload: dict[str, Any]) -> list[UsageRow]:
    result = [row for key, label in _WINDOWS if (row := _row(label, payload.get(key)))]
    if extra := _extra_row(payload.get("extra_usage")):
        result.append(extra)
    return result


def render(payload: dict[str, Any]) -> str:
    return "\n".join(
        f"{r.label:<20} {r.utilization:>5.1f}%   resets {r.resets_at or '-'}" for r in rows(payload)
    )


def _row(label: str, block: dict[str, Any] | None) -> UsageRow | None:
    if not block or block.get("utilization") is None:
        return None
    return UsageRow(label, float(block["utilization"]), block.get("resets_at"))


def _extra_row(block: dict[str, Any] | None) -> UsageRow | None:
    if not block or not block.get("is_enabled") or block.get("utilization") is None:
        return None
    return UsageRow("extra usage", float(block["utilization"]), block.get("resets_at"))
