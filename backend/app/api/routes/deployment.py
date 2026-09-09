"""
Deployment Route
----------------

Ye route IPFS se mile CID ko blockchain par register karta hai.

Important:

IPFS upload aur blockchain registration
do separate responsibilities hain.

Flow:

Website
   ↓
/upload
   ↓
IPFS
   ↓
CID
   ↓
/deployment
   ↓
BlockchainService
   ↓
WebsiteRegistry.sol
   ↓
Website ID
"""


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.blockchain_service import blockchain_service


router = APIRouter()


# =============================================================
# REQUEST MODEL
# =============================================================

class DeploymentRequest(BaseModel):
    """
    Blockchain registration ke liye required data.

    name:
        Website ka human-readable name.

    cid:
        IPFS root CID.
    """

    name: str
    cid: str


# =============================================================
# DEPLOY WEBSITE
# =============================================================

@router.post("/deploy")
async def deploy_website(
    data: DeploymentRequest
):
    """
    IPFS CID ko WebsiteRegistry smart contract par register karta hai.

    Expected request:

        {
            "name": "WebChain Test Website",
            "cid": "Qm..."
        }

    Flow:

        Frontend
            ↓
        FastAPI
            ↓
        BlockchainService
            ↓
        Web3.py
            ↓
        WebsiteRegistry.sol
            ↓
        Blockchain
    """

    # =========================================================
    # 1. VALIDATE WEBSITE NAME
    # =========================================================

    if not data.name.strip():

        raise HTTPException(
            status_code=400,
            detail="Website name is required"
        )

    # =========================================================
    # 2. VALIDATE CID
    # =========================================================

    if not data.cid.strip():

        raise HTTPException(
            status_code=400,
            detail="CID is required"
        )

    # =========================================================
    # 3. REGISTER WEBSITE ON BLOCKCHAIN
    # =========================================================

    try:

        result = blockchain_service.register_website(
            name=data.name,
            cid=data.cid,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Blockchain registration failed: {str(e)}"
        )
    # =========================================================
    # 4. RESPONSE
    # =========================================================

    return {
        "message": "Website deployed successfully",

        "website_id": result["website_id"],

        "name": data.name,

        "cid": data.cid,

        "transaction_hash": result["transaction_hash"],
    }