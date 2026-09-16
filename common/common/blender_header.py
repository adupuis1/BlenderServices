import gzip
import re
from pathlib import Path
 
import zstandard
 
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"
GZIP_MAGIC = b"\x1f\x8b"
 
# Blender writes one of exactly two header layouts. Both are defined in
# source/blender/blenloader_core/BLO_core_blend_header.hh in the Blender source.
#
# Format version 0 - 12 bytes:
#   0-6   b"BLENDER"
#   7     "-" for 8-byte pointers, "_" for 4-byte pointers
#   8     "v" little endian, "V" big endian
#   9-11  three ASCII digits: one major, two minor
#         "402" -> 4.2, "293" -> 2.93, "500" -> 5.0
#
# Format version 1 - 17 bytes, added for files with data blocks over 2 GB:
#   0-6   b"BLENDER"
#   7-8   header length in ASCII digits, currently always "17"
#   9     always "-"
#   10-11 header format version in ASCII digits, currently always "01"
#   12    always "v" (only little-endian systems write this layout)
#   13-16 four ASCII digits: two major, two minor
#         "0405" -> 4.5, "0500" -> 5.0
HEADER_V1 = re.compile(rb"^BLENDER\d{2}-\d{2}[vV](\d{2})(\d{2})")
HEADER_V0 = re.compile(rb"^BLENDER[_-][vV](\d)(\d{2})")
 
 
def read_head(path: Path, size: int = 64) -> bytes:
    """First `size` bytes of a .blend, transparently decompressing it."""
    with open(path, "rb") as f:
        magic = f.read(4)
        f.seek(0)
        try:
            if magic == ZSTD_MAGIC:
                return zstandard.ZstdDecompressor().stream_reader(f).read(size)
            if magic[:2] == GZIP_MAGIC:
                with gzip.open(f) as g:
                    return g.read(size)
        except (zstandard.ZstdError, OSError, EOFError) as exc:
            raise ValueError(f"Could not decompress .blend file: {exc}") from exc
        return f.read(size)
 
 
def blend_version(path: Path) -> str:
    """Version series of a .blend file, for example '4.5'."""
    head = read_head(Path(path))
    match = HEADER_V1.match(head) or HEADER_V0.match(head)
    if not match:
        raise ValueError("Not a valid .blend file")
    return f"{int(match.group(1))}.{int(match.group(2))}"
