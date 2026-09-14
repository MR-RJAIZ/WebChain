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
Ethereum-compatible blockchain (local Hardhat node)
   ↓
WebsiteRegistry.sol

IMPORTANT:
- Private key is loaded from settings (.env) only.
- Private key is never logged, returned, or exposed.
- This service is lazy-initialized: if Hardhat is not running
  at startup, FastAPI will still start. Errors appear at
  call time, not import time.
"""

import json
import logging
from pathlib import Path

from web3 import Web3

from app.config import settings


logger = logging.getLogger(__name__)


class BlockchainService:
    """
    Service responsible for interacting with
    WebsiteRegistry smart contract.

    IPFSService  → Website files → IPFS → CID
    BlockchainService → CID → Blockchain → Website ID

    Design: lazy initialization.
    The web3 connection and contract instance are created
    on first use, not at import time. This prevents FastAPI
    from crashing if Hardhat is not running at startup.
    """

    def __init__(
        self,
        rpc_url: str | None = None,
        contract_address: str | None = None,
    ):
        self.rpc_url = rpc_url or settings.rpc_url
        self.contract_address_raw = (
            contract_address or settings.contract_address
        )

        # These are set up lazily on first use.
        self._web3: Web3 | None = None
        self._contract = None

    # =========================================================
    # LAZY INITIALIZATION
    # =========================================================

    def _get_web3(self) -> Web3:
        """
        Return a connected Web3 instance.

        WHY lazy:
        If Hardhat node is not running when FastAPI starts,
        we don't want the entire application to crash.
        Instead, individual API calls will fail with a clear
        503 error message.
        """

        if self._web3 is None:
            web3 = Web3(Web3.HTTPProvider(self.rpc_url))

            if not web3.is_connected():
                raise ConnectionError(
                    f"Cannot connect to blockchain RPC at "
                    f"{self.rpc_url}. "
                    f"Is the Hardhat node running?"
                )

            self._web3 = web3

        return self._web3

    def _get_contract(self):
        """
        Return a connected contract instance.

        Loads ABI from the compiled Hardhat artifact file.
        """

        if self._contract is None:
            web3 = self._get_web3()

            # =====================================================
            # RESOLVE CONTRACT ADDRESS
            # =====================================================

            if not self.contract_address_raw:
                raise ValueError(
                    "CONTRACT_ADDRESS is not configured in .env"
                )

            address = Web3.to_checksum_address(
                self.contract_address_raw
            )

            # =====================================================
            # VERIFY CONTRACT DEPLOYMENT
            # =====================================================

            code = web3.eth.get_code(address)

            if not code or code == b"":
                raise ConnectionError(
                    f"No smart contract deployed at {address}. "
                    f"Did you run the deployment script?"
                )

            # =====================================================
            # LOAD ABI
            # =====================================================

            # Project layout:
            #
            # WebChain/
            # ├── artifacts/
            # │   └── contracts/
            # │       └── WebsiteRegistry.sol/
            # │           └── WebsiteRegistry.json  ← ABI here
            # └── backend/
            #     └── app/
            #         └── services/
            #             └── blockchain_service.py  ← this file

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
                    f"Contract artifact not found at: {artifact_path}\n"
                    f"Run: npx hardhat compile"
                )

            with artifact_path.open("r", encoding="utf-8") as f:
                artifact = json.load(f)

            # =====================================================
            # CREATE CONTRACT INSTANCE
            # =====================================================

            self._contract = web3.eth.contract(
                address=address,
                abi=artifact["abi"],
            )

        return self._contract

    # =========================================================
    # HEALTH CHECK
    # =========================================================

    def health_check(self) -> bool:
        """
        Check whether the blockchain node is reachable.

        Returns:
            True  → Hardhat/blockchain is running
            False → connection failed
        """

        try:
            web3 = Web3(Web3.HTTPProvider(self.rpc_url))
            return web3.is_connected()
        except Exception:
            return False

    # =========================================================
    # REGISTER WEBSITE
    # =========================================================

    def register_website(
        self,
        name: str,
        cid: str,
    ) -> dict:
        """
        Register a new website on the blockchain.

        Flow:
            name + CID
               ↓
            build transaction
               ↓
            sign with private key (from .env)
               ↓
            send to blockchain
               ↓
            wait for confirmation
               ↓
            read WebsiteRegistered event → website_id
               ↓
            return {website_id, transaction_hash}

        Args:
            name: Human-readable website name.
            cid:  IPFS root CID of the uploaded website.

        Returns:
            dict with 'website_id' (int) and 'transaction_hash' (str).
        """

        if not name.strip():
            raise ValueError("Website name cannot be empty")

        if not cid.strip():
            raise ValueError("CID cannot be empty")

        web3 = self._get_web3()
        contract = self._get_contract()

        # Get the private key from settings (.env).
        # NEVER hardcode or log this.
        private_key = settings.private_key

        if not private_key:
            raise ValueError("PRIVATE_KEY is not set in .env")

        # Derive the wallet address from the private key.
        account = web3.eth.account.from_key(private_key)
        wallet_address = account.address

        # Get the nonce for this wallet.
        # "pending" includes unconfirmed txs to avoid nonce conflicts.
        nonce = web3.eth.get_transaction_count(
            wallet_address,
            "pending",
        )

        # Build the contract function call transaction.
        transaction = (
            contract.functions
            .registerWebsite(name, cid)
            .build_transaction(
                {
                    "from": wallet_address,
                    "nonce": nonce,
                    "gas": 500_000,
                    "gasPrice": web3.eth.gas_price,
                }
            )
        )

        # Sign locally — private key never leaves this service.
        signed = web3.eth.account.sign_transaction(
            transaction,
            private_key=private_key,
        )

        # Broadcast the signed transaction.
        tx_hash = web3.eth.send_raw_transaction(
            signed.raw_transaction
        )

        # Wait for the transaction to be mined.
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        # Check for transaction failure.
        if receipt["status"] != 1:
            raise RuntimeError(
                "Blockchain transaction failed (status 0). "
                "Check Hardhat logs for revert reason."
            )

        # Parse the WebsiteRegistered event from the receipt.
        # This is how we get the website_id without a second call.
        events = (
            contract
            .events
            .WebsiteRegistered()
            .process_receipt(receipt)
        )

        if not events:
            raise RuntimeError(
                "WebsiteRegistered event not found in receipt. "
                "Transaction may have succeeded without emitting the event."
            )

        website_id = int(events[0]["args"]["websiteId"])

        logger.info(
            "Website registered: id=%d name=%r cid=%r tx=%s",
            website_id,
            name,
            cid,
            tx_hash.hex(),
        )

        return {
            "website_id": website_id,
            "transaction_hash": tx_hash.hex(),
        }

    # =========================================================
    # GET WEBSITE
    # =========================================================

    def get_website(
        self,
        website_id: int,
    ) -> dict:
        """
        Read website metadata from the blockchain.

        This is a READ-ONLY operation.
        No transaction, no gas, no private key needed.

        Args:
            website_id: The website's on-chain ID.

        Returns:
            dict with id, name, cid, owner, timestamp.
        """

        contract = self._get_contract()

        website = (
            contract.functions
            .getWebsite(website_id)
            .call()
        )

        return {
            "id":        int(website[0]),
            "name":      website[1],
            "cid":       website[2],
            "owner":     website[3],
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
        Verify whether the provided CID matches the
        CID stored on the blockchain for this website.

        Use case:
            The user wants to check if a given CID is authentic.
            We compare it against what's stored on-chain.

        Returns:
            True  → CIDs match (content is authentic)
            False → CIDs don't match (content may be tampered)
        """

        contract = self._get_contract()

        return contract.functions.verifyWebsite(
            website_id,
            cid,
        ).call()

    # =========================================================
    # UPDATE WEBSITE
    # =========================================================

    def update_website(
        self,
        website_id: int,
        new_cid: str,
    ) -> dict:
        """
        Update the CID for an existing website.

        IMPORTANT SECURITY:
        The smart contract enforces owner-only updates.
        Only the wallet that originally registered the website
        can update its CID. The contract will revert if
        any other wallet tries to update.

        Flow:
            new_cid
               ↓
            build updateWebsite() transaction
               ↓
            sign with private key (same backend wallet)
               ↓
            send to blockchain
               ↓
            contract checks: msg.sender == owner
               ↓
            if ok: CID updated + WebsiteUpdated event emitted

        Args:
            website_id: The website's on-chain ID.
            new_cid:    The new IPFS root CID.

        Returns:
            dict with 'transaction_hash' and 'new_cid'.
        """

        if not new_cid.strip():
            raise ValueError("New CID cannot be empty")

        web3 = self._get_web3()
        contract = self._get_contract()

        private_key = settings.private_key

        if not private_key:
            raise ValueError("PRIVATE_KEY is not set in .env")

        account = web3.eth.account.from_key(private_key)
        wallet_address = account.address

        nonce = web3.eth.get_transaction_count(
            wallet_address,
            "pending",
        )

        transaction = (
            contract.functions
            .updateWebsite(website_id, new_cid)
            .build_transaction(
                {
                    "from": wallet_address,
                    "nonce": nonce,
                    "gas": 300_000,
                    "gasPrice": web3.eth.gas_price,
                }
            )
        )

        signed = web3.eth.account.sign_transaction(
            transaction,
            private_key=private_key,
        )

        tx_hash = web3.eth.send_raw_transaction(
            signed.raw_transaction
        )

        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt["status"] != 1:
            raise RuntimeError(
                f"Update transaction failed for website_id={website_id}. "
                f"Are you the owner?"
            )

        logger.info(
            "Website updated: id=%d new_cid=%r tx=%s",
            website_id,
            new_cid,
            tx_hash.hex(),
        )

        return {
            "transaction_hash": tx_hash.hex(),
            "new_cid": new_cid,
        }


# =============================================================
# REUSABLE SERVICE INSTANCE
# =============================================================

# Single shared instance used across the application.
#
# Import it like this:
#
#   from app.services.blockchain_service import blockchain_service
#
# Then:
#
#   blockchain_service.register_website(name, cid)
#   blockchain_service.get_website(website_id)
#   blockchain_service.verify_website(website_id, cid)
#   blockchain_service.update_website(website_id, new_cid)
#
# IMPORTANT: This is lazy-initialized.
# The connection happens on first use, not at module import.

blockchain_service = BlockchainService()