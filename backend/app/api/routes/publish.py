"""
Publish Route
-------------

This is the main WebChain deployment endpoint.

It handles the complete deployment flow in one request:

Frontend
   ↓
POST /publish  (multipart/form-data: name + files[])
   ↓
FastAPI validates input
   ↓
Create isolated deployment directory  (uploads/<uuid>/)
   ↓
Save all uploaded files (preserving directory structure)
   ↓
IPFSService.upload_directory(uploads/<uuid>/)
   ↓
Kubo returns ROOT CID
   ↓
BlockchainService.register_website(name, cid)
   ↓
WebsiteRegistry.registerWebsite() on-chain
   ↓
Website ID from event
   ↓
Return { website_id, cid, name, gateway_url, ... }
   ↓
Frontend displays results

WHY one combined endpoint:
The frontend needs a single call that returns all the
information (CID + website_id) together. Splitting into
/upload + /deploy would require the frontend to chain two
calls and manage intermediate state.
"""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.upload_service import save_upload
from app.services.ipfs_service import ipfs_service
from app.services.blockchain_service import blockchain_service


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/publish")
async def publish_website(
    name: str = Form(..., description="Human-readable website name"),
    files: list[UploadFile] = File(..., description="All website files"),
):
    """
    Deploy a complete static website to IPFS and register it on blockchain.

    Request (multipart/form-data):
        name:  "My Website"
        files: [index.html, style.css, script.js, assets/logo.png, ...]

    Response:
        {
            "message": "Website deployed successfully",
            "website_id": 1,
            "name": "My Website",
            "cid": "QmXxx...",
            "deployment_id": "uuid-string",
            "files_saved": ["index.html", "css/style.css", ...],
            "gateway_url": "http://127.0.0.1:8080/ipfs/QmXxx/index.html",
            "transaction_hash": "0x..."
        }
    """

    # =========================================================
    # STEP 1: VALIDATE INPUTS
    # =========================================================

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

    # =========================================================
    # STEP 2: CREATE ISOLATED DEPLOYMENT DIRECTORY
    # =========================================================

    # Each deployment gets a unique directory.
    # This prevents any two deployments from mixing files.
    deployment_id = str(uuid.uuid4())

    logger.info(
        "Starting deployment: id=%s name=%r files=%d",
        deployment_id,
        name,
        len(files),
    )

    # =========================================================
    # STEP 3: SAVE FILES TO ISOLATED DIRECTORY
    # =========================================================

    files_saved = []

    try:
        for upload_file in files:

            # save_upload handles:
            # - path sanitization (prevents traversal)
            # - extension validation
            # - directory creation
            # - file writing
            saved_path = await save_upload(
                file=upload_file,
                deployment_id=deployment_id,
            )

            # Store the relative path for the response.
            # e.g. "assets/logo.png" not the full absolute path.
            deployment_dir = Path("uploads") / deployment_id
            relative = str(
                saved_path.relative_to(deployment_dir)
            ).replace("\\", "/")

            files_saved.append(relative)

    except HTTPException:
        # Re-raise validation errors as-is (400 status).
        raise

    except Exception as exc:
        logger.exception("File save failed during deployment %s", deployment_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded files: {str(exc)}",
        )

    logger.info(
        "Files saved for deployment %s: %s",
        deployment_id,
        files_saved,
    )

    # =========================================================
    # STEP 4: UPLOAD WEBSITE DIRECTORY TO IPFS
    # =========================================================

    deployment_dir = Path("uploads") / deployment_id

    try:
        root_cid = await ipfs_service.upload_directory(deployment_dir)

    except Exception as exc:
        logger.exception(
            "IPFS upload failed for deployment %s", deployment_id
        )
        raise HTTPException(
            status_code=503,
            detail=(
                f"IPFS upload failed: {str(exc)}. "
                f"Is the Kubo daemon running at "
                f"http://127.0.0.1:5001 ?"
            ),
        )

    logger.info(
        "IPFS upload success for deployment %s: CID=%s",
        deployment_id,
        root_cid,
    )

    # =========================================================
    # STEP 5: REGISTER CID ON BLOCKCHAIN
    # =========================================================

    try:
        blockchain_result = blockchain_service.register_website(
            name=name.strip(),
            cid=root_cid,
        )

    except ConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Blockchain connection failed: {str(exc)}. "
                f"Is the Hardhat node running at "
                f"http://127.0.0.1:8545 ?"
            ),
        )

    except Exception as exc:
        logger.exception(
            "Blockchain registration failed for deployment %s",
            deployment_id,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Blockchain registration failed: {str(exc)}",
        )

    website_id = blockchain_result["website_id"]
    transaction_hash = blockchain_result["transaction_hash"]

    logger.info(
        "Blockchain registration success: website_id=%d tx=%s",
        website_id,
        transaction_hash,
    )

    # =========================================================
    # STEP 6: BUILD GATEWAY URL
    # =========================================================

    # The IPFS gateway allows browsers to retrieve the website
    # by CID without running an IPFS node.
    #
    # Local Kubo gateway: http://127.0.0.1:8080/ipfs/<CID>/
    #
    # WHY append index.html?
    # IPFS directories need an explicit file path.
    # Without it, the gateway serves the directory listing.
    gateway_url = f"http://127.0.0.1:8080/ipfs/{root_cid}/"

    # =========================================================
    # STEP 7: RETURN COMPLETE RESULT
    # =========================================================

    return {
        "message": "Website deployed successfully",
        "website_id": website_id,
        "name": name.strip(),
        "cid": root_cid,
        "deployment_id": deployment_id,
        "files_saved": files_saved,
        "gateway_url": gateway_url,
        "transaction_hash": transaction_hash,
        "status": "deployed",
    }