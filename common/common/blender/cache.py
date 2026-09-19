import hashlib
import json
import os
import platform
import shutil
import subprocess
import tarfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

CHECKSUMS_FILE = Path(__file__).with_name("checksums.json")
CACHE = Path(os.getenv("BLENDER_CACHE_DIR", Path.home() / ".cache" / "blender"))
DOWNLOAD_BASE = os.getenv("BLENDER_DOWNLOAD_BASE", "https://download.blender.org/release")
USER_AGENT = "blenderServices/1.0"


def platform_tag() -> tuple[str, str]:
    system = platform.system()
    machine = platform.machine().lower()
    if system == "Linux" and machine in ("x86_64", "amd64"):
        return "linux-x64", ".tar.xz"
    if system == "Windows" and machine in ("x86_64", "amd64"):
        return "windows-x64", ".zip"
    if system == "Darwin" and machine == "arm64":
        return "macos-arm64", ".dmg"
    raise RuntimeError(f"Unsupported platform: {system} {machine}")


def binary_path(root: Path, tag: str) -> Path:
    if tag.startswith("linux"):
        return root / "blender"
    if tag.startswith("windows"):
        return root / "blender.exe"
    return root / "Blender.app" / "Contents" / "MacOS" / "Blender"


def _download(url: str, dest: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=120) as response, open(dest, "wb") as out:
            shutil.copyfileobj(response, out, length=1024 * 1024)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Download failed with HTTP {exc.code}: {url}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach {url}: {exc.reason}") from exc


def _verify(archive: Path, archive_name: str) -> None:
    expected = json.loads(CHECKSUMS_FILE.read_text()) if CHECKSUMS_FILE.exists() else {}
    want = expected.get(archive_name)
    if want is None:
        print(f"WARNING: no SHA-256 recorded for {archive_name}, skipping verification")
        return
    digest = hashlib.sha256()
    with open(archive, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != want:
        archive.unlink(missing_ok=True)
        raise RuntimeError(f"Checksum mismatch for {archive_name}")


def ensure_blender(full_version: str) -> Path:
    """Path to a runnable Blender of this exact version, downloading it once."""
    tag, ext = platform_tag()
    target = CACHE / f"{full_version}-{tag}"
    binary = binary_path(target, tag)
    if binary.exists():
        return binary

    series = ".".join(full_version.split(".")[:2])
    name = f"blender-{full_version}-{tag}"
    CACHE.mkdir(parents=True, exist_ok=True)
    archive = CACHE / f"{name}.{os.getpid()}{ext}"
    partial = CACHE / f"{name}.{os.getpid()}.partial"

    _download(f"{DOWNLOAD_BASE}/Blender{series}/{name}{ext}", archive)
    _verify(archive, f"{name}{ext}")

    shutil.rmtree(partial, ignore_errors=True)
    partial.mkdir()
    try:
        if ext == ".tar.xz":
            with tarfile.open(archive) as tf:
                tf.extractall(partial, filter="data")
            shutil.move(str(partial / name), str(target))
        elif ext == ".zip":
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(partial)
            shutil.move(str(partial / name), str(target))
        else:
            mount = CACHE / f"dmg_mount_{os.getpid()}"
            mount.mkdir(exist_ok=True)
            subprocess.run(["hdiutil", "attach", str(archive), "-nobrowse",
                            "-readonly", "-mountpoint", str(mount)], check=True)
            try:
                target.mkdir(parents=True)
                subprocess.run(["ditto", str(mount / "Blender.app"),
                                str(target / "Blender.app")], check=True)
            finally:
                subprocess.run(["hdiutil", "detach", str(mount)], check=True)
                mount.rmdir()
    finally:
        shutil.rmtree(partial, ignore_errors=True)
        archive.unlink(missing_ok=True)

    if not binary.exists():
        raise RuntimeError(f"Blender binary not found at {binary}")
    if os.name != "nt":
        binary.chmod(binary.stat().st_mode | 0o111)
    return binary