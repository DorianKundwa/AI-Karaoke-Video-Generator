import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StoragePaths:
    base_dir: Path
    uploads_dir: Path
    outputs_dir: Path
    tmp_dir: Path


def get_storage_paths() -> StoragePaths:
    base = Path(os.getenv("STORAGE_DIR", Path.cwd() / "data"))
    uploads = base / "uploads"
    outputs = base / "outputs"
    tmp = base / "tmp"
    for d in [uploads, outputs, tmp]:
        d.mkdir(parents=True, exist_ok=True)
    return StoragePaths(base, uploads, outputs, tmp)


