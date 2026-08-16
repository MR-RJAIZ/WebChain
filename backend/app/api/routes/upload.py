from fastapi import APIRouter, UploadFile, File
from app.services.upload_service import save_upload
from app.models.upload import UploadResponse

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    saved_file = await save_upload(file)

    return {
        "filename": file.filename,
        "message": "File uploaded successfully",
        "path": str(saved_file)
    }