"""Netscape cookie jar serialization.

This is the wire format between ``ccookies`` and ``ccusage`` (the same format
curl's ``-b`` / ``-c`` flags speak) so that cookie extraction and API fetching
remain independently usable and composable.

Session cookies (``expires=0``) and expired cookies are preserved across the
round trip; Claude's auth cookies are long-lived but we stay permissive rather
than silently dropping anything the caller provided.
"""

from __future__ import annotations

from http.cookiejar import CookieJar, MozillaCookieJar
from pathlib import Path


def dump(jar: CookieJar, path: Path) -> None:
    _as_mozilla(jar).save(str(path), ignore_discard=True, ignore_expires=True)


def load(path: Path) -> CookieJar:
    jar = MozillaCookieJar()
    jar.load(str(path), ignore_discard=True, ignore_expires=True)
    return jar


def _as_mozilla(jar: CookieJar) -> MozillaCookieJar:
    if isinstance(jar, MozillaCookieJar):
        return jar
    out = MozillaCookieJar()
    for cookie in jar:
        out.set_cookie(cookie)
    return out
