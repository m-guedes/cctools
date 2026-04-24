"""Fetch and display Claude subscription rate-limit usage.

Cookies are read from, in priority order:
    1. ``--cookies PATH``
    2. ``$CLAUDE_COOKIE_JAR``
    3. stdin, if piped

Org ID from ``--org`` or ``$CLAUDE_ORG_ID``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from cctools.jar import load
from cctools.usage import fetch, render

_STDIN = Path("/dev/stdin")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    org = args.org or os.environ.get("CLAUDE_ORG_ID")
    if not org:
        print("error: --org or $CLAUDE_ORG_ID required", file=sys.stderr)
        return 2
    source = _cookie_source(args.cookies)
    if source is None:
        print(
            "error: provide --cookies PATH, set $CLAUDE_COOKIE_JAR, or pipe a jar on stdin",
            file=sys.stderr,
        )
        return 2
    print(render(fetch(org, load(source))))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cookies",
        type=Path,
        help="Netscape cookie jar (default: $CLAUDE_COOKIE_JAR, else stdin)",
    )
    parser.add_argument("--org", help="Claude organization ID (default: $CLAUDE_ORG_ID)")
    return parser.parse_args(argv)


def _cookie_source(explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit
    if env := os.environ.get("CLAUDE_COOKIE_JAR"):
        return Path(env)
    if not sys.stdin.isatty():
        return _STDIN
    return None


if __name__ == "__main__":
    raise SystemExit(main())
