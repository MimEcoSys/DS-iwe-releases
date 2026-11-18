"""(copied from the rc.5 red-team run; drift tag made configurable via RT_DRIFT_TAG)
GitHub API mock for disposable red-team runs: answers from real `git ls-remote` data.

Usage: apimock.py LSREMOTE_FILE URL -> prints JSON body, exit 0; exit 22 for unknown endpoint.
"""
import json
import re
import sys

ls_file, url = sys.argv[1], sys.argv[2]
REPO = "https://api.github.com/repos/TserenTserenov/FMT-exocortex-template"
refs, peeled = {}, {}
for line in open(ls_file, encoding="utf-8"):
    sha, ref = line.split()
    if ref.endswith("^{}"):
        peeled[ref[:-3]] = sha
    else:
        refs[ref] = sha
import os
if os.environ.get("RT_DRIFT"):
    cnt_file = os.path.join(os.path.dirname(ls_file), "drift.count")
    n = int(open(cnt_file).read()) if os.path.exists(cnt_file) else 0
    if "/git/matching-refs/" in url:
        n += 1
        open(cnt_file, "w").write(str(n))
    if n % 2 == 0:
        refs["refs/tags/" + os.environ["RT_DRIFT_TAG"]] = os.environ["RT_DRIFT"]
commit_of = {r: peeled.get(r, s) for r, s in refs.items()}
LATEST = sys.argv[3] if len(sys.argv) > 3 else "v0.41.11"

path = url[len(REPO):] if url.startswith(REPO) else None
if path is None:
    sys.exit(22)
path = path.split("?")[0]
if path.startswith("/git/matching-refs/tags/"):
    prefix = "refs/tags/" + path[len("/git/matching-refs/tags/"):]
    out = [{"ref": r, "object": {"sha": s, "type": "tag"}} for r, s in sorted(refs.items()) if r.startswith(prefix)]
    # Optional pagination like the real API (RT_PAGINATE=1): honour per_page/page, default 30 per page.
    if os.environ.get("RT_PAGINATE"):
        from urllib.parse import urlparse, parse_qs
        q = parse_qs(urlparse(url).query)
        per = int(q.get("per_page", ["30"])[0]); page = int(q.get("page", ["1"])[0])
        out = out[(page - 1) * per: page * per]
    print(json.dumps(out))
elif path == "/releases/latest":
    print(json.dumps({"tag_name": LATEST, "target_commitish": "main", "draft": False, "prerelease": False}))
elif path.startswith("/releases/tags/"):
    print(json.dumps({"tag_name": path.rsplit("/", 1)[1], "draft": False, "prerelease": False}))
elif path.startswith("/commits/"):
    ref = path[len("/commits/"):]
    if re.fullmatch(r"[0-9a-f]{40}", ref):
        print(json.dumps({"sha": ref}))
    elif "refs/tags/" + ref in commit_of:
        print(json.dumps({"sha": commit_of["refs/tags/" + ref]}))
    else:
        sys.exit(22)
else:
    sys.stderr.write("apimock: unknown endpoint " + path + "\n")
    sys.exit(22)
