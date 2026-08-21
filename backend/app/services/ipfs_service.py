from pathlib import Path


def upload_to_ipfs(deployment_dir: Path) -> str | None:
    """
    Integration hook for Ritik's IPFS implementation.

    Expected future behavior:
    - Upload the deployment directory to IPFS/Kubo
    - Return the generated CID

    For now, no IPFS logic is implemented here.
    """
    return None