"""
Website Routes
--------------

Existing website data ko blockchain se read karta hai
aur CID update karne ki functionality provide karta hai.

Routes:

GET  /website/{website_id}         → website metadata
GET  /website/{website_id}/verify  → CID verification
PUT  /website/{website_id}         → update CID (owner only)
"""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.blockchain_service import blockchain_service
from app.services.ipfs_service import ipfs_service
from app.services.upload_service import save_upload


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================
# GET WEBSITE METADATA
# =============================================================

@router.get("/website/{website_id}")
async def get_website(website_id: int):
    """
    Retrieve website metadata from the blockchain.

    This is a read-only call — no transaction needed.

    Response:
        {
            "website_id": 1,
            "name": "My Website",
            "cid": "QmXxx...",
            "owner": "0x...",
            "timestamp": 1234567890,
            "gateway_url": "http://127.0.0.1:8080/ipfs/QmXxx/"
        }
    """

    try:
        website = blockchain_service.get_website(website_id)

    except ConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Blockchain unavailable: {str(exc)}",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch website: {str(exc)}",
        )

    # website_id == 0 means the contract returned an empty record
    # (Solidity mapping returns zero-value struct for missing keys).
    if website["id"] == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Website with ID {website_id} not found",
        )

    gateway_url = (
        f"http://127.0.0.1:8080/ipfs/{website['cid']}/"
    )

    return {
        "website_id": website["id"],
        "name":       website["name"],
        "cid":        website["cid"],
        "owner":      website["owner"],
        "timestamp":  website["timestamp"],
        "gateway_url": gateway_url,
    }


# =============================================================
# VERIFY CID AGAINST BLOCKCHAIN
# =============================================================

@router.get("/website/{website_id}/verify")
async def verify_website(website_id: int, cid: str):
    """
    Verify whether a given CID matches what's stored on-chain.

    Use case:
        User has a CID and wants to confirm it hasn't been tampered.

    Query param:
        cid — the CID to verify

    Response:
        {
            "website_id": 1,
            "provided_cid": "QmXxx...",
            "verified": true
        }

    'verified': true  → provided CID matches on-chain CID
    'verified': false → CIDs don't match (content may differ)
    """

    if not cid or not cid.strip():
        raise HTTPException(
            status_code=400,
            detail="'cid' query parameter is required",
        )

    try:
        verified = blockchain_service.verify_website(
            website_id,
            cid.strip(),
        )

    except ConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Blockchain unavailable: {str(exc)}",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(exc)}",
        )

    return {
        "website_id":    website_id,
        "provided_cid":  cid.strip(),
        "verified":      verified,
    }


# =============================================================
# UPDATE WEBSITE (OWNER ONLY)
# =============================================================

@router.put("/website/{website_id}")
async def update_website(
    website_id: int,
    name: str = Form(..., description="Website name (unchanged)"),
    files: list[UploadFile] = File(
        ...,
        description="New version of all website files",
    ),
):
    """
    Upload a new version of the website and update the CID on-chain.

    This triggers the SAME flow as /publish but calls
    updateWebsite() on the contract instead of registerWebsite().

    IMPORTANT SECURITY:
    The smart contract enforces owner-only updates.
    The backend wallet signs the transaction. If the backend wallet
    is NOT the owner of website_id, the transaction will revert.

    Flow:
        new files
           ↓
        new isolated deployment directory
           ↓
        IPFS upload → new CID
           ↓
        blockchain_service.update_website(website_id, new_cid)
           ↓
        WebsiteRegistry.updateWebsite() → reverts if not owner
           ↓
        return { website_id, new_cid, gateway_url, ... }

    Response:
        {
            "message": "Website updated successfully",
            "website_id": 1,
            "name": "My Website",
            "new_cid": "QmYyy...",
            "old_cid": "QmXxx...",
            "gateway_url": "http://127.0.0.1:8080/ipfs/QmYyy/",
            "transaction_hash": "0x..."
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
            detail="At least one file is required for the update",
        )

    # =========================================================
    # STEP 1: GET CURRENT CID (to return as 'old_cid')
    # =========================================================

    try:
        current = blockchain_service.get_website(website_id)
    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch current website: {str(exc)}",
        )

    if current["id"] == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Website with ID {website_id} not found",
        )

    old_cid = current["cid"]

    # =========================================================
    # STEP 2: CREATE NEW ISOLATED DIRECTORY
    # =========================================================

    deployment_id = str(uuid.uuid4())

    logger.info(
        "Starting update: website_id=%d deployment_id=%s",
        website_id,
        deployment_id,
    )

    # =========================================================
    # STEP 3: SAVE NEW FILES
    # =========================================================

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
        logger.exception("File save failed during update %s", deployment_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save files: {str(exc)}",
        )

    # =========================================================
    # STEP 4: UPLOAD NEW VERSION TO IPFS
    # =========================================================

    deployment_dir = Path("uploads") / deployment_id

    try:
        new_cid = await ipfs_service.upload_directory(deployment_dir)

    except Exception as exc:
        logger.exception("IPFS upload failed for update %s", deployment_id)
        raise HTTPException(
            status_code=503,
            detail=f"IPFS upload failed: {str(exc)}",
        )

    logger.info(
        "IPFS upload for update: website_id=%d new_cid=%s",
        website_id,
        new_cid,
    )

    # =========================================================
    # STEP 5: UPDATE CID ON BLOCKCHAIN
    # =========================================================

    try:
        blockchain_result = blockchain_service.update_website(
            website_id=website_id,
            new_cid=new_cid,
        )

    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    except RuntimeError as exc:
        # Likely "Not website owner" revert from the contract.
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except Exception as exc:
        logger.exception(
            "Blockchain update failed for website_id=%d", website_id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Blockchain update failed: {str(exc)}",
        )

    transaction_hash = blockchain_result["transaction_hash"]

    logger.info(
        "Website updated on-chain: website_id=%d tx=%s",
        website_id,
        transaction_hash,
    )

    # =========================================================
    # STEP 6: RETURN RESULT
    # =========================================================

    gateway_url = f"http://127.0.0.1:8080/ipfs/{new_cid}/"

    return {
        "message":         "Website updated successfully",
        "website_id":      website_id,
        "name":            name.strip(),
        "new_cid":         new_cid,
        "old_cid":         old_cid,
        "files_saved":     files_saved,
        "gateway_url":     gateway_url,
        "transaction_hash": transaction_hash,
        "status":          "updated",
    }