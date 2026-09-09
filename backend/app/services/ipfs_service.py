"""
IPFS Service
============

This module is responsible ONLY for communication with Kubo/IPFS.

Architecture:

    FastAPI
       |
       v
    IPFSService
       |
       v
    Kubo HTTP API
       |
       v
    IPFS
       |
       v
      CID


IMPORTANT
---------
This service does NOT contain:

- Blockchain logic
- Smart contract logic
- Database logic
- Frontend logic

Its only responsibility is interacting with IPFS/Kubo.
"""

import json
from pathlib import Path

import httpx

from app.config import settings


class IPFSService:
    """
    Service responsible for communicating with a Kubo IPFS node.

    We use asynchronous HTTP requests because our FastAPI
    application is asynchronous.
    """

    def __init__(self, api_url: str | None = None):
        """
        Initialize the IPFS service.

        The IPFS API URL comes from application settings.

        Example:

            IPFS_API_URL=http://127.0.0.1:5001
        """

        # Use the URL provided explicitly if one is given.
        # Otherwise use the value from our application settings.
        self.api_url = (
            api_url or settings.ipfs_api_url
        ).rstrip("/")

        # Kubo endpoint used to add files/directories.
        self.add_url = (
            f"{self.api_url}/api/v0/add"
        )

        # Kubo endpoint used to retrieve content.
        self.cat_url = (
            f"{self.api_url}/api/v0/cat"
        )

        # Kubo endpoint used to check node health.
        self.id_url = (
            f"{self.api_url}/api/v0/id"
        )

    # =========================================================
    # HEALTH CHECK
    # =========================================================

    async def health_check(self) -> bool:
        """
        Check whether the Kubo IPFS node is reachable.

        Returns:

            True  -> Kubo is running
            False -> Kubo is unreachable
        """

        try:
            async with httpx.AsyncClient(
                timeout=5.0
            ) as client:

                response = await client.post(
                    self.id_url
                )

                response.raise_for_status()

                return True

        except httpx.HTTPError:
            return False

    # =========================================================
    # FILE -> IPFS -> CID
    # =========================================================

    async def upload_file(
        self,
        file_path: str | Path,
    ) -> str:
        """
        Upload a single file to IPFS.

        Example:

            index.html
                |
                v
            IPFSService
                |
                v
              Kubo
                |
                v
               CID
        """

        file_path = Path(file_path)

        # Make sure the file exists.
        if not file_path.is_file():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        try:
            # Open in binary mode so this works with:
            #
            # HTML
            # CSS
            # JavaScript
            # Images
            # Fonts
            # etc.
            with file_path.open("rb") as file:

                async with httpx.AsyncClient(
                    timeout=60.0
                ) as client:

                    response = await client.post(
                        self.add_url,
                        files={
                            "file": (
                                file_path.name,
                                file,
                            )
                        },
                    )

            response.raise_for_status()

            data = response.json()

            # Kubo returns the CID in "Hash".
            cid = data.get("Hash")

            if not cid:
                raise RuntimeError(
                    "Kubo did not return a CID"
                )

            return cid

        except httpx.HTTPError as error:

            raise RuntimeError(
                f"Failed to upload file to IPFS: {error}"
            ) from error

    # =========================================================
    # DIRECTORY -> IPFS -> ROOT CID
    # =========================================================

    async def upload_directory(
        self,
        directory_path: str | Path,
    ) -> str:
        """
        Upload an entire website directory to IPFS.

        Example website:

            website/
            ├── index.html
            ├── style.css
            ├── script.js
            └── images/
                └── logo.png

        IPFS will create a directory object containing
        all these files.

        Returns:

            Root CID of the website directory.
        """

        directory_path = Path(directory_path)

        if not directory_path.is_dir():
            raise FileNotFoundError(
                f"Directory not found: {directory_path}"
            )

        file_handles = []

        try:
            # These parameters tell Kubo:
            #
            # recursive=true
            #     Process directory structure.
            #
            # wrap-with-directory=true
            #     Create a root directory object.
            params = {
                "recursive": "true",
                "wrap-with-directory": "true",
            }

            files = []

            # Recursively find every file inside
            # the website directory.
            for file_path in directory_path.rglob("*"):

                if not file_path.is_file():
                    continue

                # Preserve the website's internal structure.
                #
                # Example:
                #
                # images/logo.png
                #
                # instead of:
                #
                # C:\...\website\images\logo.png
                relative_path = file_path.relative_to(
                    directory_path
                )

                file_handle = file_path.open("rb")

                file_handles.append(file_handle)

                files.append(
                    (
                        "file",
                        (
                            str(relative_path),
                            file_handle,
                        ),
                    )
                )

            if not files:
                raise ValueError(
                    "Website directory is empty"
                )

            async with httpx.AsyncClient(
                timeout=120.0
            ) as client:

                response = await client.post(
                    self.add_url,
                    params=params,
                    files=files,
                )

            response.raise_for_status()

            # Kubo returns multiple JSON objects,
            # one for each uploaded file.
            #
            # The LAST object represents the root
            # directory when wrap-with-directory=true.
            results = [
                line
                for line in response.text.splitlines()
                if line.strip()
            ]

            if not results:
                raise RuntimeError(
                    "Kubo returned an empty response"
                )

            root_data = json.loads(
                results[-1]
            )

            root_cid = root_data.get("Hash")

            if not root_cid:
                raise RuntimeError(
                    "Kubo did not return a root CID"
                )

            return root_cid

        except httpx.HTTPError as error:

            raise RuntimeError(
                f"Failed to upload directory to IPFS: {error}"
            ) from error

        finally:

            # Always close all opened files.
            for file_handle in file_handles:
                file_handle.close()

    # =========================================================
    # CID -> IPFS -> CONTENT
    # =========================================================

    async def get_file(
        self,
        cid: str,
    ) -> bytes:
        """
        Retrieve content from IPFS using a CID.

        Returns raw bytes.

        This allows us to retrieve:

        - HTML
        - CSS
        - JavaScript
        - Images
        - PDFs
        - etc.
        """

        if not cid or not cid.strip():
            raise ValueError(
                "CID cannot be empty"
            )

        try:
            async with httpx.AsyncClient(
                timeout=60.0
            ) as client:

                response = await client.post(
                    self.cat_url,
                    params={
                        "arg": cid
                    },
                )

            response.raise_for_status()

            return response.content

        except httpx.HTTPError as error:

            raise RuntimeError(
                f"Failed to retrieve content from IPFS: {error}"
            ) from error


# =============================================================
# REUSABLE SERVICE INSTANCE
# =============================================================

# Create one reusable IPFS service instance.
#
# Other backend modules can import it:
#
# from app.services.ipfs_service import ipfs_service
#
# Then:
#
# await ipfs_service.health_check()
# await ipfs_service.upload_file(...)
# await ipfs_service.upload_directory(...)
# await ipfs_service.get_file(...)

ipfs_service = IPFSService()