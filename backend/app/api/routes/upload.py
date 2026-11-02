<<<<<<< HEAD
from typing import Annotated

from fastapi import APIRouter, File
from fastapi import UploadFile as FastAPIUploadFile
from pydantic import WithJsonSchema

from app.services.upload_service import (
    UPLOAD_DIR,
    save_uploads,
    save_zip_upload,
)

=======
"""
Upload Route (File-Only)
------------------------

Ye route sirf files receive karke save karta hai.
IPFS aur blockchain ka kaam yahan nahi hota.

WHY keep this separate from /publish?
- Testing: Files ko independently upload karke verify karo.
- Future: Two-step workflows jahan IPFS/blockchain baad mein hona ho.

For the complete deployment flow, use POST /publish instead.

Flow:

POST /upload
   ↓
Save files to isolated directory
   ↓
Return { deployment_id, files_saved }

The returned deployment_id can then be used to
track which files were uploaded.
"""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.upload_service import save_upload
>>>>>>> main


logger = logging.getLogger(__name__)

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
<<<<<<< HEAD
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
=======
    name: str = Form(..., description="Website name"),
    files: list[UploadFile] = File(
        ...,
        description="Website files to upload",
    ),
):
    """
    Upload website files and save them to an isolated directory.

    Does NOT upload to IPFS or register on blockchain.
    Use POST /publish for the complete deployment flow.

    Request (multipart/form-data):
        name:  "My Website"
        files: [index.html, style.css, ...]

    Response:
        {
            "message": "Files uploaded successfully",
            "deployment_id": "uuid...",
            "name": "My Website",
            "files_saved": ["index.html", "css/style.css", ...]
        }
    """

    if not name.strip():
        raise HTTPException(
            status_code=400,
            detail="Website name is required",
        )

    if not files:
        raise HTTPException(
            status_code=400,
            detail="At least one file is required",
        )

    deployment_id = str(uuid.uuid4())

    files_saved = []

    try:
        for upload_file in files:

            saved_path = await save_upload(
                file=upload_file,
                deployment_id=deployment_id,
            )

            deployment_dir = Path("uploads") / deployment_id
            relative = str(
                saved_path.relative_to(deployment_dir)
            ).replace("\\", "/")

            files_saved.append(relative)

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("File upload failed")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(exc)}",
        )

    return {
        "message": "Files uploaded successfully",
        "deployment_id": deployment_id,
        "name": name.strip(),
        "files_saved": files_saved,
>>>>>>> main
    }