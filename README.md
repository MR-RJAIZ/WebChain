### Ritik — Blockchain + IPFS

#### Blockchain — Completed

- [x] Hardhat 3 project setup
- [x] Solidity smart contract development
- [x] `WebsiteRegistry.sol` created
- [x] Website registration functionality
- [x] IPFS CID storage on blockchain
- [x] Website owner/address storage
- [x] Website timestamp storage
- [x] Website lookup functionality
- [x] CID verification functionality
- [x] Owner-only CID update
- [x] Unauthorized update protection
- [x] Smart contract events
- [x] Mocha/Chai tests
- [x] Solidity tests
- [x] Hardhat Ignition deployment
- [x] Local Hardhat blockchain deployment

#### Our Current Blockchain Flow :-

```text
Website Name + IPFS CID
          ↓
   WebsiteRegistry
          ↓
 ┌──────────────────────┐
 │ Website ID           │
 │ Website Name         │
 │ IPFS CID             │
 │ Owner Address        │
 │ Timestamp            │
 └──────────────────────┘
