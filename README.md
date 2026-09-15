# WebChain — Decentralized Web Hosting

> A decentralized static web hosting platform using **IPFS for website storage** and **Blockchain for a verifiable CID registry**.

## 🚀 Overview

WebChain allows users to upload and deploy static websites using decentralized technologies.

The core idea is:

**IPFS stores the website content, while Blockchain stores and verifies its CID.**

## 🎯 Purpose

Traditional hosting depends on centralized servers. WebChain explores a decentralized alternative for static websites by combining:

- **IPFS** → decentralized content storage
- **Blockchain** → Website-to-CID registry and verification

Website files are **not stored on the blockchain**.

## 🏗️ Architecture

```text
User
 ↓
React / Vite Frontend
 ↓
FastAPI Backend
 ├──→ IPFSService → Kubo / IPFS → Root CID
 │
 └──→ BlockchainService → WebsiteRegistry.sol
                              ↓
                         Website ID + CID

🔄 How It Works
1. User selects website files
          ↓
2. Frontend sends files to FastAPI
          ↓
3. Backend uploads website to IPFS
          ↓
4. IPFS generates Root CID
          ↓
5. Backend registers CID on blockchain
          ↓
6. Blockchain returns Website ID
          ↓
7. Frontend shows Website ID + CID
          ↓
8. User can view and verify the deployed website


🛠️ Tech Stack

Frontend: React, Vite, JavaScript, CSS
Backend: Python, FastAPI, Uvicorn
Storage: IPFS, Kubo
Blockchain: Solidity, Hardhat, Web3.py
Development: Git, GitHub, VS Code

📂 Project Structure

WebChain/
├── contracts/
│   └── WebsiteRegistry.sol
├── ignition/
├── test/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   │   ├── ipfs_service.py
│   │   │   ├── blockchain_service.py
│   │   │   └── upload_service.py
│   │   └── main.py
│   ├── tests/
│   └── .env.example
├── frontend/
├── test-site/
└── README.md

✨ Features

Static website deployment
Multiple file upload
Nested assets support
IPFS content storage
Blockchain CID registration
Website ID generation
CID verification
Owner-only website updates
IPFS gateway website access
Frontend + Backend + IPFS + Blockchain integration

▶️ Run Locally

1. Start Blockchain
npx hardhat node
2. Deploy Contract
npx hardhat ignition deploy ignition/modules/WebsiteRegistry.ts --network localhost

Update the deployed contract address in backend/.env.

3. Start IPFS
ipfs daemon
4. Start Backend
cd backend
python -m uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs

5. Start Frontend
cd frontend
npm install
npm run dev

Open the URL shown by Vite, usually:

http://127.0.0.1:5173

🧪 Test

Smart contract:

npx hardhat test

Backend:

cd backend
pytest

For end-to-end testing, upload the included test-site/ and verify:

HTML loads
CSS loads
JavaScript works
Image/assets load
CID is generated
Website ID is registered
CID verification works
🔐 Security
Private keys stay in backend/.env
.env must never be committed
Kubo RPC should not be publicly exposed
Uploaded paths are validated and sanitized
Blockchain stores metadata/CID, not website files


🌐 Applications

WebChain can be used for:

Decentralized static websites
Documentation hosting
Academic/research archives
Organizational websites
dApp frontends
Versioned static content
👥 Team

Ritik — Blockchain + IPFS
Suryansh — Frontend
Saquib — Backend

🔮 Future Scope
Custom domains
Wallet-based ownership
Persistent IPFS pinning
Public blockchain deployment
Website version history
Deployment rollback
Production-grade authentication and monitoring
📌 Core Idea

IPFS stores the website. Blockchain stores and verifies its CID.

WebChain demonstrates an end-to-end approach to decentralized static website deployment.


                         
