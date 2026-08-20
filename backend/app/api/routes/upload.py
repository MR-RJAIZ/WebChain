from typing import Annotated

from fastapi import APIRouter, File
from fastapi import UploadFile as FastAPIUploadFile
from pydantic import WithJsonSchema

from app.services.upload_service import (
    UPLOAD_DIR,
    save_uploads,
    save_zip_upload,
)


router = APIRouter()


UploadFile = Annotated[
    FastAPIUploadFile,
    WithJsonSchema({
        "type": "string",
        "format": "binary"
    })
]


@router.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...)
):
    saved_files = await save_uploads(files)

    return {
        "message": "Files uploaded successfully",
        "files": [
            path.relative_to(UPLOAD_DIR).as_posix()
            for path in saved_files
        ]
    }


@router.post("/upload/zip")
async def upload_zip(
    file: UploadFile = File(...)
):
    saved_files = await save_zip_upload(file)

    return {
        "message": "Website ZIP uploaded successfully",
        "files": [
            path.relative_to(UPLOAD_DIR.resolve()).as_posix()
            for path in saved_files
        ]
    }