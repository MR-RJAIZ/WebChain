import { expect } from "chai";
import { network } from "hardhat";

const { ethers } = await network.create();

describe("WebsiteRegistry", function () {
  async function deployRegistry() {
    const registry = await ethers.deployContract("WebsiteRegistry");
    return registry;
  }

  it("Should register a website", async function () {
    const registry = await deployRegistry();

    await registry.registerWebsite(
      "Ritik Portfolio",
      "bafybeiexample123"
    );

    const website = await registry.getWebsite(1);

    expect(website.id).to.equal(1n);
    expect(website.name).to.equal("Ritik Portfolio");
    expect(website.cid).to.equal("bafybeiexample123");
  });

  it("Should assign the connected wallet as owner", async function () {
    const registry = await deployRegistry();

    const [owner] = await ethers.getSigners();

    await registry.registerWebsite(
      "Ritik Portfolio",
      "bafybeiexample123"
    );

    const website = await registry.getWebsite(1);

    expect(website.owner).to.equal(owner.address);
  });

  it("Should verify a correct CID", async function () {
    const registry = await deployRegistry();

    await registry.registerWebsite(
      "Ritik Portfolio",
      "bafybeiexample123"
    );

    expect(
      await registry.verifyWebsite(1, "bafybeiexample123")
    ).to.equal(true);
  });

  it("Should reject an incorrect CID", async function () {
    const registry = await deployRegistry();

    await registry.registerWebsite(
      "Ritik Portfolio",
      "bafybeiexample123"
    );

    expect(
      await registry.verifyWebsite(1, "wrongcid")
    ).to.equal(false);
  });

  it("Should allow the owner to update the CID", async function () {
    const registry = await deployRegistry();

    await registry.registerWebsite(
      "Ritik Portfolio",
      "bafybeiexample123"
    );

    await registry.updateWebsite(
      1,
      "bafybeinewcide456"
    );

    const website = await registry.getWebsite(1);

    expect(website.cid).to.equal("bafybeinewcide456");
  });

  it("Should reject an update from a non-owner", async function () {
    const registry = await deployRegistry();

    const [, attacker] = await ethers.getSigners();

    await registry.registerWebsite(
      "Ritik Portfolio",
      "bafybeiexample123"
    );

    const attackerRegistry = registry.connect(attacker);

    await expect(
      attackerRegistry.updateWebsite(
        1,
        "bafybeimalicious"
      )
    ).to.be.revertedWith("Not website owner");
  });
});