"""
Application Configuration
-------------------------

Ye file application ki configuration ko ek central place
par manage karti hai.

Important:
Sensitive values jaise PRIVATE_KEY code mein hard-code
nahi karni hain.

Wo .env se load hongi.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    WebChain application settings.

    Values automatically .env file se load hongi.
    """

    # Hardhat / Ethereum-compatible blockchain RPC
    rpc_url: str = "http://127.0.0.1:8545"

    ipfs_api_url: str = "http://127.0.0.1:5001"

    # WebsiteRegistry smart contract address
    contract_address: str

    # Development wallet private key.
    #
    # IMPORTANT:
    # Ye kabhi GitHub par commit nahi honi chahiye.
    private_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Application ke andar reusable configuration object.
settings = Settings()