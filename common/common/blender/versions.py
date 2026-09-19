import json
from pathlib import Path

VERSIONS_FILE = Path(__file__).with_name("versions.json")


def _versions() -> dict[str, str]:
    return json.loads(VERSIONS_FILE.read_text())


def resolve_full_version(series: str | None) -> str:
    if not series:
        raise ValueError("Project has no Blender version recorded")
    versions = _versions()
    if series not in versions:
        raise ValueError(f"No Blender release configured for series {series}")
    return versions[series]


def known_full_versions() -> set[str]:
    return set(_versions().values())