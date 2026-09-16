from pathlib import Path

import pytest

from common.blender.blender_header import blend_version

FIXTURES = Path(__file__).parent / "fixtures"

@pytest.mark.parametrize("head, expected", [
     # Format version 0, 12 bytes.
    (b"BLENDER_v293", "2.93"),
    (b"BLENDER-v402", "4.2"),
    (b"BLENDER-v405", "4.5"),
    (b"BLENDER-v500", "5.0"),
    # Format version 1, 17 bytes.
    (b"BLENDER17-01v0405", "4.5"),
    (b"BLENDER17-01v0500", "5.0"),
    (b"BLENDER17-01v0502", "5.2"),

])
def test_header_layouts(tmp_path, head, expected):
    path = tmp_path / "synthetic.blend"
    path.write_bytes(head + b"\x00" * 64)
    assert blend_version(path) == expected
 
 
@pytest.mark.parametrize("name, expected", [
    ("cube_4_5.blend", "4.5"),
    ("cube_4_5_compressed.blend", "4.5"),
    ("cube_5_2.blend", "5.2"),
])
def test_real_files(name, expected):
    path = FIXTURES / name
    if not path.exists():
        pytest.skip(f"missing fixture {name}")
    assert blend_version(path) == expected
 
 
def test_rejects_non_blend(tmp_path):
    fake = tmp_path / "fake.blend"
    fake.write_bytes(b"this is not a blender file")
    with pytest.raises(ValueError):
        blend_version(fake)
 
 
def test_rejects_truncated_file(tmp_path):
    fake = tmp_path / "short.blend"
    fake.write_bytes(b"BLE")
    with pytest.raises(ValueError):
        blend_version(fake)



