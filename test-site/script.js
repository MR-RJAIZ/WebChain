// WebChain Test Site — script.js
// Confirms JavaScript loaded successfully.

(function () {
    "use strict";

    // Update the JS status card.
    const statusEl = document.getElementById("js-status");
    if (statusEl) {
        statusEl.textContent = "✓ JavaScript loaded successfully from IPFS!";
        statusEl.style.color = "#00d4aa";
    }

    // Show the current timestamp.
    const timestampEl = document.getElementById("timestamp");
    if (timestampEl) {
        const now = new Date().toISOString();
        timestampEl.textContent = "Page loaded at: " + now;
    }

    console.log("[WebChain Test Site] All files loaded from IPFS ✓");
    console.log("[WebChain Test Site] HTML ✓  CSS ✓  JS ✓  Assets ✓");
})();
