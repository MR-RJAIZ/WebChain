from pathlib import Path


UPLOAD_DIR = Path("uploads")


def deploy_website():
    files = [
    file for file in UPLOAD_DIR.iterdir()
    if file.name != ".gitkeep"
    ]

    if not files:
        return {
            "status": "failed",
            "message": "No website files found"
        }

    return {
        "status": "deployed",
        "message": "Website deployment simulated successfully",
        "files": [file.name for file in files]
    }