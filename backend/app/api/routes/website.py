from fastapi import APIRouter, HTTPException

from app.services.blockchain_service import blockchain_service
from app.services.ipfs_service import ipfs_service

router = APIRouter()


@router.get("/website/{website_id}")
async def get_website(website_id: int):
    try:
        website = blockchain_service.get_website(website_id)

        if website["id"] == 0:
            raise HTTPException(
                status_code=404,
                detail="Website not found"
            )

        return {
            "website_id": website["id"],
            "name": website["name"],
            "cid": website["cid"],
            "owner": website["owner"],
            "timestamp": website["timestamp"],
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch website: {str(e)}"
        )


@router.get("/website/{website_id}/verify")
async def verify_website(website_id: int, cid: str):
    try:
        result = blockchain_service.verify_website(
            website_id,
            cid
        )

        return {
            "website_id": website_id,
            "provided_cid": cid,
            "verified": result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(e)}"
        )


@router.get("/website/{website_id}/content")
async def get_website_content(website_id: int):
    try:
        website = blockchain_service.get_website(website_id)

        if website["id"] == 0:
            raise HTTPException(
                status_code=404,
                detail="Website not found"
            )

        cid = website["cid"]

        content = await ipfs_service.get_file(
            f"{cid}/index.html"
        )

        return {
            "website_id": website_id,
            "name": website["name"],
            "cid": cid,
            "content": content.decode("utf-8"),
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve website: {str(e)}"
        )