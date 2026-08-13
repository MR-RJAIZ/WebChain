javascript
// ==========================================
// WEB3HOST JAVASCRIPT
// ==========================================


// Sample websites

let websites = JSON.parse(
    localStorage.getItem("websites")
) || [
    {
        id: 1,
        name: "My Portfolio",
        cid: "bafybeig12345",
        size: 12,
        status: "Live"
    },
    {
        id: 2,
        name: "College Project",
        cid: "bafybeig67890",
        size: 25,
        status: "Live"
    }
];


// ==========================================
// PAGE LOAD
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    displayWebsites();

    updateStats();

    displayActivity();

});


// ==========================================
// CONNECT WALLET
// ==========================================

function connectWallet() {

    const button = document.querySelector(".wallet-btn");

    button.innerText = "0x71...A92F";

    showNotification("Wallet connected successfully!");

}


// ==========================================
// DASHBOARD
// ==========================================

function showDashboard() {

    document
        .getElementById("dashboard")
        .scrollIntoView({
            behavior: "smooth"
        });

}


// ==========================================
// FEATURES
// ==========================================

function scrollToFeatures() {

    document
        .getElementById("features")
        .scrollIntoView({
            behavior: "smooth"
        });

}


// ==========================================
// DEPLOY MODAL
// ==========================================

function openDeployModal() {

    document.getElementById("deployModal").style.display = "flex";

}


function closeDeployModal() {

    document.getElementById("deployModal").style.display = "none";

}


// Close modal when clicking outside

window.onclick = function (event) {

    const modal = document.getElementById("deployModal");

    if (event.target === modal) {

        closeDeployModal();

    }

};


// ==========================================
// FILE SELECTION
// ==========================================

function showSelectedFiles() {

    const files =
        document.getElementById("websiteFile").files;

    const fileInfo =
        document.getElementById("fileInfo");


    if (files.length === 0) {

        fileInfo.innerText =
            "No files selected";

        return;

    }


    let totalSize = 0;

    for (let file of files) {

        totalSize += file.size;

    }


    const sizeMB =
        (totalSize / (1024 * 1024)).toFixed(2);


    fileInfo.innerText =
        files.length +
        " file(s) selected • " +
        sizeMB +
        " MB";

}


// ==========================================
// DEPLOY WEBSITE
// ==========================================

function deployWebsite() {

    const name =
        document
            .getElementById("projectName")
            .value
            .trim();


    const files =
        document
            .getElementById("websiteFile")
            .files;


    if (!name) {

        showNotification(
            "Please enter project name!"
        );

        return;

    }


    if (files.length === 0) {

        showNotification(
            "Please select website files!"
        );

        return;

    }


    // Calculate size

    let totalSize = 0;

    for (let file of files) {

        totalSize += file.size;

    }


    const sizeMB =
        Number(
            (totalSize / (1024 * 1024))
                .toFixed(2)
        );


    // Generate fake CID

    const cid =
        "bafy" +
        Math.random()
            .toString(36)
            .substring(2, 15);


    const newWebsite = {

        id: Date.now(),

        name: name,

        cid: cid,

        size: sizeMB,

        status: "Live"

    };


    websites.push(newWebsite);


    // Save in browser

    localStorage.setItem(
        "websites",
        JSON.stringify(websites)
    );


    // Update UI

    displayWebsites();

    updateStats();

    displayActivity();


    // Close modal

    closeDeployModal();


    // Clear form

    document.getElementById("projectName").value = "";

    document.getElementById("websiteFile").value = "";

    document.getElementById("fileInfo").innerText =
        "No files selected";


    showNotification(
        "Website deployed successfully!"
    );

}


// ==========================================
// DISPLAY WEBSITES
// ==========================================

function displayWebsites() {

    const container =
        document.getElementById(
            "websiteContainer"
        );


    container.innerHTML = "";


    if (websites.length === 0) {

        container.innerHTML = `
    < div class="website-card" >
        <p>No websites deployed yet.</p>
            </div >
    `;

        return;

    }


    websites.forEach(function (site) {

        const card =
            document.createElement("div");

        card.className =
            "website-card";


        card.innerHTML = `

    < div >

                <h3>
                    ${site.name}
                </h3>

                <p>
                    CID: ${site.cid}
                </p>

                <p>
                    Size: ${site.size} MB
                </p>

                <span class="status">
                    ● ${site.status}
                </span>

            </div >


    <div class="card-buttons">

        <button
            onclick="viewWebsite('${site.cid}')">
            View
        </button>

        <button
            onclick="copyCID('${site.cid}')">
            Copy CID
        </button>

        <button
            onclick="deleteWebsite(${site.id})">
            Delete
        </button>

    </div>

`;


        container.appendChild(card);

    });

}


// ==========================================
// VIEW WEBSITE
// ==========================================

function viewWebsite(cid) {

    showNotification(
        "IPFS website: " + cid
    );

}


// ==========================================
// COPY CID
// ==========================================

function copyCID(cid) {

    navigator.clipboard.writeText(cid);

    showNotification(
        "CID copied!"
    );

}


// ==========================================
// DELETE WEBSITE
// ==========================================

function deleteWebsite(id) {

    const confirmDelete =
        confirm(
            "Are you sure you want to delete this website?"
        );


    if (!confirmDelete) {

        return;

    }


    websites =
        websites.filter(
            function (site) {

                return site.id !== id;

            }
        );


    localStorage.setItem(
        "websites",
        JSON.stringify(websites)
    );


    displayWebsites();

    updateStats();

    displayActivity();


    showNotification(
        "Website deleted!"
    );

}


// ==========================================
// SEARCH
// ==========================================

function searchWebsites() {

    const search =
        document
            .getElementById("searchInput")
            .value
            .toLowerCase();


    const cards =
        document.querySelectorAll(
            ".website-card"
        );


    cards.forEach(function (card) {

        const text =
            card.innerText.toLowerCase();


        if (text.includes(search)) {

            card.style.display = "flex";

        } else {

            card.style.display = "none";

        }

    });

}


// ==========================================
// UPDATE STATS
// ==========================================

function updateStats() {

    document.getElementById(
        "totalWebsites"
    ).innerText = websites.length;


    document.getElementById(
        "totalDeployments"
    ).innerText = websites.length;


    let totalStorage = 0;


    websites.forEach(
        function (site) {

            totalStorage += site.size;

        }
    );


    document.getElementById(
        "storageUsed"
    ).innerText =
        totalStorage.toFixed(2) + " MB";


    document.getElementById(
        "activeSites"
    ).innerText =
        websites.filter(
            site => site.status === "Live"
        ).length;

}


// ==========================================
// ACTIVITY
// ==========================================

function displayActivity() {

    const container =
        document.getElementById(
            "activityContainer"
        );


    container.innerHTML = "";


    const recent =
        websites.slice(-5).reverse();


    recent.forEach(
        function (site) {

            const item =
                document.createElement("div");


            item.className =
                "activity-item";


            item.innerHTML = `

    < div >

                    🚀

<strong>
    ${site.name}
</strong>

                    deployed successfully

                </div >

    <span>
        ● Live
    </span>

`;


            container.appendChild(item);

        }
    );

}


// ==========================================
// NOTIFICATION
// ==========================================

function showNotification(message) {

    const toast =
        document.getElementById("toast");


    toast.innerText = message;


    toast.style.display = "block";


    setTimeout(
        function () {

            toast.style.display =
                "none";

        },
        2500
    );

}


// ==========================================
// DARK / LIGHT MODE
// ==========================================

const themeBtn =
    document.getElementById("themeBtn");


themeBtn.addEventListener(
    "click",
    function () {

        document.body.classList.toggle(
            "light-mode"
        );


        if (
            document.body.classList.contains(
                "light-mode"
            )
        ) {

            themeBtn.innerText = "☀️";

            localStorage.setItem(
                "theme",
                "light"
            );

        } else {

            themeBtn.innerText = "🌙";

            localStorage.setItem(
                "theme",
                "dark"
            );

        }

    }
);


// Load saved theme

if (
    localStorage.getItem("theme") ===
    "light"
) {

    document.body.classList.add(
        "light-mode"
    );

    themeBtn.innerText = "☀️";

}
