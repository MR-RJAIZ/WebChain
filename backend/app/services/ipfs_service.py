
"""
IPFS Service
------------
This file contains all communication between our FastAPI backend
and the local Kubo IPFS node.

Architecture:

FastAPI
   ↓
IPFSService
   ↓
Kubo HTTP API
   ↓
IPFS Network
   ↓
CID
"""

from pathlib import Path
from typing import Union

# Hum Python se Kubo ke HTTP API ko call karenge.
import requests


class IPFSService:
    """
    Service responsible for communicating with Kubo.

    Important:
    This class does NOT contain blockchain logic.
    Its only responsibility is IPFS.
    """

    def __init__(self, api_url: str = "http://127.0.0.1:5001"):
        """
        Kubo exposes an HTTP API.

        Default Kubo API:
            http://127.0.0.1:5001

        We store the API URL so every IPFS operation
        can use the same Kubo node.
        """

        self.api_url = api_url.rstrip("/")

        # Kubo's API endpoint for adding files.
        self.add_url = f"{self.api_url}/api/v0/add"

    def health_check(self) -> bool:
        """
        Check whether the Kubo node is reachable.

        Returns:
            True  -> Kubo is running
            False -> Kubo is not reachable
        """

        try:
            response = requests.post(
                f"{self.api_url}/api/v0/id",
                timeout=5,
            )

            return response.ok

        except requests.RequestException:
            return False

    def upload_file(self, file_path: Union[str, Path]) -> str:
        """
        Upload a single file to IPFS.

        Example:

            index.html
                ↓
              Kubo
                ↓
              CID

        Returns:
            CID of the uploaded file.
        """

        file_path = Path(file_path)

        # Make sure the file actually exists
        # before sending it to Kubo.
        if not file_path.is_file():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        # Open the file in binary mode because
        # websites can contain images, fonts, PDFs, etc.
        with file_path.open("rb") as file:

            response = requests.post(
                self.add_url,
                files={
                    "file": (
                        file_path.name,
                        file,
                    )
                },
                timeout=60,
            )

        # If Kubo returned an error, raise an exception.
        response.raise_for_status()

        # Kubo returns JSON containing information
        # about the uploaded object.
        data = response.json()

        # "Hash" is the CID returned by Kubo.
        cid = data["Hash"]

        return cid

    def get_file(self, cid: str) -> bytes:
        """
        Retrieve file content from IPFS using its CID.

        Example:

            CID
             ↓
            Kubo
             ↓
          file data

        This method is useful later for verification/testing.
        """

        response = requests.post(
            f"{self.api_url}/api/v0/cat",
            params={"arg": cid},
            timeout=60,
        )

        response.raise_for_status()

        return response.content


# Create one reusable IPFS service instance.

ipfs_service = IPFSService()

