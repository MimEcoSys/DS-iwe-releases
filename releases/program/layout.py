"""Where things live in DS-iwe-releases (WP-529 F278): every path the programs read or write.

The layout follows DP.METHOD.265 (PACK-digital-platform): each folder has one purpose,
helper programs and their inputs live inside the module they serve.
"""

from __future__ import annotations

from pathlib import Path

NOW_PAGE = Path("NOW.md")
README = Path("README.md")
OLD_BOARD_POINTER = Path("BOARD.md")

BOARD_DIR = Path("board")
BOARD_PAGE = BOARD_DIR / "README.md"
SNAPSHOT = BOARD_DIR / "snapshot.yaml"
DEVELOPER_LINKS = BOARD_DIR / "developer-links.yaml"
DEVELOPER_SOURCES = BOARD_DIR / "developer-sources.yaml"
BOARD_BUILDER = BOARD_DIR / "program" / "build_board.py"

RELEASES_DIR = Path("releases")
CATALOG = RELEASES_DIR / "index.yaml"
CATALOG_JSON = RELEASES_DIR / "catalog.json"
INDEX_PAGE = RELEASES_DIR / "INDEX.md"
HISTORY_PAGE = RELEASES_DIR / "HISTORY.md"
NEXT_PAGE = RELEASES_DIR / "NEXT.md"
HANDOFF = RELEASES_DIR / "developer-handoff.yaml"

METHOD_DIR = Path("method")
BOARD_RULES = METHOD_DIR / "board-rules.md"
TEAM_DIR = Path("team")


def release_dir(version: str) -> Path:
    """releases/<first number>.N/<version>: versions are grouped by their first number (pilot, 18.11)."""
    return RELEASES_DIR / f"{version.split('.', 1)[0]}.N" / version


def release_dirs(repo: Path) -> list[Path]:
    """Every version folder on disk, repository-relative, in version order."""
    found = [path.relative_to(repo) for group in sorted((repo / RELEASES_DIR).glob("*.N"))
             for path in group.iterdir() if path.is_dir()]
    return sorted(found, key=lambda path: tuple(int(part) for part in path.name.split(".") if part.isdigit()))
