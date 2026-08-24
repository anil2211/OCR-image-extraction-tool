from __future__ import annotations

import re
import uuid
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
    ".pdf",
}

# Maximum upload size: 50 MB
MAX_FILE_SIZE = 50 * 1024 * 1024


# ============================================================
# Filename
# ============================================================

def create_safe_filename(
    filename: str,
) -> str:
    """
    Create a safe unique filename.
    """

    original = Path(filename)

    extension = original.suffix.lower()

    stem = original.stem

    stem = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        stem,
    )

    stem = re.sub(
        r"_+",
        "_",
        stem,
    )

    stem = stem.strip("_")

    if not stem:
        stem = "document"

    unique_id = uuid.uuid4().hex[:8]

    return f"{stem}_{unique_id}{extension}"


# ============================================================
# Extension
# ============================================================

def get_file_extension(
    filename: str,
) -> str:
    return Path(
        filename
    ).suffix.lower()


def validate_extension(
    filename: str,
) -> bool:
    """
    Check whether the file extension is supported.
    """

    extension = get_file_extension(
        filename
    )

    return extension in ALLOWED_EXTENSIONS


def is_allowed_file(
    filename: str,
) -> bool:
    return validate_extension(
        filename
    )


# ============================================================
# File size
# ============================================================

def validate_file_size(
    file_size: int,
    max_size: int = MAX_FILE_SIZE,
) -> bool:
    """
    Validate file size.

    Args:
        file_size:
            Size in bytes.

        max_size:
            Maximum allowed size in bytes.

    Returns:
        True when the file is within the limit.
    """

    if file_size < 0:
        return False

    return file_size <= max_size


# ============================================================
# File type
# ============================================================

def is_image_file(
    filename: str,
) -> bool:

    return get_file_extension(
        filename
    ) in {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".tif",
        ".tiff",
    }


def is_pdf_file(
    filename: str,
) -> bool:

    return (
        get_file_extension(
            filename
        )
        == ".pdf"
    )


def get_file_type(
    filename: str,
) -> str:

    if is_pdf_file(filename):
        return "pdf"

    if is_image_file(filename):
        return "image"

    return "unknown"