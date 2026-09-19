import json
import subprocess
import tempfile
from pathlib import Path

from common.blender.blender_header import blend_version
from common.blender.cache import ensure_blender
from common.blender.versions import resolve_full_version

from common.config import settings

SCAN_SCRIPT = Path(__file__).with_name("scan_blend.py")

def scan_file(blend: Path) -> dict:
    series = blend_version(blend)
    binary = ensure_blender()