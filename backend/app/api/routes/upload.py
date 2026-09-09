"""
Upload Route
------------

Ye route website files receive karta hai aur
IPFS par upload karta hai.

Flow:

Client
   ↓
POST /upload
   ↓
FastAPI
   ↓
Save files locally
   ↓
IPFSService
   ↓
Kubo
   ↓
Root CID
"""

from fastapi import APIRouter, UploadFile, File

from app.services.upload_service import save_upload
from app.services.ipfs_service import ipfs_service


router = APIRouter()


@router.post("/upload")
async def upload_file(
    files: list[UploadFile] = File(...)
):
    """
    Multiple website files upload karta hai.

    Example:

        index.html
        style.css
        script.js

    Ye files pehle temporary local storage mein save hoti hain,
    phir complete directory IPFS par upload hoti hai.

    Returns:
        Root CID of the uploaded website.
    """

    # Uploaded files ke names store karne ke liye.
    uploaded_files = []

    # =========================================================
    # 1. SAVE FILES LOCALLY
    # =========================================================

    for file in files:

        saved_file = await save_upload(file)

        uploaded_files.append(
            saved_file.name
        )

    # =========================================================
    # 2. UPLOAD COMPLETE WEBSITE TO IPFS
    # =========================================================

    # Complete uploads directory ko IPFS par upload karo.
    #
    # IPFSService sirf IPFS responsibility handle karta hai.
    # Blockchain ka kaam yahan nahi hona chahiye.

    root_cid = await ipfs_service.upload_directory(
        "uploads"
    )

    # =========================================================
    # 3. RESPONSE
    # =========================================================

    return {
        "message": "Website uploaded successfully",
        "files": uploaded_files,
        "root_cid": root_cid,
    }