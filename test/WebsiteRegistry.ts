// Chai ka expect assertion use kar rahe hain.
//
// Example:
// expect(value).to.equal(10)
import { expect } from "chai";


// Hardhat network access karne ke liye network import kar rahe hain.
import { network } from "hardhat";


// Hardhat network create kar rahe hain.
//
// ethers hume Ethereum/blockchain ke saath interact
// karne ki functionality deta hai.
const { ethers } = await network.create();

  describe("WebsiteRegistry", function () {

  async function deployRegistry() {

    // Har test ke liye fresh WebsiteRegistry contract deploy.
    //
    // Iska benefit:
    // Ek test ka data dusre test ko affect nahi karega.
    const registry =
      await ethers.deployContract("WebsiteRegistry");

    return registry;
  }


  it("Should register a website", async function () {

    // Fresh contract deploy.
    const registry = await deployRegistry();


    // Website register kar rahe hain.
    await registry.registerWebsite(
      "Ritik Portfolio",
      "bafybeiexample123"
    );


    // Blockchain se website ID 1 ka data read kar rahe hain.
    const website = await registry.getWebsite(1);


    // Verify kar rahe hain ki ID 1 hai.
    expect(website.id).to.equal(1n);


    // Verify kar rahe hain ki name correct hai.
    expect(website.name).to.equal(
      "Ritik Portfolio"
    );


    // Verify kar rahe hain ki CID correct hai.
    expect(website.cid).to.equal(
      "bafybeiexample123"
    );
  });

  it("Should assign the connected wallet as owner", async function () {

    // Contract deploy
    const registry = await deployRegistry();


    // Available blockchain wallets mein se first wallet le rahe hain.
    const [owner] = await ethers.getSigners();


    // Website register.
    await registry.registerWebsite(
      "Ritik Portfolio",
      "bafybeiexample123"
    );


    // Website data read.
    const website = await registry.getWebsite(1);


    // Contract mein stored owner ko
    // transaction bhejne wale wallet se compare kar rahe hain.
    expect(website.owner).to.equal(owner.address);
  });

  it("Should verify a correct CID", async function () {

    const registry = await deployRegistry();


    // Website register.
    await registry.registerWebsite(
      "Ritik Portfolio",
      "bafybeiexample123"
    );


    // Same CID verify kar rahe hain.
    const result =
      await registry.verifyWebsite(
        1,
        "bafybeiexample123"
      );


    // Expected result true hona chahiye.
    expect(result).to.equal(true);
 });

  it("Should reject an incorrect CID", async function () {

    const registry = await deployRegistry();


    await registry.registerWebsite(
      "Ritik Portfolio",
      "bafybeiexample123"
    );


    // Galat CID provide kar rahe hain.
    const result =
      await registry.verifyWebsite(
        1,
        "wrongcid"
      );


    // Isliye false expected hai.
    expect(result).to.equal(false);
  });

  it("Should allow the owner to update the CID", async function () {

    const registry = await deployRegistry();


    // First website register.
    await registry.registerWebsite(
      "Ritik Portfolio",
      "bafybeiexample123"
    );


    // Owner new CID update kar raha hai.
    await registry.updateWebsite(
      1,
      "bafybeinewcide456"
    );


    // Updated website read.
    const website =
      await registry.getWebsite(1);


    // Confirm karo ki CID change hua.
    expect(website.cid).to.equal(
      "bafybeinewcide456"
    );
  });

  it("Should reject an update from a non-owner", async function () {

    const registry = await deployRegistry();


    // Blockchain ke second wallet ko attacker maan rahe hain.
    const [, attacker] =
      await ethers.getSigners();


    // Original wallet website register karta hai.
    await registry.registerWebsite(
      "Ritik Portfolio",
      "bafybeiexample123"
    );


    // Contract ko attacker ke wallet se connect kar rahe hain.
    const attackerRegistry =
      registry.connect(attacker);


    // Attacker CID change karne ki koshish karta hai.
    //
    // Lekin contract ke andar:
    //
    // websites[websiteId].owner == msg.sender
    //
    // false hoga.
    //
    // Isliye transaction revert honi chahiye.
    await expect(
      attackerRegistry.updateWebsite(
        1,
        "bafybeimalicious"
      )
    ).to.be.revertedWith(
      "Not website owner"
    );
  });
});