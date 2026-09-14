# WebChain — Decentralized Web Hosting Platform

WebChain is an academic prototype of a decentralized website hosting platform. It allows users to upload static websites, host the content securely on IPFS, and register the website's root CID on an Ethereum-compatible blockchain for immutable tracking.

## 🎯 The Problem Solved
Traditional static hosting (like Vercel or AWS S3) relies on centralized servers. If those servers go down, or if the provider decides to censor the content, the website disappears. WebChain solves this by decentralizing the hosting layer (via IPFS) and the registry layer (via Blockchain).

## 🧠 Core Idea & Architecture
The platform separates responsibilities cleanly across a Web3 stack:

1. **Frontend (Vite + React)**: Provides a simple UI for users to upload their static website files (`.html`, `.css`, `.js`, etc.) and view their deployment status.
2. **Backend (FastAPI)**: Serves as the orchestrator. It receives the files, places them into an isolated deployment directory, and coordinates with IPFS and the blockchain.
3. **Storage (IPFS / Kubo)**: The actual website files are uploaded to a local IPFS node, which returns a cryptographic **Root CID**. This CID represents the entire directory structure of the website.
4. **Registry (Blockchain / Hardhat)**: The smart contract (`WebsiteRegistry.sol`) stores the relationship between a `Website ID`, its `Owner`, and the `CID`. The files themselves are never stored on the blockchain, only the metadata.

### Why is the CID on the blockchain?
By storing the CID on the blockchain, we create an immutable, timestamped record of exactly what content was deployed. If a user wants to verify that the website they are viewing on IPFS hasn't been tampered with, they can query the blockchain registry and verify that the CIDs match. Only the original owner wallet can push an updated CID to the registry.

## 🛠️ Technology Stack
- **Frontend**: React, Vite, CSS (Vanilla)
- **Backend**: FastAPI, Web3.py, Uvicorn, Python-Multipart
- **Blockchain**: Solidity, Hardhat, Ethers.js
- **Storage**: IPFS (Kubo)

## 📂 Project Structure
```text
WebChain/
├── backend/            # FastAPI orchestration layer
│   ├── app/            # Routes, services, models
│   ├── tests/          # Pytest backend tests
│   └── uploads/        # Isolated deployment directories
├── contracts/          # Solidity smart contracts
│   └── WebsiteRegistry.sol
├── frontend/           # Vite React UI
│   ├── src/            # App.jsx, index.css
│   └── index.html
├── ignition/           # Hardhat ignition deployment modules
├── test/               # Mocha/Chai smart contract tests
└── test-site/          # A sample static website to test deployments
```

---

## 🚀 Setup & Installation

### Prerequisites
1. **Node.js & npm** (v18+)
2. **Python** (v3.10+)
3. **Kubo (IPFS)** (v0.43.0+)

### 1. Configure Environment
A default `.env.example` file is provided in the `backend` folder.
Copy it to `.env`:
```bash
cd backend
cp .env.example .env
```
*(The default placeholders are already configured for the local Hardhat node).*

### 2. Start the IPFS Node (Kubo)
Open a terminal and start the IPFS daemon:
```bash
ipfs daemon
```

### 3. Start the Blockchain Node (Hardhat)
Open a new terminal at the project root and install dependencies, then start the local node:
```bash
npm install
npx hardhat node
```

### 4. Deploy the Smart Contract
Open a third terminal at the project root and deploy the contract to your local node:
```bash
npx hardhat ignition deploy ignition/modules/WebsiteRegistry.ts --network localhost
```
*(The deployed address `0x5FbDB2315678afecb367f032d93F642f64180aa3` is already set in the backend `.env.example` by default).*

### 5. Start the FastAPI Backend
In a new terminal, navigate to the `backend` directory, install dependencies, and run the server:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```
*(The API documentation will be available at http://127.0.0.1:8000/docs).*

### 6. Start the Frontend
In a new terminal, navigate to the `frontend` directory, install dependencies, and run Vite:
```bash
cd frontend
npm install
npm run dev
```
*(The frontend will be available at http://localhost:5173).*

---

## 🎥 Demonstration Flow

To demonstrate the platform to a judge or instructor, follow this simple flow:

1. **Open the Frontend**: Go to `http://localhost:5173`.
2. **Login**: Click "Start Deploying" and enter any mock email/password to access the dashboard.
3. **Check Health**: Show the health indicator bar on the dashboard confirming that the API, IPFS, and Blockchain are all connected.
4. **Create a Project**: Click `+ New Project`. Name it "My Test Demo".
5. **Upload Files**: Select all the files inside the `test-site` folder (HTML, CSS, JS, SVG).
6. **Deploy**: Click the "Deploy" button.
   - Explain that the files are being saved to an isolated directory on the backend.
   - The backend then uploads the entire directory to IPFS.
   - The backend finally signs a transaction sending the IPFS root CID to the Hardhat blockchain.
7. **View Details**: Click "Details" to open the project view.
   - Show the assigned **Website ID** and the **IPFS CID**.
   - Show the **Transaction Hash**.
8. **View Website**: Click the IPFS Gateway link to prove the website was actually deployed and all HTML/CSS/JS/Assets loaded correctly via IPFS.
9. **Verify CID**: Paste the CID (or click "Use Current CID") and click "Verify CID". Show that the backend successfully checked the blockchain and confirmed the CID matches.
10. **Update Flow (Optional)**: Click "Deploy Update", select a single file (e.g., `index.html`), and show that a *new* CID is generated and updated on the blockchain.

---

## 🔒 Security & Limitations

As an academic prototype, WebChain prioritizes architectural clarity over production-grade security:
- **Private Keys**: The backend signs transactions locally using a private key loaded from `.env`. The frontend never sees or handles private keys.
- **Path Traversal**: File upload paths are strictly sanitized to prevent malicious `../../` attacks.
- **Isolated Deployments**: Every deployment receives a unique UUID folder (e.g., `uploads/<uuid>/`) so user files cannot overwrite each other.
- **Local Network Only**: This prototype connects to a local Hardhat node and local Kubo instance. Deploying to public networks (e.g., Ethereum Mainnet, public IPFS gateways) would require real gas fees and a production-grade infrastructure setup.