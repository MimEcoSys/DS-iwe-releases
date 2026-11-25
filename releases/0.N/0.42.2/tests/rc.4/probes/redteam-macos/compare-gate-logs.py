#!/usr/bin/env python3
"""usage: compare-gate-logs.py <label=log>...  — one row per probe, one column per build.

Reads logs of probe-session-gate*.sh (same fixtures, same order) and prints the probes whose
verdict differs between builds or is not "ok" somewhere. Cell: verdict, plus "landed" when the
executed command really produced a commit in the IWE repository.
"""
import re
import sys

HEAD = re.compile(r"^(ok|OPEN|DIFF)\s*\| want=(\w+)\s+got=(\w+)\s*\| (.*)$")


def parse(path):
    rows = []
    for line in open(path, encoding="utf-8", errors="replace"):
        m = HEAD.match(line)
        if m:
            rows.append({"flag": m.group(1), "want": m.group(2), "got": m.group(3), "label": m.group(4).strip(), "landed": ""})
        elif rows and "executed: a new commit" in line:
            rows[-1]["landed"] = " landed"
    return rows


labels, tables = [], []
for arg in sys.argv[1:]:
    name, path = arg.split("=", 1)
    labels.append(name)
    tables.append(parse(path))
assert len({len(t) for t in tables}) == 1, "logs hold a different number of probes"
print(" | ".join(labels) + " | want | probe")
for rows in zip(*tables):
    assert len({r["label"] for r in rows}) == 1, rows[0]["label"]
    if all(r["flag"] == "ok" for r in rows):
        continue
    print(" | ".join(f"{r['got']}{r['landed']}" for r in rows) + f" | {rows[0]['want']} | {rows[0]['label']}")
