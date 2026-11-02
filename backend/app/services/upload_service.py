<<<<<<< HEAD
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile
import shutil
import os
import stat
=======
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
>>>>>>> main

from fastapi import UploadFile, HTTPException


<<<<<<< HEAD
UPLOAD_DIR = Path("uploads")

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
    ".webp",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
}

MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_ZIP_SIZE = 20 * 1024 * 1024
MAX_EXTRACTED_SIZE = 50 * 1024 * 1024


def _remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def clear_upload_directory():
    UPLOAD_DIR.mkdir(exist_ok=True)

    for item in UPLOAD_DIR.iterdir():
        if item.name == ".gitkeep":
            continue

        if item.is_file() or item.is_symlink():
            try:
                item.unlink()
            except PermissionError:
                os.chmod(item, stat.S_IWRITE)
                item.unlink()

        elif item.is_dir():
            shutil.rmtree(
                item,
                onexc=_remove_readonly
            )


def validate_file(filename: str):
    extension = Path(filename).suffix.lower()
=======
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
>>>>>>> main

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
<<<<<<< HEAD
            detail=f"File type not allowed: {filename}"
        )


async def save_uploads(files: list[UploadFile]):
    validated_files = []

    for file in files:
        filename = Path(file.filename or "").name

        if not filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )

        validate_file(filename)

        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {filename}"
            )

        validated_files.append(
            (filename, content)
        )

    clear_upload_directory()

    saved_files = []

    for filename, content in validated_files:
        file_path = UPLOAD_DIR / filename

        file_path.write_bytes(content)

        saved_files.append(file_path)

    return saved_files


async def save_zip_upload(file: UploadFile):
    if not file.filename or Path(file.filename).suffix.lower() != ".zip":
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are allowed"
        )

    content = await file.read()

    if len(content) > MAX_ZIP_SIZE:
        raise HTTPException(
            status_code=413,
            detail="ZIP file is too large"
        )

    try:
        with ZipFile(BytesIO(content)) as archive:
            members = [
                member
                for member in archive.infolist()
                if not member.is_dir()
            ]

            if not members:
                raise HTTPException(
                    status_code=400,
                    detail="ZIP file is empty"
                )

            total_extracted_size = sum(
                member.file_size
                for member in members
            )

            if total_extracted_size > MAX_EXTRACTED_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="Extracted ZIP contents are too large"
                )

            upload_root = UPLOAD_DIR.resolve()
            validated_files = []

            for member in members:
                validate_file(member.filename)

                destination = (
                    UPLOAD_DIR / member.filename
                ).resolve()

                try:
                    destination.relative_to(upload_root)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="Unsafe path found in ZIP file"
                    )

                validated_files.append(
                    (member, destination)
                )

            has_index = any(
                Path(member.filename).as_posix() == "index.html"
                for member, _ in validated_files
            )

            if not has_index:
                raise HTTPException(
                    status_code=400,
                    detail="ZIP must contain index.html at the root"
                )

            clear_upload_directory()

            saved_files = []

            for member, destination in validated_files:
                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                with archive.open(member) as source:
                    with open(destination, "wb") as target:
                        shutil.copyfileobj(source, target)

                saved_files.append(destination)

            return saved_files

    except BadZipFile:
        raise HTTPException(
            status_code=400,
            detail="Invalid ZIP file"
        )
=======
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
>>>>>>> main
