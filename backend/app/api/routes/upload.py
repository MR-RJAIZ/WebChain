from typing import Annotated

from fastapi import APIRouter, File
from fastapi import UploadFile as FastAPIUploadFile
from pydantic import WithJsonSchema

from app.services.upload_service import save_uploads

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
            {
                "filename": path.name,
                "path": str(path)
            }
            for path in saved_files
        ]
    }