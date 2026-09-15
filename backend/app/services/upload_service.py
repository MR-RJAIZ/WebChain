"""
Upload Service
--------------

Website files ko local filesystem par save karta hai.

Responsibilities:
- File validation (type, size, emptiness)
- Path sanitization (path traversal attacks rokna)
- Isolated deployment directories (har deployment ka apna folder)
- Directory structure preserve karna (assets/logo.png flatten nahi hogi)

Architecture:

UploadFile (FastAPI)
   ↓
validate_file_type()
   ↓
sanitize_path()
   ↓
uploads/<deployment_id>/<relative_path>
"""

import re
from pathlib import Path, PurePosixPath

from fastapi import UploadFile, HTTPException


# Base directory where all deployment folders will live.
#
# uploads/
#   <deployment_id_1>/
#     index.html
#     css/style.css
#   <deployment_id_2>/
#     index.html
#
BASE_UPLOAD_DIR = Path("uploads")


# Allowed file types for a static website.
#
# WHY restrict file types?
# Uploading executable scripts (.php, .py, .sh) to a static
# hosting platform is a security risk. We only allow static assets.

ALLOWED_EXTENSIONS = {
    ".html",
    ".htm",
    ".css",
    ".js",
    ".json",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".webp",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".otf",
    ".txt",
    ".xml",
    ".map",
}


def sanitize_relative_path(raw_filename: str) -> str:
    """
    Sanitize the filename/path received from the browser.

    WHY this is needed:
    A malicious client could send a filename like:
        ../../etc/passwd
        ../secret.txt
        C:\\Windows\\System32\\...

    We normalize to a safe relative path inside the
    deployment directory.

    Returns:
        A safe relative POSIX path string like "assets/logo.png"
        or "index.html".

    Raises:
        HTTPException 400 if the path cannot be made safe.
    """

    if not raw_filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    # Normalize to forward slashes (handles Windows paths from browser).
    normalized = raw_filename.replace("\\", "/")

    # Remove any leading slashes or drive letters (C:/).
    normalized = re.sub(r"^[a-zA-Z]:/", "", normalized)
    normalized = normalized.lstrip("/")

    # Use PurePosixPath to safely resolve the path.
    # This handles ".." components.
    try:
        safe_path = PurePosixPath(normalized)

        # Resolve all ".." by converting to string and re-parsing.
        # If any part is "..", reject the upload.
        parts = safe_path.parts

        clean_parts = []

        for part in parts:

            if part in (".", ".."):
                # Skip "." and refuse ".."
                if part == "..":
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Invalid path: path traversal "
                            f"detected in '{raw_filename}'"
                        ),
                    )
            else:
                clean_parts.append(part)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid filename: {raw_filename}",
        ) from exc

    if not clean_parts:
        raise HTTPException(
            status_code=400,
            detail="Filename resolved to empty path",
        )

    # Rebuild the safe relative path.
    # Example: ["assets", "logo.png"] → "assets/logo.png"
    relative_path = "/".join(clean_parts)

    return relative_path


async def save_upload(
    file: UploadFile,
    deployment_id: str,
) -> Path:
    """
    Save one uploaded website file into an isolated deployment directory.

    Each deployment gets its own folder:
        uploads/<deployment_id>/index.html
        uploads/<deployment_id>/css/style.css
        uploads/<deployment_id>/assets/logo.png

    This prevents deployments from overwriting each other.

    Args:
        file:
            The uploaded file from FastAPI.

        deployment_id:
            Unique ID for this deployment (UUID-based).

    Returns:
        Path to the saved file on disk.

    Raises:
        HTTPException 400 for invalid files.
    """

    # =========================================================
    # STEP 1: VALIDATE AND SANITIZE PATH
    # =========================================================

    # The browser sends the relative path in file.filename.
    # Example: "assets/logo.png" or just "index.html".
    raw_name = file.filename or ""

    safe_relative = sanitize_relative_path(raw_name)

    # =========================================================
    # STEP 2: VALIDATE FILE EXTENSION
    # =========================================================

    # Get the extension from the FINAL part of the path.
    # "assets/logo.png" → ".png"
    extension = Path(safe_relative).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: '{extension}'. "
                f"Only static website files are allowed."
            ),
        )

    # =========================================================
    # STEP 3: BUILD ISOLATED DESTINATION PATH
    # =========================================================

    # Destination: uploads/<deployment_id>/<relative_path>
    deployment_dir = BASE_UPLOAD_DIR / deployment_id
    dest_path = deployment_dir / safe_relative

    # Create parent directories (e.g. uploads/<id>/assets/)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # =========================================================
    # STEP 4: READ AND VALIDATE CONTENT
    # =========================================================

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail=f"File is empty: {safe_relative}",
        )

    # =========================================================
    # STEP 5: WRITE FILE
    # =========================================================

    dest_path.write_bytes(content)

    return dest_path