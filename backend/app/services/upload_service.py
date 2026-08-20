from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile
import shutil

from fastapi import UploadFile, HTTPException


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


def clear_upload_directory():
    UPLOAD_DIR.mkdir(exist_ok=True)

    for item in UPLOAD_DIR.iterdir():
        if item.name == ".gitkeep":
            continue

        if item.is_file() or item.is_symlink():
            item.unlink()

        elif item.is_dir():
            shutil.rmtree(item)


def validate_file(filename: str):
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed: {filename}"
        )


async def save_uploads(files: list[UploadFile]):
    # Validate everything before deleting the previous upload
    for file in files:
        filename = Path(file.filename or "").name

        if not filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )

        validate_file(filename)

    clear_upload_directory()

    saved_files = []

    for file in files:
        filename = Path(file.filename).name
        file_path = UPLOAD_DIR / filename

        content = await file.read()
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

            # WebChain requires index.html at website root
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