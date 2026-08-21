// SPDX-License-Identifier: UNLICENSED

// Solidity compiler ko bataya ja raha hai ki
// hum Solidity 0.8.28 ya compatible 0.8.x version use karenge.
pragma solidity ^0.8.28;


// Hamara smart contract.
// Ye blockchain par deploy hoga.
contract WebsiteRegistry {

    // ---------------------------------------------------------
    // WEBSITE DATA STRUCTURE
    // ---------------------------------------------------------

    // struct ek custom data type hai.
    //
    // Ek website ke baare mein jo information humein
    // blockchain par store karni hai, wo yahan define hoti hai.
    struct Website {

        // Website ka unique ID.
        // Example: 1, 2, 3...
        uint256 id;

        // Website ka human-readable naam.
        // Example: "Ritik Portfolio"
        string name;

        // IPFS ka CID.
        //
        // Website ki actual files blockchain par nahi hongi.
        // IPFS par upload hone ke baad jo CID milega,
        // wahi yahan store hoga.
        //
        // Example:
        // bafybeigdyr...
        string cid;

        // Website register karne wale wallet ka address.
        //
        // msg.sender se ye address milega.
        address owner;

        // Website registration ke time ka blockchain timestamp.
        uint256 timestamp;
    }


    // ---------------------------------------------------------
    // STORAGE
    // ---------------------------------------------------------

    // Ye mapping website ID ko Website object se connect karti hai.
    //
    // Example:
    //
    // websites[1] -> Website #1
    // websites[2] -> Website #2
    // websites[3] -> Website #3
    //
    // "private" ka matlab contract ke bahar directly
    // is mapping ko access nahi kiya ja sakta.
    mapping(uint256 => Website) private websites;


    // Next website ko kaunsi ID deni hai.
    //
    // Agar first website register hoti hai:
    // nextWebsiteId = 1
    //
    // registration ke baad:
    // nextWebsiteId = 2
    uint256 private nextWebsiteId = 1;


    // ---------------------------------------------------------
    // EVENTS
    // ---------------------------------------------------------

    // Event blockchain par ek log create karta hai.
    //
    // Jab website register hogi to ye event emit hoga.
    //
    // Frontend/backend future mein in events ko
    // listen karke updates detect kar sakte hain.
    event WebsiteRegistered(
        uint256 indexed websiteId,
        string name,
        string cid,
        address indexed owner
    );


    // Website update hone par ye event emit hoga.
    event WebsiteUpdated(
        uint256 indexed websiteId,
        string newCid
    );


    // ---------------------------------------------------------
    // REGISTER WEBSITE
    // ---------------------------------------------------------

    function registerWebsite(
        string memory name,
        string memory cid
    ) public returns (uint256) {

        // Empty website name allow nahi karna.
        require(
            bytes(name).length > 0,
            "Website name cannot be empty"
        );

        // Empty CID allow nahi karna.
        require(
            bytes(cid).length > 0,
            "CID cannot be empty"
        );


        // Current nextWebsiteId ko local variable mein rakh rahe hain.
        //
        // Example:
        // nextWebsiteId = 1
        //
        // to currentWebsiteId = 1
        uint256 currentWebsiteId = nextWebsiteId;


        // Website data blockchain storage mein save kar rahe hain.
        websites[currentWebsiteId] = Website({

            // Website ID
            id: currentWebsiteId,

            // User ke dwara diya gaya name
            name: name,

            // IPFS CID
            cid: cid,

            // msg.sender = jis wallet ne transaction bheji.
            //
            // Isi wallet ko website ka owner bana rahe hain.
            owner: msg.sender,

            // Current blockchain timestamp
            timestamp: block.timestamp
        });


        // Next website ke liye ID increase kar do.
        //
        // 1 → 2
        // 2 → 3
        // 3 → 4
        nextWebsiteId++;


        // Event emit kar rahe hain.
        //
        // Isse blockchain logs mein registration record
        // create ho jata hai.
        emit WebsiteRegistered(
            currentWebsiteId,
            name,
            cid,
            msg.sender
        );


        // Website ID return kar rahe hain.
        return currentWebsiteId;
    }


    // ---------------------------------------------------------
    // GET WEBSITE
    // ---------------------------------------------------------

    // "view" ka matlab:
    //
    // Ye function blockchain state ko change nahi karega.
    // Sirf data read karega.
    function getWebsite(
        uint256 websiteId
    ) public view returns (Website memory) {

        // Given ID ka website record return kar do.
        return websites[websiteId];
    }


    // ---------------------------------------------------------
    // VERIFY WEBSITE
    // ---------------------------------------------------------

    function verifyWebsite(
        uint256 websiteId,
        string memory providedCid
    ) public view returns (bool) {

        // Stored CID blockchain se read kar rahe hain.
        string memory storedCid = websites[websiteId].cid;


        // Solidity mein strings ko directly == se compare
        // nahi karte.
        //
        // Isliye dono strings ka keccak256 hash bana rahe hain.
        //
        // Agar hashes same hain:
        // CID same hai.
        //
        // Agar hashes different hain:
        // CID different hai.
        return
            keccak256(bytes(storedCid)) ==
            keccak256(bytes(providedCid));
    }


    // ---------------------------------------------------------
    // UPDATE WEBSITE
    // ---------------------------------------------------------

    function updateWebsite(
        uint256 websiteId,
        string memory newCid
    ) public {

        // Check kar rahe hain ki website exist karti hai.
        require(
            websites[websiteId].id != 0,
            "Website does not exist"
        );


        // IMPORTANT SECURITY CHECK
        //
        // Sirf website ka owner CID update kar sakta hai.
        //
        // Agar:
        //
        // stored owner = 0xABC
        // msg.sender   = 0xABC
        //
        // allowed ✅
        //
        // Agar:
        //
        // stored owner = 0xABC
        // msg.sender   = 0xXYZ
        //
        // transaction reject ❌
        require(
            websites[websiteId].owner == msg.sender,
            "Not website owner"
        );


        // New CID ko blockchain mein update kar rahe hain.
        websites[websiteId].cid = newCid;


        // Update event emit kar rahe hain.
        emit WebsiteUpdated(
            websiteId,
            newCid
        );
    }
}