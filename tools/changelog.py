"""Template CHANGELOG.md parsing shared by the board and the decisions check (WP-529 Ф282).

One parser, one key formula: a record's key U-xxxxxx is the SHA-1 of the first 200 characters of
its first line, so a deferred record returned to "Unreleased" unchanged keeps its candidate key.
"""

from __future__ import annotations

import hashlib
import re

VERSION_HEAD = re.compile(r"^## \[(?P<ver>[^\]]+)\]")


def changelog_sections(changelog: str) -> dict[str, list[dict]]:
    sections, current, group = {}, None, ""
    for line in changelog.splitlines():
        head = VERSION_HEAD.match(line)
        if head:
            current, group = head.group("ver"), ""
            sections[current] = []
            continue
        if current is None:
            continue
        if line.startswith("### "):
            group = line[4:].strip()
        elif line.startswith("- "):
            text = line[2:].strip()
            tag = re.match(r"^\[(\w[\w-]*)\]\s*", text)
            sections[current].append(
                {
                    "key": "U-" + hashlib.sha1(text[:200].encode()).hexdigest()[:6],
                    "group": group,
                    "tag": tag.group(1) if tag else "",
                    "text": text[tag.end() :] if tag else text,
                }
            )
    return sections
