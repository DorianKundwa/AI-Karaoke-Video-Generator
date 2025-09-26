from pathlib import Path
import os
from fastapi import UploadFile


def ensure_dir(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_upload(file: UploadFile, destination_dir: Path) -> Path:
    ensure_dir(destination_dir)
    safe_name = os.path.basename(file.filename or "upload.bin")
    target = destination_dir / safe_name
    with open(target, "wb") as f:
        f.write(file.file.read())
    return target


def read_text_file(path: Path | str) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8", errors="ignore")


