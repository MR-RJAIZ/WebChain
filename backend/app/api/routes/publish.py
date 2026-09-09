from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.upload_service import save_upload
from app.services.ipfs_service import ipfs_service
from app.services.blockchain_service import blockchain_service


router = APIRouter()


@router.post("/publish")
async def publish_website(
    name: str = Form(...),
    files: list[UploadFile] = File(...),
):
    """
    Complete WebChain publishing flow.

    Website files
        ↓
    FastAPI
        ↓
    IPFS
        ↓
    Root CID
        ↓
    Blockchain
        ↓
    Website ID
        ↓
    Gateway URL
    """

    # =====================================================
    # STEP 1: VALIDATE WEBSITE NAME
    # =====================================================

    if not name.strip():
        raise HTTPException(
            status_code=400,
            detail="Website name is required",
        )

    if not files:
        raise HTTPException(
            status_code=400,
            detail="At least one website file is required",
        )

    try:

        # =================================================
        # STEP 2: SAVE UPLOADED FILES
        # =================================================

        uploaded_files = []

        for file in files:

            saved_file = await save_upload(file)

            uploaded_files.append(
                saved_file.name
            )

        # =================================================
        # STEP 3: UPLOAD WEBSITE TO IPFS
        # =================================================

        root_cid = await ipfs_service.upload_directory(
            "uploads"
        )

        # =================================================
        # STEP 4: REGISTER CID ON BLOCKCHAIN
        # =================================================

        blockchain_result = (
            blockchain_service.register_website(
                name=name,
                cid=root_cid,
            )
        )

        website_id = blockchain_result[
            "website_id"
        ]

        transaction_hash = blockchain_result[
            "transaction_hash"
        ]

        # =================================================
        # STEP 5: CREATE GATEWAY URL
        # =================================================

        gateway_url = (
            f"http://127.0.0.1:8080/ipfs/"
            f"{root_cid}/index.html"
        )

        # =================================================
        # STEP 6: RETURN COMPLETE RESULT
        # =================================================

        return {
            "message": "Website published successfully",

            "website_id": website_id,

            "name": name,

            "cid": root_cid,

            "transaction_hash": transaction_hash,

            "files": uploaded_files,

            "gateway_url": gateway_url,
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Website publishing failed: {str(e)}",
        )