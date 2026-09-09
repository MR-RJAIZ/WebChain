from pathlib import Path
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = Path("uploads")

ALLOWED_EXTENSIONS = {
    ".html",
    ".css",
    ".js",
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
}


async def save_upload(file: UploadFile) -> Path:
    """
    Save one uploaded website file locally.

    IPFS upload is NOT handled here.

    Responsibility:
        UploadFile -> local uploads directory
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    filename = Path(file.filename).name
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}",
        )

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = UPLOAD_DIR / filename

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail=f"File is empty: {filename}",
        )

    file_path.write_bytes(content)

    return file_path