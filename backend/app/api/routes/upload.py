from fastapi import APIRouter, UploadFile, File
from app.services.upload_service import save_upload

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    saved_file = await save_upload(file)

    return {
        "filename": file.filename,
        "message": "File uploaded successfully",
        "path": str(saved_file)
    }