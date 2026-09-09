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
import os
from pathlib import Path

from web3 import Web3


class BlockchainService:
    """
    Service responsible for interacting with
    WebsiteRegistry smart contract.

    IMPORTANT:

    IPFSService handles:
        Website → IPFS → CID

    BlockchainService handles:
        CID → Blockchain

    We keep these responsibilities separate because
    this makes our backend architecture cleaner.
    """

    def __init__(
        self,
        rpc_url: str = "http://127.0.0.1:8545",
        contract_address: str | None = None,
    ):

        # -----------------------------------------------------
        # STEP 1: Connect to blockchain node
        # -----------------------------------------------------

        # Hardhat local network normally exposes RPC at:
        #
        # http://127.0.0.1:8545
        #
        # Web3.py uses this URL to communicate with
        # the blockchain node.

        self.web3 = Web3(
            Web3.HTTPProvider(rpc_url)
        )


        # -----------------------------------------------------
        # STEP 2: Check blockchain connection
        # -----------------------------------------------------

        if not self.web3.is_connected():
            raise ConnectionError(
                f"Could not connect to blockchain RPC: {rpc_url}"
            )


        # -----------------------------------------------------
        # STEP 3: Contract address
        # -----------------------------------------------------

        # The smart contract must already be deployed.
        #
        # Earlier we deployed WebsiteRegistry and got:
        #
        # 0x5FbDB2315678afecb367f032d93F642f64180aa3
        #
        # This address belongs to the local Hardhat network.

        self.contract_address = contract_address or (
            "0x5FbDB2315678afecb367f032d93F642f64180aa3"
        )


        # -----------------------------------------------------
        # STEP 4: Load contract ABI
        # -----------------------------------------------------

        # Hardhat generates the ABI after compilation.
        #
        # ABI tells Web3.py:
        #
        # - which functions exist
        # - what parameters they accept
        # - what they return
        #
        # Example:
        #
        # registerWebsite(string,string)
        # getWebsite(uint256)
        # verifyWebsite(uint256,string)

        artifact_path = Path(
            "../artifacts/contracts/WebsiteRegistry.sol/"
            "WebsiteRegistry.json"
        )


        if not artifact_path.exists():
            raise FileNotFoundError(
                f"Contract artifact not found: {artifact_path}"
            )


        with artifact_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            artifact = json.load(file)


        self.contract = self.web3.eth.contract(
            address=Web3.to_checksum_address(
                self.contract_address
            ),
            abi=artifact["abi"],
        )


    # =========================================================
    # HEALTH CHECK
    # =========================================================

    def health_check(self) -> bool:
        """
        Check whether blockchain node is reachable.

        Returns:

            True
                Blockchain is reachable.

            False
                Blockchain is not reachable.
        """

        return self.web3.is_connected()


    # =========================================================
    # REGISTER WEBSITE
    # =========================================================

    def register_website(
        self,
        name: str,
        cid: str,
        private_key: str,
    ) -> int:
        """
        Register a website on the blockchain.

        Input:

            name
                Human-readable website name.

            cid
                Root CID returned by IPFS.

            private_key
                Wallet private key used to sign
                the blockchain transaction.

        Flow:

            Website
                ↓
            IPFS
                ↓
            CID
                ↓
            this function
                ↓
            registerWebsite()
                ↓
            Blockchain
        """

        # -----------------------------------------------------
        # STEP 1: Get wallet address
        # -----------------------------------------------------

        account = self.web3.eth.account.from_key(
            private_key
        )

        wallet_address = account.address


        # -----------------------------------------------------
        # STEP 2: Get current nonce
        # -----------------------------------------------------

        # Nonce identifies the transaction number
        # for this wallet.

        nonce = self.web3.eth.get_transaction_count(
            wallet_address
        )


        # -----------------------------------------------------
        # STEP 3: Build smart contract transaction
        # -----------------------------------------------------

        transaction = (
            self.contract.functions
            .registerWebsite(name, cid)
            .build_transaction(
                {
                    "from": wallet_address,

                    # Current account nonce
                    "nonce": nonce,

                    # Gas limit for local development
                    "gas": 500000,

                    # Current gas price
                    "gasPrice": self.web3.eth.gas_price,
                }
            )
        )


        # -----------------------------------------------------
        # STEP 4: Sign transaction
        # -----------------------------------------------------

        # IMPORTANT:
        #
        # The private key NEVER goes to the smart contract.
        #
        # It is used locally to cryptographically sign
        # the transaction.

        signed_transaction = (
            self.web3.eth.account.sign_transaction(
                transaction,
                private_key=private_key,
            )
        )


        # -----------------------------------------------------
        # STEP 5: Send transaction
        # -----------------------------------------------------

        transaction_hash = (
            self.web3.eth.send_raw_transaction(
                signed_transaction.raw_transaction
            )
        )


        # -----------------------------------------------------
        # STEP 6: Wait for blockchain confirmation
        # -----------------------------------------------------

        receipt = (
            self.web3.eth.wait_for_transaction_receipt(
                transaction_hash
            )
        )


        # -----------------------------------------------------
        # STEP 7: Extract website ID
        # -----------------------------------------------------

        # registerWebsite() returns website ID.
        #
        # However, because this is a blockchain transaction,
        # the return value is normally represented through
        # transaction execution/event logs.
        #
        # Our contract emits WebsiteRegistered event.
        #
        # We therefore read the event from the receipt.

        events = self.contract.events.WebsiteRegistered().process_receipt(
            receipt
        )


        if not events:
            raise RuntimeError(
                "WebsiteRegistered event not found"
            )


        website_id = events[0]["args"]["websiteId"]


        return int(website_id)


    # =========================================================
    # GET WEBSITE
    # =========================================================

    def get_website(
        self,
        website_id: int,
    ):
        """
        Read website information from blockchain.

        This is a READ operation.

        Therefore:

            No transaction
            No gas
            No private key

        is required.
        """

        return self.contract.functions.getWebsite(
            website_id
        ).call()


    # =========================================================
    # VERIFY WEBSITE
    # =========================================================

    def verify_website(
        self,
        website_id: int,
        cid: str,
    ) -> bool:
        """
        Verify whether a CID matches the CID stored
        on blockchain.

        Example:

            Stored CID:
                QmABC...

            Provided CID:
                QmABC...

            Result:
                True
        """

        return self.contract.functions.verifyWebsite(
            website_id,
            cid,
        ).call()


# =============================================================
# REUSABLE SERVICE INSTANCE
# =============================================================

blockchain_service = BlockchainService()