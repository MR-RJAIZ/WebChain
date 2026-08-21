// Hardhat Ignition ka buildModule function import kar rahe hain.
//
// Ignition ka use smart contracts ko systematically
// deploy karne ke liye hota hai.
import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";


// WebsiteRegistryModule naam ka deployment module create kar rahe hain.
//
// "m" deployment manager hai jo contract deployment
// ko handle karega.
export default buildModule(
  "WebsiteRegistryModule",
  (m) => {

    // WebsiteRegistry smart contract deploy kar rahe hain.
    //
    // Solidity file:
    //
    // contracts/WebsiteRegistry.sol
    //
    // Ignition automatically compiled contract ko
    // identify karke deploy karega.
    const registry = m.contract("WebsiteRegistry");


    // Deployed contract ko return kar rahe hain.
    //
    // Isse Ignition ko pata hota hai ki
    // WebsiteRegistry deployment ka result kya hai.
    return {
      registry
    };
  }
);