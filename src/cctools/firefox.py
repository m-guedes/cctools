"""Read Claude session cookies from a Firefox profile (Linux).

Profiles are resolved via ``~/.mozilla/firefox/profiles.ini`` so callers pass
the human-readable profile name shown in ``about:profiles``, not the hashed
directory name.
"""

from __future__ import annotations

import configparser
from http.cookiejar import CookieJar
from pathlib import Path

import browser_cookie3

FIREFOX_ROOT = Path.home() / ".mozilla" / "firefox"
_PROFILES_INI = FIREFOX_ROOT / "profiles.ini"
_CLAUDE_DOMAIN = "claude.ai"


class ProfileError(LookupError):
    """Raised when a profile name cannot be uniquely resolved."""


def load_claude_cookies(profile: str) -> CookieJar:
    cookie_db = _resolve_cookie_db(profile)
    return browser_cookie3.firefox(
        cookie_file=str(cookie_db), domain_name=_CLAUDE_DOMAIN
    )


def _resolve_cookie_db(profile: str) -> Path:
    profiles = _read_profiles()
    matches = [(name, path) for name, path in profiles.items() if profile in name]
    if not matches:
        raise ProfileError(
            f"no Firefox profile matching '{profile}'. Known: {sorted(profiles)}"
        )
    if len(matches) > 1:
        raise ProfileError(f"ambiguous profile '{profile}': {[n for n, _ in matches]}")
    return FIREFOX_ROOT / matches[0][1] / "cookies.sqlite"


def _read_profiles() -> dict[str, str]:
    parser = configparser.ConfigParser()
    parser.read(_PROFILES_INI)
    return {
        parser[s]["Name"]: parser[s]["Path"]
        for s in parser.sections()
        if s.startswith("Profile") and "Name" in parser[s] and "Path" in parser[s]
    }
