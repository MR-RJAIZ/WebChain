"""
Blockchain Service
------------------

This service is responsible ONLY for communicating with
the WebsiteRegistry smart contract.

Architecture:

FastAPI
   ↓
BlockchainService
   ↓
Web3.py
   ↓
Ethereum-compatible blockchain
   ↓
WebsiteRegistry.sol
"""

import json
from pathlib import Path

from web3 import Web3

from app.config import settings


class BlockchainService:
    """
    Service responsible for interacting with
    WebsiteRegistry smart contract.

    IPFSService:
        Website → IPFS → CID

    BlockchainService:
        CID → Blockchain
    """

    def __init__(
        self,
        rpc_url: str | None = None,
        contract_address: str | None = None,
    ):
        # =====================================================
        # STEP 1: RPC CONNECTION
        # =====================================================

        self.rpc_url = rpc_url or settings.rpc_url

        self.web3 = Web3(
            Web3.HTTPProvider(self.rpc_url)
        )

        if not self.web3.is_connected():
            raise ConnectionError(
                f"Could not connect to blockchain RPC: {self.rpc_url}"
            )

        # =====================================================
        # STEP 2: CONTRACT ADDRESS
        # =====================================================

        self.contract_address = contract_address or settings.contract_address

        if not self.contract_address:
            raise ValueError(
                "Contract address is not configured."
            )

        self.contract_address = Web3.to_checksum_address(
            self.contract_address
        )

        # =====================================================
        # STEP 3: CHECK CONTRACT DEPLOYMENT
        # =====================================================

        contract_code = self.web3.eth.get_code(
            self.contract_address
        )

        if not contract_code:
            raise ConnectionError(
                f"No smart contract deployed at "
                f"{self.contract_address}"
            )

        # =====================================================
        # STEP 4: LOAD CONTRACT ABI
        # =====================================================

        # Project root:
        #
        # WebChain/
        # ├── artifacts/
        # ├── backend/
        # │   └── app/
        #
        # __file__:
        # backend/app/services/blockchain_service.py
        #
        # parents[3] → WebChain/

        project_root = Path(__file__).resolve().parents[3]

        artifact_path = (
            project_root
            / "artifacts"
            / "contracts"
            / "WebsiteRegistry.sol"
            / "WebsiteRegistry.json"
        )

        if not artifact_path.exists():
            raise FileNotFoundError(
                f"Contract artifact not found: {artifact_path}"
            )

        with artifact_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            artifact = json.load(file)

        # =====================================================
        # STEP 5: CREATE CONTRACT INSTANCE
        # =====================================================

        self.contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=artifact["abi"],
        )

    # =========================================================
    # HEALTH CHECK
    # =========================================================

    def health_check(self) -> bool:
        """
        Check whether blockchain node is reachable.
        """

        return self.web3.is_connected()

    # =========================================================
    # REGISTER WEBSITE
    # =========================================================

    def register_website(
        self,
        name: str,
        cid: str,
    ) -> dict:
        """
        Register a website on the blockchain.

        Input:
            name:
                Website name.

            cid:
                Root CID returned by IPFS.

        Flow:

            Website
                ↓
            IPFS
                ↓
            CID
                ↓
            registerWebsite()
                ↓
            Blockchain
        """

        # =====================================================
        # STEP 1: VALIDATE INPUT
        # =====================================================

        if not name.strip():
            raise ValueError(
                "Website name cannot be empty"
            )

        if not cid.strip():
            raise ValueError(
                "CID cannot be empty"
            )

        # =====================================================
        # STEP 2: GET PRIVATE KEY
        # =====================================================

        private_key = settings.private_key

        if not private_key:
            raise ValueError(
                "PRIVATE_KEY is not configured."
            )

        # =====================================================
        # STEP 3: GET WALLET
        # =====================================================

        account = self.web3.eth.account.from_key(
            private_key
        )

        wallet_address = account.address

        # =====================================================
        # STEP 4: GET NONCE
        # =====================================================

        nonce = self.web3.eth.get_transaction_count(
            wallet_address,
            "pending",
        )

        # =====================================================
        # STEP 5: BUILD TRANSACTION
        # =====================================================

        transaction = (
            self.contract.functions
            .registerWebsite(
                name,
                cid,
            )
            .build_transaction(
                {
                    "from": wallet_address,
                    "nonce": nonce,
                    "gas": 500000,
                    "gasPrice": self.web3.eth.gas_price,
                }
            )
        )

        # =====================================================
        # STEP 6: SIGN TRANSACTION
        # =====================================================

        signed_transaction = (
            self.web3.eth.account.sign_transaction(
                transaction,
                private_key=private_key,
            )
        )

        # =====================================================
        # STEP 7: SEND TRANSACTION
        # =====================================================

        transaction_hash = (
            self.web3.eth.send_raw_transaction(
                signed_transaction.raw_transaction
            )
        )

        # =====================================================
        # STEP 8: WAIT FOR CONFIRMATION
        # =====================================================

        receipt = (
            self.web3.eth.wait_for_transaction_receipt(
                transaction_hash
            )
        )

        # =====================================================
        # STEP 9: CHECK TRANSACTION STATUS
        # =====================================================

        if receipt["status"] != 1:
            raise RuntimeError(
                "Blockchain transaction failed."
            )

        # =====================================================
        # STEP 10: READ WEBSITE REGISTERED EVENT
        # =====================================================

        events = (
            self.contract
            .events
            .WebsiteRegistered()
            .process_receipt(receipt)
        )

        if not events:
            raise RuntimeError(
                "WebsiteRegistered event not found."
            )

        website_id = events[0]["args"]["websiteId"]

        # =====================================================
        # STEP 11: RETURN RESULT
        # =====================================================

        return {
            "website_id": int(website_id),
            "transaction_hash": transaction_hash.hex(),
        }

    # =========================================================
    # GET WEBSITE
    # =========================================================

    def get_website(
        self,
        website_id: int,
    ) -> dict:
        """
        Read website information from blockchain.

        This is a READ operation.

        No:
            - transaction
            - gas
            - private key

        is required.
        """

        website = (
            self.contract
            .functions
            .getWebsite(website_id)
            .call()
        )

        return {
            "id": int(website[0]),
            "name": website[1],
            "cid": website[2],
            "owner": website[3],
            "timestamp": int(website[4]),
        }

    # =========================================================
    # VERIFY WEBSITE
    # =========================================================

    def verify_website(
        self,
        website_id: int,
        cid: str,
    ) -> bool:
        """
        Verify whether the provided CID matches
        the CID stored on the blockchain.
        """

        return self.contract.functions.verifyWebsite(
            website_id,
            cid,
        ).call()


# =============================================================
# REUSABLE SERVICE INSTANCE
# =============================================================

blockchain_service = BlockchainService()