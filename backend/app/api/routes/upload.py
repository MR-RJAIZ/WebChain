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


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_files(
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
    }