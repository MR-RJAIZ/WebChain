"""
Health Check Route
------------------

Ye endpoint confirm karta hai ki:
1. FastAPI backend is running
2. Kubo/IPFS node is reachable
3. Hardhat/blockchain node is reachable

Frontend is status ka use karke user ko
service health dikhata hai.
"""

from fastapi import APIRouter

from app.services.ipfs_service import ipfs_service
from app.services.blockchain_service import blockchain_service


router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Check the health of all WebChain services.

    Returns:
        {
            "api": true,
            "ipfs": true,
            "blockchain": true
        }

    All values are booleans:
        true  → service is reachable and responding
        false → service is down or unreachable
    """

    # Check IPFS/Kubo connectivity.
    # This hits POST /api/v0/id on the Kubo node.
    ipfs_ok = await ipfs_service.health_check()

    # Check blockchain/Hardhat connectivity.
    # This checks Web3 is_connected().
    blockchain_ok = blockchain_service.health_check()

    return {
        "api": True,
        "ipfs": ipfs_ok,
        "blockchain": blockchain_ok,
    }