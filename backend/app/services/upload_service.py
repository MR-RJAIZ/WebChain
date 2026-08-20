from pathlib import Path
import shutil

from fastapi import UploadFile, HTTPException

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".html", ".css", ".js"}


async def save_uploads(files: list[UploadFile]):
    # Validate every file before changing the upload folder
    for file in files:
        filename = Path(file.filename).name
        extension = Path(filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Only HTML, CSS, and JS files are allowed"
            )

    UPLOAD_DIR.mkdir(exist_ok=True)

    # Remove files from the previous upload batch
    for item in UPLOAD_DIR.iterdir():
        if item.name == ".gitkeep":
            continue

        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    saved_files = []

    # Save the new batch
    for file in files:
        filename = Path(file.filename).name
        file_path = UPLOAD_DIR / filename

        content = await file.read()

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        saved_files.append(file_path)

    return saved_files