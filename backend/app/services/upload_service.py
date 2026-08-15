from pathlib import Path
from fastapi import UploadFile, HTTPException


UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".html", ".css", ".js"}


async def save_upload(file: UploadFile):
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only HTML, CSS, and JS files are allowed"
        )

    UPLOAD_DIR.mkdir(exist_ok=True)

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path