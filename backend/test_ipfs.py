import asyncio

from app.services.ipfs_service import ipfs_service


async def main():

    # ---------------------------------------------------------
    # STEP 1: Check Kubo
    # ---------------------------------------------------------

    is_connected = await ipfs_service.health_check()

    print("IPFS connected:", is_connected)

    if not is_connected:
        print("Kubo is not running.")
        return

    # ---------------------------------------------------------
    # STEP 2: Upload complete website
    # ---------------------------------------------------------

    website_path = "../ipfs-test-site"

    root_cid = await ipfs_service.upload_directory(
        website_path
    )

    # ---------------------------------------------------------
    # STEP 3: Display Root CID
    # ---------------------------------------------------------

    print()
    print("===================================")
    print("Website uploaded successfully!")
    print("Root CID:", root_cid)
    print("===================================")


if __name__ == "__main__":
    asyncio.run(main())