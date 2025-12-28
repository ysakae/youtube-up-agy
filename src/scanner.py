import os
import xxhash
import logging
from pathlib import Path
from typing import Generator, List

logger = logging.getLogger("youtube_up")

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

def calculate_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """
    Calculate xxHash64 of a file efficiently.
    """
    hasher = xxhash.xxh64()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {file_path}: {e}")
        return ""

def scan_directory(directory: str) -> Generator[Path, None, None]:
    """
    Recursively scan a directory for video files.
    """
    path = Path(directory)
    if not path.exists():
        logger.error(f"Directory not found: {directory}")
        return

    for entry in path.rglob("*"):
        if entry.is_file() and entry.suffix.lower() in VIDEO_EXTENSIONS:
            # Ignore hidden files
            if entry.name.startswith("."):
                continue
            yield entry
