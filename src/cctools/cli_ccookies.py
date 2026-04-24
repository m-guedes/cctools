"""Extract Claude session cookies from a browser into a Netscape jar.

The jar is emitted to ``--output`` (default: stdout) so it can be piped into
``ccusage`` or consumed by any tool that speaks the Netscape format (e.g.
``curl -b``).
"""

from __future__ import annotations

import argparse
import sys
from http.cookiejar import CookieJar
from pathlib import Path

from cctools.firefox import ProfileError, load_claude_cookies
from cctools.jar import dump

_STDOUT = Path("/dev/stdout")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        jar = _extract(args)
    except ProfileError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    dump(jar, args.output)
    return 0


def _extract(args: argparse.Namespace) -> CookieJar:
    # argparse `required=True` on the subparser guarantees a known browser.
    if args.browser == "firefox":
        return load_claude_cookies(args.profile)
    raise AssertionError(args.browser)  # pragma: no cover


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="browser", required=True)

    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument(
        "-o",
        "--output",
        type=Path,
        default=_STDOUT,
        help="destination file for the Netscape jar (default: stdout)",
    )

    firefox = sub.add_parser(
        "firefox",
        parents=[shared],
        help="extract from a Firefox profile",
    )
    firefox.add_argument(
        "--profile",
        required=True,
        help="profile name as shown in about:profiles (substring match allowed)",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
