#!/usr/bin/env python3
"""Fail if tracked text files contain e-mail addresses or phone numbers.

Part of the publication gate of this public repository (README, "Домены данных").
"""

import re
import subprocess
import sys
from pathlib import Path

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
# International ("+" and country code) or Russian trunk ("8") phone numbers, ten digits after the prefix;
# plain digit runs like issue lists "456-458-459" do not match.
PHONE = re.compile(r"(?<![\w-])(?:\+\d{1,3}|8)[ (-]*\d{3}[ )-]*\d{3}[ -]?\d{2}[ -]?\d{2}(?![\w-])")
ALLOWED_EMAILS = {"noreply@anthropic.com", "noreply@github.com"}
TEXT_SUFFIXES = (".md", ".yaml", ".yml", ".py", ".txt", "CODEOWNERS")


def main() -> int:
    files = subprocess.run(["git", "ls-files"], check=True, capture_output=True, text=True).stdout.split()
    findings = []
    for path in files:
        if not path.endswith(TEXT_SUFFIXES):
            continue
        for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
            for match in EMAIL.findall(line):
                if match.lower() not in ALLOWED_EMAILS:
                    findings.append(f"{path}:{number}: e-mail")
            if PHONE.search(line):
                findings.append(f"{path}:{number}: phone number")
    for finding in findings:
        print(finding)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
