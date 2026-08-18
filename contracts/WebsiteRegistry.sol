// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract WebsiteRegistry {
    struct Website {
        uint256 id;
        string name;
        string cid;
        address owner;
        uint256 timestamp;
    }

    uint256 private nextWebsiteId;

    mapping(uint256 => Website) private websites;

    event WebsiteRegistered(
        uint256 indexed websiteId,
        string name,
        string cid,
        address indexed owner
    );

    event WebsiteUpdated(
        uint256 indexed websiteId,
        string newCid
    );

    constructor() {
        nextWebsiteId = 1;
    }

    function registerWebsite(
        string memory name,
        string memory cid
    ) public returns (uint256) {
        require(bytes(name).length > 0, "Website name required");
        require(bytes(cid).length > 0, "CID required");

        uint256 websiteId = nextWebsiteId;

        websites[websiteId] = Website({
            id: websiteId,
            name: name,
            cid: cid,
            owner: msg.sender,
            timestamp: block.timestamp
        });

        nextWebsiteId++;

        emit WebsiteRegistered(
            websiteId,
            name,
            cid,
            msg.sender
        );

        return websiteId;
    }

    function getWebsite(
        uint256 websiteId
    )
        public
        view
        returns (
            uint256 id,
            string memory name,
            string memory cid,
            address owner,
            uint256 timestamp
        )
    {
        require(
            websites[websiteId].id != 0,
            "Website does not exist"
        );

        Website memory website = websites[websiteId];

        return (
            website.id,
            website.name,
            website.cid,
            website.owner,
            website.timestamp
        );
    }

    function verifyWebsite(
        uint256 websiteId,
        string memory cid
    ) public view returns (bool) {
        require(
            websites[websiteId].id != 0,
            "Website does not exist"
        );

        return keccak256(bytes(websites[websiteId].cid))
            == keccak256(bytes(cid));
    }

    function updateWebsite(
        uint256 websiteId,
        string memory newCid
    ) public {
        require(
            websites[websiteId].id != 0,
            "Website does not exist"
        );

        require(
            websites[websiteId].owner == msg.sender,
            "Not website owner"
        );

        require(
            bytes(newCid).length > 0,
            "CID required"
        );

        websites[websiteId].cid = newCid;

        emit WebsiteUpdated(
            websiteId,
            newCid
        );
    }
}