from pathlib import Path

import pytest

from common.blender import cache


@pytest.fixture
def fake_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE", tmp_path)
    monkeypatch.setattr(cache, "platform_tag", lambda: ("linux-x64", ".tar.xz"))
    return tmp_path


def test_a_cached_blender_is_reused_without_downloading(fake_cache, monkeypatch):
    binary = fake_cache / "4.5.14-linux-x64" / "blender"
    binary.parent.mkdir()
    binary.write_text("#!/bin/sh\n")
    monkeypatch.setattr(cache, "_download",
                        lambda url, dest: pytest.fail("should not download"))
    assert cache.ensure_blender("4.5.14") == binary


def test_a_checksum_mismatch_deletes_the_archive(tmp_path, monkeypatch):
    archive = tmp_path / "blender.tar.xz"
    archive.write_bytes(b"not really blender")
    sums = tmp_path / "checksums.json"
    sums.write_text('{"blender.tar.xz": "0000"}')
    monkeypatch.setattr(cache, "CHECKSUMS_FILE", sums)
    with pytest.raises(RuntimeError, match="Checksum mismatch"):
        cache._verify(archive, "blender.tar.xz")
    assert not archive.exists()