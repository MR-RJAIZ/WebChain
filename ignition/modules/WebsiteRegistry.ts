import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

export default buildModule("WebsiteRegistryModule", (m) => {
  const websiteRegistry = m.contract("WebsiteRegistry");

  return { websiteRegistry };
});