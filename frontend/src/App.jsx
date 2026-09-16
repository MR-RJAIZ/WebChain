import { useEffect, useRef, useState } from "react";
import "./index.css";

// =========================================================
// BACKEND API URL
//
// WHY a constant?
// Easy to change for different environments.
// In production you'd replace this with the actual server URL.
// =========================================================

const BACKEND_URL = "http://127.0.0.1:8000";

// =========================================================
// API HELPERS
// =========================================================

/**
 * POST /publish — Deploy website files to IPFS + blockchain.
 *
 * @param {string} name - Website name
 * @param {FileList} files - All selected files
 * @param {function} onStep - Callback to update progress step text
 * @returns {Promise<object>} - { website_id, cid, gateway_url, ... }
 */
async function apiPublish(name, files, onStep) {
  onStep("Preparing files...");

  const formData = new FormData();
  formData.append("name", name);

  // Append every file. The relative path is preserved via
  // file.webkitRelativePath (folder upload) or file.name.
  for (const file of files) {
    // Use the relative path if available (folder upload),
    // otherwise just the filename.
    const relativePath = file.webkitRelativePath || file.name;
    formData.append("files", file, relativePath);
  }

  onStep("Uploading to IPFS...");

  const response = await fetch(`${BACKEND_URL}/publish`, {
    method: "POST",
    body: formData,
    // NOTE: Do NOT set Content-Type header — browser sets it
    // automatically with the correct boundary for multipart.
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || `Server error: ${response.status}`);
  }

  onStep("Registering on blockchain...");

  return data;
}

/**
 * GET /website/{id} — Retrieve website metadata from blockchain.
 */
async function apiGetWebsite(websiteId) {
  const response = await fetch(
    `${BACKEND_URL}/website/${websiteId}`
  );
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || `Not found: ${response.status}`);
  }
  return data;
}

/**
 * GET /website/{id}/verify?cid=... — Verify a CID against blockchain.
 */
async function apiVerifyCID(websiteId, cid) {
  const url = `${BACKEND_URL}/website/${websiteId}/verify?cid=${encodeURIComponent(cid)}`;
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || `Verification failed: ${response.status}`);
  }
  return data;
}

/**
 * PUT /website/{id} — Update CID for an existing website.
 */
async function apiUpdateWebsite(websiteId, name, files, onStep) {
  onStep("Preparing update files...");

  const formData = new FormData();
  formData.append("name", name);

  for (const file of files) {
    const relativePath = file.webkitRelativePath || file.name;
    formData.append("files", file, relativePath);
  }

  onStep("Uploading new version to IPFS...");

  const response = await fetch(`${BACKEND_URL}/website/${websiteId}`, {
    method: "PUT",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || `Update failed: ${response.status}`);
  }

  onStep("Updating blockchain record...");

  return data;
}

/**
 * GET /health — Check all service statuses.
 */
async function apiHealth() {
  try {
    const response = await fetch(`${BACKEND_URL}/health`);
    if (!response.ok) return { api: false, ipfs: false, blockchain: false };
    return await response.json();
  } catch {
    return { api: false, ipfs: false, blockchain: false };
  }
}

// =========================================================
// MAIN APP COMPONENT
// =========================================================

function App() {
  const [page, setPage] = useState("home");
  const [authMode, setAuthMode] = useState("login");
  const [showPassword, setShowPassword] = useState(false);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // ================= THEME =================
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("web3host-theme") === "dark";
  });

  useEffect(() => {
    localStorage.setItem(
      "web3host-theme",
      darkMode ? "dark" : "light"
    );
  }, [darkMode]);

  // ================= USER =================
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("web3host-user");
    return saved ? JSON.parse(saved) : null;
  });

  // ================= PROJECTS =================
  const [projects, setProjects] = useState(() => {
    const saved = localStorage.getItem("web3host-projects");
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem(
      "web3host-projects",
      JSON.stringify(projects)
    );
  }, [projects]);

  const [showProjectModal, setShowProjectModal] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [selectedFiles, setSelectedFiles] = useState([]);

  const [search, setSearch] = useState("");

  // Deployment state
  const [deployingId, setDeployingId] = useState(null);
  const [deploymentStep, setDeploymentStep] = useState("");
  const [deploymentError, setDeploymentError] = useState("");

  // ================= PROJECT DETAILS =================
  const [selectedProject, setSelectedProject] = useState(null);

  // ================= NOTIFICATIONS =================
  const [notifications, setNotifications] = useState([]);

  // ================= WALLET (UI only) =================
  const [walletConnected, setWalletConnected] = useState(false);

  // ================= HEALTH STATUS =================
  const [health, setHealth] = useState({
    api: null,
    ipfs: null,
    blockchain: null,
  });

  // ================= CID VERIFICATION =================
  const [verifyCid, setVerifyCid] = useState("");
  const [verifyResult, setVerifyResult] = useState(null);
  const [verifyError, setVerifyError] = useState("");
  const [verifying, setVerifying] = useState(false);

  // ================= UPDATE STATE =================
  const [updateFiles, setUpdateFiles] = useState([]);
  const [updating, setUpdating] = useState(false);
  const [updateStep, setUpdateStep] = useState("");
  const [updateError, setUpdateError] = useState("");

  // Refs for file inputs
  const deployFileInputRef = useRef(null);
  const updateFileInputRef = useRef(null);

  // ================= FETCH HEALTH ON DASHBOARD OPEN =================
  useEffect(() => {
    if (page === "dashboard") {
      apiHealth().then(setHealth);
    }
  }, [page]);

  // ================= AUTH =================
  function handleSubmit(e) {
    e.preventDefault();

    if (authMode === "signup" && !name.trim()) {
      alert("Please enter your name.");
      return;
    }

    if (!email.trim() || !password.trim()) {
      alert("Please enter email and password.");
      return;
    }

    const savedUser = {
      name: name.trim() || "Developer",
      email: email.trim(),
    };

    localStorage.setItem(
      "web3host-user",
      JSON.stringify(savedUser)
    );

    setUser(savedUser);
    setPage("dashboard");
  }

  // ================= LOGOUT =================
  function logout() {
    localStorage.removeItem("web3host-user");
    setUser(null);
    setPage("home");
    setEmail("");
    setPassword("");
    setName("");
  }

  // ================= NEW PROJECT =================
  function openProjectModal() {
    setProjectName("");
    setProjectDescription("");
    setSelectedFiles([]);
<<<<<<< HEAD
    setShowProjectModal(true);
  }

async function createProject() {
  if (!projectName.trim()) {
    alert("Please enter project name.");
    return;
  }

  if (selectedFiles.length === 0) {
    alert("Please select website files.");
    return;
  }

  try {
    const formData = new FormData();

    selectedFiles.forEach((file) => {
      formData.append("files", file);
    });

    const uploadResponse = await fetch(
      "http://127.0.0.1:8000/upload",
      {
        method: "POST",
        body: formData,
      }
    );

    if (!uploadResponse.ok) {
      const error = await uploadResponse.json();
      throw new Error(
        error.detail || "Upload failed"
      );
    }

    const cleanName = projectName
      .toLowerCase()
      .trim()
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9-]/g, "");

    const newProject = {
      id: Date.now(),
      name: projectName.trim(),
      description:
        projectDescription.trim() ||
        "A new Web3Host project.",

      status: "Ready",
      deployment: "Not deployed",

      url: "",

      fileName:
        selectedFiles.length === 1
          ? selectedFiles[0].name
          : `${selectedFiles.length} files`,

      createdAt: new Date().toLocaleString(),
      lastDeployment: "Not deployed",

      visits: 0,

      storage: Math.floor(
        selectedFiles.reduce(
          (total, file) => total + file.size,
          0
        ) / 1024
      ),

      deploymentId: null,
      siteUrl: null,
      cid: null,
      transactionHash: null,
    };

    setProjects((prev) => [
      ...prev,
      newProject,
    ]);

    setShowProjectModal(false);
    setProjectName("");
    setProjectDescription("");
    setSelectedFiles([]);

    addNotification(
      "Project uploaded successfully 🚀"
    );

  } catch (error) {
    console.error(error);
    alert(error.message);
  }
}

=======
    setDeploymentError("");
    setShowProjectModal(true);
  }

>>>>>>> main
  // ================= NOTIFICATION =================
  function addNotification(message) {
    const notification = {
      id: Date.now(),
      message,
      time: new Date().toLocaleTimeString(),
    };

    setNotifications((prev) => [notification, ...prev]);
  }

<<<<<<< HEAD
  // ================= DEPLOY =================
async function deployProject(id) {
  setDeployingId(id);
  setDeploymentStep("Creating deployment...");

  try {
    const deployResponse = await fetch(
      "http://127.0.0.1:8000/deploy",
      {
        method: "POST",
      }
    );

    if (!deployResponse.ok) {
      const error = await deployResponse.json();

      throw new Error(
        error.detail ||
        error.message ||
        "Deployment failed"
      );
    }

    const deployment = await deployResponse.json();

    const deploymentId =
      deployment.deployment_id;

    setDeploymentStep(
      "Processing deployment..."
    );

    let currentDeployment = deployment;

    for (let attempt = 0; attempt < 10; attempt++) {
      await new Promise((resolve) =>
        setTimeout(resolve, 500)
      );

      const statusResponse = await fetch(
        `http://127.0.0.1:8000/deploy/${deploymentId}`
      );

      if (!statusResponse.ok) {
        throw new Error(
          "Could not check deployment status"
        );
      }

      currentDeployment =
        await statusResponse.json();

      if (
        currentDeployment.status === "deployed" ||
        currentDeployment.status === "failed"
      ) {
        break;
      }
    }

    if (
      currentDeployment.status === "failed"
    ) {
      throw new Error(
        currentDeployment.message ||
        "Deployment failed"
      );
    }

    const fullSiteUrl =
      "http://127.0.0.1:8000" +
      currentDeployment.site_url;

    setProjects((prev) =>
      prev.map((project) =>
        project.id === id
          ? {
              ...project,
              deployment: "Live",
              status: "Deployed",

              deploymentId:
                currentDeployment.deployment_id,

              siteUrl: fullSiteUrl,
              url: fullSiteUrl,

              cid:
                currentDeployment.cid,

              transactionHash:
                currentDeployment.transaction_hash,

              lastDeployment:
                new Date().toLocaleString(),
            }
          : project
      )
    );

    setDeploymentStep("Deployment complete");

    addNotification(
      "Project deployed successfully 🚀"
    );

    alert(
      "Project deployed successfully!"
    );

  } catch (error) {
    console.error(error);

    setProjects((prev) =>
      prev.map((project) =>
        project.id === id
          ? {
              ...project,
              status: "Failed",
              deployment: "Failed",
            }
          : project
      )
    );

    alert(error.message);

  } finally {
    setDeployingId(null);
    setDeploymentStep("");
=======
  // ================= REAL DEPLOY =================
  /**
   * Deploys a website by:
   * 1. Sending files to POST /publish
   * 2. Backend: saves → IPFS → blockchain
   * 3. Returns website_id, cid, gateway_url
   * 4. Stores result in project state
   */
  async function deployProject(project) {
    if (!project.files || project.files.length === 0) {
      setDeploymentError(
        "No files selected. Please select website files before deploying."
      );
      return;
    }

    setDeployingId(project.id);
    setDeploymentStep("Connecting to backend...");
    setDeploymentError("");

    try {
      // ── Call POST /publish ──────────────────────────────
      const result = await apiPublish(
        project.name,
        project.files,
        (step) => setDeploymentStep(step)
      );

      setDeploymentStep("Deployment complete! ✓");

      // ── Update project state with real blockchain data ──
      setProjects((prev) =>
        prev.map((p) =>
          p.id === project.id
            ? {
                ...p,
                deployment:      "Live",
                status:          "Deployed",
                lastDeployment:  new Date().toLocaleString(),
                // Real data from backend:
                websiteId:       result.website_id,
                cid:             result.cid,
                gatewayUrl:      result.gateway_url,
                transactionHash: result.transaction_hash,
                filesSaved:      result.files_saved,
              }
            : p
        )
      );

      addNotification(
        `🚀 Deployed! Website ID: ${result.website_id} | CID: ${result.cid.substring(0, 16)}...`
      );
    } catch (err) {
      setDeploymentStep("");
      setDeploymentError(
        `Deployment failed: ${err.message}`
      );
      addNotification(`❌ Deployment failed: ${err.message}`);
    } finally {
      setDeployingId(null);
    }
>>>>>>> main
  }
}

  // ================= DELETE =================
  function deleteProject(id) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this project?"
    );

    if (!confirmed) return;

    setProjects((prev) =>
      prev.filter((project) => project.id !== id)
    );

    if (selectedProject && selectedProject.id === id) {
      setSelectedProject(null);
    }

    addNotification("Project deleted.");
  }

  // ================= COPY =================
  function copyText(text) {
    if (!navigator.clipboard) {
      alert(text);
      return;
    }
    navigator.clipboard
      .writeText(text)
      .then(() => addNotification("📋 Copied to clipboard!"))
      .catch(() => alert(text));
  }

  // ================= OPEN PROJECT =================
  function openProjectDetails(project) {
    setSelectedProject(project);
    setVerifyCid(project.cid || "");
    setVerifyResult(null);
    setVerifyError("");
    setUpdateFiles([]);
    setUpdateStep("");
    setUpdateError("");
    setPage("project");
  }

  // ================= RELOAD SELECTED PROJECT =================
  useEffect(() => {
    if (!selectedProject) return;

    const updated = projects.find(
      (project) => project.id === selectedProject.id
    );

    if (updated) setSelectedProject(updated);
  }, [projects]);

  // ================= WALLET (UI) =================
  function connectWallet() {
    setWalletConnected((prev) => !prev);

    if (!walletConnected) {
      addNotification("🔗 Wallet connected.");
    } else {
      addNotification("Wallet disconnected.");
    }
  }

  // ================= SEARCH =================
  const filteredProjects = projects.filter((project) =>
    project.name.toLowerCase().includes(search.toLowerCase())
  );

  // ================= DEPLOYMENT PROGRESS =================
  function getProgress() {
    if (!deployingId) return 0;
    if (deploymentStep.includes("Connecting")) return 10;
    if (deploymentStep.includes("Preparing")) return 25;
    if (deploymentStep.includes("IPFS")) return 55;
    if (deploymentStep.includes("blockchain") || deploymentStep.includes("Blockchain")) return 80;
    if (deploymentStep.includes("complete")) return 100;
    return 15;
  }

  // ================= VERIFY CID =================
  async function handleVerifyCID(project) {
    if (!verifyCid.trim()) {
      setVerifyError("Please enter a CID to verify.");
      return;
    }

    if (!project.websiteId) {
      setVerifyError("Website not yet deployed. Deploy first.");
      return;
    }

    setVerifying(true);
    setVerifyResult(null);
    setVerifyError("");

    try {
      const result = await apiVerifyCID(project.websiteId, verifyCid.trim());
      setVerifyResult(result.verified);
    } catch (err) {
      setVerifyError(`Verification error: ${err.message}`);
    } finally {
      setVerifying(false);
    }
  }

  // ================= UPDATE WEBSITE =================
  async function handleUpdateWebsite(project) {
    if (!project.websiteId) {
      setUpdateError("Website not yet deployed on blockchain.");
      return;
    }

    if (updateFiles.length === 0) {
      setUpdateError("Please select the new website files for update.");
      return;
    }

    setUpdating(true);
    setUpdateStep("Starting update...");
    setUpdateError("");

    try {
      const result = await apiUpdateWebsite(
        project.websiteId,
        project.name,
        updateFiles,
        (step) => setUpdateStep(step)
      );

      setUpdateStep("Update complete! ✓");

      // Store new CID in project state
      setProjects((prev) =>
        prev.map((p) =>
          p.id === project.id
            ? {
                ...p,
                cid:             result.new_cid,
                gatewayUrl:      result.gateway_url,
                transactionHash: result.transaction_hash,
                lastDeployment:  new Date().toLocaleString(),
                filesSaved:      result.files_saved,
              }
            : p
        )
      );

      setVerifyCid(result.new_cid);
      setVerifyResult(null);

      addNotification(
        `🔄 Updated! New CID: ${result.new_cid.substring(0, 16)}...`
      );
    } catch (err) {
      setUpdateStep("");
      setUpdateError(`Update failed: ${err.message}`);
    } finally {
      setUpdating(false);
      setUpdateFiles([]);
      if (updateFileInputRef.current) {
        updateFileInputRef.current.value = "";
      }
    }
  }

  // ================= CREATE PROJECT (store files in state) =================
  function createProject() {
    if (!projectName.trim()) {
      alert("Please enter project name.");
      return;
    }

    if (selectedFiles.length === 0) {
      alert("Please select at least one file.");
      return;
    }

    const newProject = {
      id:          Date.now(),
      name:        projectName.trim(),
      description: projectDescription.trim() || "A WebChain project.",
      status:      "Ready",
      deployment:  "Not deployed",
      // Store the actual File objects so we can send them to the backend
      files:       selectedFiles,
      fileName:    selectedFiles.length === 1
                     ? selectedFiles[0].name
                     : `${selectedFiles.length} files`,
      createdAt:   new Date().toLocaleString(),
      lastDeployment: "Not deployed",
      visits:      0,
      storage:     Array.from(selectedFiles).reduce((s, f) => s + f.size, 0),
      // These will be filled in after deployment:
      websiteId:   null,
      cid:         null,
      gatewayUrl:  null,
      transactionHash: null,
      filesSaved:  [],
    };

    setProjects((prev) => [...prev, newProject]);
    setShowProjectModal(false);
    setProjectName("");
    setProjectDescription("");
    setSelectedFiles([]);
    addNotification("📁 Project created. Click Deploy to publish it.");
  }

  return (
    <div className={darkMode ? "app dark-mode" : "app"}>
      {/* ================= NAVBAR ================= */}

      <nav className="navbar">
        <button className="brand" onClick={() => setPage("home")}>
          <div className="logo">W3</div>

          <div>
            <div className="brand-name">
              Web3<span>Host</span>
            </div>

            <div className="brand-subtitle">
              DECENTRALIZED HOSTING
            </div>
          </div>
        </button>

        <div className="nav-links">
          {page === "home" && (
            <>
              <a href="#features">Features</a>
              <a href="#about">About</a>

              <button
                className="wallet-button"
                onClick={connectWallet}
              >
                🔗{" "}
                {walletConnected ? "Connected" : "Connect Wallet"}
              </button>

              <button
                className="nav-button"
                onClick={() => {
                  setAuthMode("login");
                  setPage("auth");
                }}
              >
                Login
              </button>
            </>
          )}

          {page !== "home" && (
            <button
              className="nav-button"
              onClick={() => setPage("dashboard")}
            >
              Dashboard
            </button>
          )}

          {user && page === "dashboard" && (
            <button className="nav-button" onClick={logout}>
              Logout
            </button>
          )}

          <button
            className="theme-button"
            onClick={() => setDarkMode(!darkMode)}
            aria-label="Toggle theme"
          >
            {darkMode ? "☀️" : "🌙"}
          </button>
        </div>
      </nav>

      {/* ================= HOME ================= */}

      {page === "home" && (
        <>
          <section className="hero">
            <div className="hero-badge">
              ✦ Next Generation Web Hosting
            </div>

            <h1>
              Build.
              <span> Deploy.</span>
              <br />
              <strong>Host the Future.</strong>
            </h1>

            <p>
              Web3Host is a modern hosting platform
              designed for developers to upload,
              deploy and manage websites with a
              fast, secure and Web3-ready experience.
            </p>

            <div className="hero-buttons">
              <button
                className="primary-button"
                onClick={() => {
                  setAuthMode("signup");
                  setPage("auth");
                }}
              >
                🚀 Start Deploying
              </button>

              <a href="#features" className="secondary-button">
                Explore Features
              </a>
            </div>

            <div className="hero-glow"></div>
          </section>

          {/* STATS */}
          <section className="stats">
            <div>
              <h2>100%</h2>
              <p>Decentralized</p>
            </div>
            <div>
              <h2>⚡ IPFS</h2>
              <p>Powered</p>
            </div>
            <div>
              <h2>🔐 On-Chain</h2>
              <p>Registry</p>
            </div>
            <div>
              <h2>🌍 Global</h2>
              <p>Accessibility</p>
            </div>
          </section>

          {/* FEATURES */}
          <section id="features" className="section">
            <div className="section-heading">
              <p>WHY WEB3HOST</p>
              <h2>Powerful Hosting Experience</h2>
              <span>
                Everything you need to build and
                deploy modern websites.
              </span>
            </div>

            <div className="feature-grid">
              <Feature icon="⚡" title="Lightning Fast" text="Deploy your websites to IPFS with a developer-friendly workflow." />
              <Feature icon="🛡️" title="Immutable" text="Your website content is cryptographically verified on the blockchain." />
              <Feature icon="🌎" title="Global" text="IPFS distributes your content globally via a peer-to-peer network." />
              <Feature icon="🔗" title="Web3 Ready" text="Built on IPFS and Ethereum — fully decentralized hosting." />
              <Feature icon="📦" title="Easy Deployment" text="Upload your project and manage deployments from one dashboard." />
              <Feature icon="🔍" title="CID Verification" text="Verify your website content against the blockchain registry." />
              <Feature icon="🔔" title="Notifications" text="Stay updated about your projects and deployments." />
              <Feature icon="👤" title="Developer Profile" text="Manage your Web3Host account from one place." />
              <Feature icon="🔐" title="Owner Updates" text="Only the website owner can update the CID on-chain." />
              <Feature icon="🌙" title="Dark Mode" text="Switch between light and dark themes." />
              <Feature icon="🔍" title="Project Search" text="Find your projects quickly from the dashboard." />
              <Feature icon="🔄" title="Version Updates" text="Deploy new versions and update the blockchain registry." />
            </div>
          </section>

          {/* ABOUT */}
          <section id="about" className="about">
            <div className="about-content">
              <p className="pink-label">BUILT FOR DEVELOPERS</p>

              <h2>
                One Platform.
                <br />
                <span>Infinite Possibilities.</span>
              </h2>

              <p>
                Upload your project, deploy it to IPFS,
                and register it on the blockchain.
                Web3Host brings modern hosting and
                decentralized technology together.
              </p>

              <button
                className="primary-button"
                onClick={() => {
                  setAuthMode("signup");
                  setPage("auth");
                }}
              >
                Get Started →
              </button>
            </div>

            <div className="about-card">
              <div className="terminal-top">
                <span></span>
                <span></span>
                <span></span>
              </div>

              <div className="terminal-content">
                <p>
                  <span>$</span> web3host deploy ./my-site/
                </p>
                <p className="terminal-muted">
                  Uploading to IPFS...
                </p>
                <p className="terminal-success">
                  ✓ CID: QmXvZ9...
                </p>
                <p className="terminal-muted">
                  Registering on blockchain...
                </p>
                <p className="terminal-success">
                  ✓ Website ID: 1
                </p>
                <p className="terminal-muted">
                  Your website is live 🚀
                </p>
              </div>
            </div>
          </section>

          {/* FOOTER */}
          <footer>
            <div>
              <strong>Web3Host</strong>
              <p>Decentralized hosting for the modern web.</p>
            </div>
            <p>© 2026 Web3Host. All rights reserved.</p>
          </footer>
        </>
      )}

      {/* ================= AUTH ================= */}

      {page === "auth" && (
        <section className="auth-page">
          <div className="auth-card">
            <div className="auth-logo">W3</div>

            <h2>
              {authMode === "login" ? "Welcome Back" : "Create Account"}
            </h2>

            <p className="auth-subtitle">
              {authMode === "login"
                ? "Login to your Web3Host account"
                : "Create your Web3Host account"}
            </p>

            <form onSubmit={handleSubmit}>
              {authMode === "signup" && (
                <Input
                  label="Full Name"
                  type="text"
                  placeholder="Your name"
                  value={name}
                  setValue={setName}
                />
              )}

              <Input
                label="Email"
                type="email"
                placeholder="you@example.com"
                value={email}
                setValue={setEmail}
              />

              <div className="input-group">
                <label>Password</label>

                <div className="password-box">
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />

                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
              </div>

              <button type="submit" className="primary-button full">
                {authMode === "login" ? "Login →" : "Create Account →"}
              </button>
            </form>

            <div className="switch-auth">
              {authMode === "login"
                ? "Don't have an account?"
                : "Already have an account?"}

              <button
                onClick={() =>
                  setAuthMode(authMode === "login" ? "signup" : "login")
                }
              >
                {authMode === "login" ? "Sign Up" : "Login"}
              </button>
            </div>

            <button
              className="back-button"
              onClick={() => setPage("home")}
            >
              ← Back to Home
            </button>
          </div>
        </section>
      )}

      {/* ================= DASHBOARD ================= */}

      {page === "dashboard" && (
        <section className="dashboard">
          <div className="dashboard-header">
            <div>
              <p className="pink-label">DASHBOARD</p>

              <h1>
                Welcome back{" "}
                {user?.name ? user.name : "Developer"} 👋
              </h1>

              <p>
                Manage your decentralized projects.
              </p>
            </div>

            <button
              className="primary-button"
              onClick={openProjectModal}
            >
              + New Project
            </button>
          </div>

          {/* ──── HEALTH STATUS ──── */}
          <div className="health-bar">
            <HealthDot
              label="API"
              status={health.api}
            />
            <HealthDot
              label="IPFS"
              status={health.ipfs}
            />
            <HealthDot
              label="Blockchain"
              status={health.blockchain}
            />
            <button
              className="outline-button small"
              onClick={() => apiHealth().then(setHealth)}
            >
              ↻ Refresh Status
            </button>
          </div>

          {/* DASHBOARD STATS */}
          <div className="dashboard-grid">
            <DashboardCard
              icon="📁"
              title="Projects"
              value={projects.length}
            />

            <DashboardCard
              icon="🚀"
              title="Deployed"
              value={
                projects.filter((p) => p.deployment === "Live").length
              }
            />

            <DashboardCard
              icon="🔗"
              title="On-Chain"
              value={
                projects.filter((p) => p.websiteId).length
              }
            />

            <DashboardCard
              icon="🟢"
              title="IPFS Status"
              value={
                health.ipfs === null
                  ? "Checking..."
                  : health.ipfs
                  ? "Online"
                  : "Offline"
              }
            />
          </div>

          {/* NOTIFICATIONS */}
          {notifications.length > 0 && (
            <div className="notification-panel">
              <div className="projects-heading">
                <div>
                  <h2>🔔 Notifications</h2>
                  <p>Recent project activity</p>
                </div>
              </div>

              {notifications.slice(0, 4).map((notification) => (
                <div
                  className="notification-item"
                  key={notification.id}
                >
                  <span>{notification.message}</span>
                  <small>{notification.time}</small>
                </div>
              ))}
            </div>
          )}

          {/* PROJECTS */}
          <div className="projects-section">
            <div className="projects-heading">
              <div>
                <h2>Your Projects</h2>
                <p>Create and manage your websites.</p>
              </div>

              <button
                className="outline-button"
                onClick={openProjectModal}
              >
                + Add Project
              </button>
            </div>

            {projects.length > 0 && (
              <div className="project-search">
                <input
                  type="text"
                  placeholder="🔍 Search projects..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
            )}

            {projects.length === 0 ? (
              <div className="empty-project">
                <div className="empty-icon">📦</div>
                <h3>No projects yet</h3>
                <p>Create your first project and start deploying.</p>
                <button
                  className="primary-button"
                  onClick={openProjectModal}
                >
                  Create First Project
                </button>
              </div>
            ) : filteredProjects.length === 0 ? (
              <div className="empty-project">
                <div className="empty-icon">🔍</div>
                <h3>No project found</h3>
                <p>Try searching with another name.</p>
              </div>
            ) : (
              <div className="project-list">
                {filteredProjects.map((project) => (
                  <div
                    className="project-card"
                    key={project.id}
                  >
                    <div className="project-icon">🌐</div>

                    <div className="project-info">
                      <h3>{project.name}</h3>
                      <p>{project.description}</p>
                      <small>
                        📦 {project.fileName}
                      </small>

                      {/* Show real CID when deployed */}
                      {project.cid && (
                        <div className="live-url" style={{ wordBreak: "break-all", fontSize: "0.75rem" }}>
                          🔗 CID: {project.cid.substring(0, 20)}...
                        </div>
                      )}

                      {/* IPFS gateway link */}
                      {project.gatewayUrl && project.deployment === "Live" && (
                        <div className="live-url">
                          🌐{" "}
                          <a
                            href={project.gatewayUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ color: "inherit" }}
                          >
                            View on IPFS
                          </a>
                        </div>
                      )}
                    </div>

                    <span
                      className={
                        project.deployment === "Live"
                          ? "status live-status"
                          : "status"
                      }
                    >
                      ●{" "}
                      {project.deployment === "Live" ? "Live" : "Ready"}
                    </span>

                    <button
                      className="outline-button"
                      onClick={() => openProjectDetails(project)}
                    >
                      Details
                    </button>

                    {project.deployment === "Live" && (
                      <button
                        className="copy-button"
                        onClick={() => copyText(project.cid || "")}
                      >
                        Copy CID
                      </button>
                    )}

                    {/* Real deploy button */}
                    <button
                      className="deploy-button"
                      disabled={deployingId === project.id}
                      onClick={() => deployProject(project)}
                    >
                      {deployingId === project.id
                        ? "Deploying..."
                        : project.deployment === "Live"
                        ? "Redeploy"
                        : "Deploy"}
                    </button>

                    <button
                      className="delete-button"
                      onClick={() => deleteProject(project.id)}
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* DEPLOYMENT PROGRESS + ERRORS */}
          {deployingId && (
            <div className="deployment-panel">
              <h2>🚀 Deployment in progress</h2>
              <p>{deploymentStep}</p>

              <div className="progress-track">
                <div
                  className="progress-bar"
                  style={{ width: getProgress() + "%" }}
                ></div>
              </div>

              <span>{getProgress()}%</span>
            </div>
          )}

          {deploymentError && (
            <div
              className="deployment-panel"
              style={{ borderColor: "#ff4444", background: "rgba(255,68,68,0.08)" }}
            >
              <h2>❌ Deployment Error</h2>
              <p style={{ color: "#ff4444" }}>{deploymentError}</p>
              <button
                className="outline-button"
                onClick={() => setDeploymentError("")}
                style={{ marginTop: "0.5rem" }}
              >
                Dismiss
              </button>
            </div>
          )}
        </section>
      )}

      {/* ================= PROJECT DETAILS ================= */}

      {page === "project" && selectedProject && (
        <section className="project-details-page">
          <button
            className="back-button"
            onClick={() => setPage("dashboard")}
          >
            ← Back to Dashboard
          </button>

          <div className="project-details-header">
            <div>
              <p className="pink-label">PROJECT DETAILS</p>
              <h1>{selectedProject.name}</h1>
              <p>{selectedProject.description}</p>
            </div>

            <div
              className={
                selectedProject.deployment === "Live"
                  ? "status live-status large-status"
                  : "status large-status"
              }
            >
              ●{" "}
              {selectedProject.deployment === "Live" ? "Live" : "Ready"}
            </div>
          </div>

          {/* ──── DETAILS GRID ──── */}
          <div className="details-grid">

            {/* Website ID */}
            <div className="details-card">
              <span>🔢 Website ID</span>
              <strong>
                {selectedProject.websiteId != null
                  ? `#${selectedProject.websiteId}`
                  : "Not deployed yet"}
              </strong>
            </div>

            {/* IPFS CID */}
            <div className="details-card">
              <span>🔗 IPFS CID</span>
              <strong style={{ wordBreak: "break-all", fontSize: "0.8rem" }}>
                {selectedProject.cid || "Not deployed yet"}
              </strong>
              {selectedProject.cid && (
                <button
                  className="copy-button"
                  onClick={() => copyText(selectedProject.cid)}
                  style={{ marginTop: "0.4rem" }}
                >
                  Copy CID
                </button>
              )}
            </div>

            {/* IPFS Gateway Link */}
            <div className="details-card">
              <span>🌐 IPFS Gateway</span>
              <strong>
                {selectedProject.gatewayUrl ? (
                  <a
                    href={selectedProject.gatewayUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: "#a78bfa", wordBreak: "break-all", fontSize: "0.8rem" }}
                  >
                    {selectedProject.gatewayUrl}
                  </a>
                ) : "Not deployed yet"}
              </strong>
            </div>

            {/* Created */}
            <div className="details-card">
              <span>📅 Created</span>
              <strong>{selectedProject.createdAt}</strong>
            </div>

            {/* Last Deployment */}
            <div className="details-card">
              <span>🚀 Last Deployment</span>
              <strong>{selectedProject.lastDeployment}</strong>
            </div>

            {/* Files */}
            <div className="details-card">
              <span>📦 Files Deployed</span>
              <strong>
                {selectedProject.filesSaved?.length > 0
                  ? selectedProject.filesSaved.join(", ")
                  : selectedProject.fileName}
              </strong>
            </div>

            {/* Transaction Hash */}
            {selectedProject.transactionHash && (
              <div className="details-card">
                <span>⛓️ Tx Hash</span>
                <strong style={{ wordBreak: "break-all", fontSize: "0.75rem" }}>
                  {selectedProject.transactionHash}
                </strong>
              </div>
            )}
          </div>

          {/* ──── DEPLOY BUTTON ──── */}
          <div className="project-actions">
            <button
              className="primary-button"
              disabled={deployingId === selectedProject.id}
              onClick={() => deployProject(selectedProject)}
            >
              {deployingId === selectedProject.id
                ? "Deploying..."
                : selectedProject.deployment === "Live"
                ? "🔄 Redeploy"
                : "🚀 Deploy Project"}
            </button>

            <button
              className="delete-button"
              onClick={() => deleteProject(selectedProject.id)}
            >
              🗑️ Delete Project
            </button>
          </div>

          {deployingId === selectedProject.id && (
            <div className="deployment-panel">
              <h2>Deployment Progress</h2>
              <p>{deploymentStep}</p>
              <div className="progress-track">
                <div
                  className="progress-bar"
                  style={{ width: getProgress() + "%" }}
                ></div>
              </div>
              <span>{getProgress()}%</span>
            </div>
          )}

          {deploymentError && (
            <div
              className="deployment-panel"
              style={{ borderColor: "#ff4444", background: "rgba(255,68,68,0.08)" }}
            >
              <p style={{ color: "#ff4444" }}>{deploymentError}</p>
            </div>
          )}

          {/* ──── CID VERIFICATION ──── */}
          {selectedProject.deployment === "Live" && (
            <div className="deployment-panel" style={{ marginTop: "1.5rem" }}>
              <h2>🔍 Verify CID Against Blockchain</h2>
              <p style={{ marginBottom: "1rem", opacity: 0.7 }}>
                Enter any CID to check if it matches what's stored on-chain for Website #{selectedProject.websiteId}.
              </p>

              <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", flexWrap: "wrap" }}>
                <input
                  type="text"
                  placeholder="Paste a CID to verify..."
                  value={verifyCid}
                  onChange={(e) => {
                    setVerifyCid(e.target.value);
                    setVerifyResult(null);
                    setVerifyError("");
                  }}
                  style={{
                    flex: 1,
                    minWidth: "200px",
                    padding: "0.6rem 1rem",
                    borderRadius: "8px",
                    border: "1px solid rgba(255,255,255,0.15)",
                    background: "rgba(255,255,255,0.05)",
                    color: "inherit",
                    fontSize: "0.875rem",
                  }}
                />

                <button
                  className="outline-button"
                  onClick={() => handleVerifyCID(selectedProject)}
                  disabled={verifying}
                >
                  {verifying ? "Verifying..." : "Verify CID"}
                </button>

                {/* Quick-fill with current CID */}
                {selectedProject.cid && (
                  <button
                    className="copy-button"
                    onClick={() => setVerifyCid(selectedProject.cid)}
                  >
                    Use Current CID
                  </button>
                )}
              </div>

              {verifyResult === true && (
                <div style={{ marginTop: "1rem", color: "#4ade80", fontWeight: "bold" }}>
                  ✅ Verified! CID matches the blockchain record.
                </div>
              )}

              {verifyResult === false && (
                <div style={{ marginTop: "1rem", color: "#f87171", fontWeight: "bold" }}>
                  ❌ Mismatch! This CID does NOT match the blockchain record.
                </div>
              )}

              {verifyError && (
                <div style={{ marginTop: "1rem", color: "#f87171" }}>
                  ⚠️ {verifyError}
                </div>
              )}
            </div>
          )}

          {/* ──── UPDATE WEBSITE ──── */}
          {selectedProject.websiteId != null && (
            <div className="deployment-panel" style={{ marginTop: "1.5rem" }}>
              <h2>🔄 Update Website</h2>
              <p style={{ marginBottom: "1rem", opacity: 0.7 }}>
                Upload a new version. A new IPFS CID will be generated and the blockchain record will be updated (owner-only).
              </p>

              <div className="upload-box" style={{ marginBottom: "1rem" }}>
                <input
                  ref={updateFileInputRef}
                  type="file"
                  multiple
                  onChange={(e) => {
                    setUpdateFiles(Array.from(e.target.files || []));
                    setUpdateError("");
                    setUpdateStep("");
                  }}
                  style={{ display: "block", marginBottom: "0.5rem" }}
                />

                {updateFiles.length > 0 && (
                  <div className="selected-file">
                    ✓ {updateFiles.length} file{updateFiles.length > 1 ? "s" : ""} selected:{" "}
                    {updateFiles.slice(0, 3).map(f => f.name).join(", ")}
                    {updateFiles.length > 3 && `... +${updateFiles.length - 3} more`}
                  </div>
                )}
              </div>

              <button
                className="primary-button"
                onClick={() => handleUpdateWebsite(selectedProject)}
                disabled={updating || updateFiles.length === 0}
              >
                {updating ? updateStep || "Updating..." : "🔄 Deploy Update"}
              </button>

              {updateStep && !updating && (
                <div style={{ marginTop: "0.75rem", color: "#4ade80" }}>
                  ✅ {updateStep}
                </div>
              )}

              {updateError && (
                <div style={{ marginTop: "0.75rem", color: "#f87171" }}>
                  ❌ {updateError}
                </div>
              )}
            </div>
          )}
        </section>
      )}

      {/* ================= NEW PROJECT MODAL ================= */}

      {showProjectModal && (
        <div
          className="modal-overlay"
          onClick={() => setShowProjectModal(false)}
        >
          <div
            className="project-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="modal-close"
              onClick={() => setShowProjectModal(false)}
            >
              ×
            </button>

            <div className="modal-icon">🚀</div>

            <h2>Create New Project</h2>

            <p className="modal-subtitle">
              Add your website files and deploy to IPFS + blockchain.
            </p>

            <div className="input-group">
              <label>Project Name</label>
              <input
                type="text"
                placeholder="my-awesome-website"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
              />
            </div>

            <div className="input-group">
              <label>Description</label>
              <textarea
                className="project-textarea"
                placeholder="Describe your project..."
                value={projectDescription}
                onChange={(e) =>
                  setProjectDescription(e.target.value)
                }
              ></textarea>
            </div>

            {/* FILE UPLOAD — supports multiple files */}
            <div className="upload-box">
              <div className="upload-icon">📦</div>

              <h3>Upload Project Files</h3>

              <p>Select all your website files (HTML, CSS, JS, images)</p>

              <label className="upload-button">
                Choose Files

<<<<<<< HEAD
              <input
  		type="file"
  		multiple
  		onChange={(e) =>
    		  setSelectedFiles(
      		    Array.from(e.target.files)
    		  )
  		}
	      />
              </label>

              {selectedFiles.length > 0 && (
  		<div className="selected-file">
    		  ✓ {selectedFiles.length} file(s) selected
  		</div>
	      )}
=======
                <input
                  ref={deployFileInputRef}
                  type="file"
                  multiple
                  onChange={(e) => {
                    setSelectedFiles(Array.from(e.target.files || []));
                  }}
                />
              </label>

              {selectedFiles.length > 0 && (
                <div className="selected-file">
                  ✓ {selectedFiles.length} file
                  {selectedFiles.length > 1 ? "s" : ""} selected:{" "}
                  {selectedFiles
                    .slice(0, 3)
                    .map((f) => f.name)
                    .join(", ")}
                  {selectedFiles.length > 3 &&
                    ` ... +${selectedFiles.length - 3} more`}
                </div>
              )}

              <p style={{ fontSize: "0.75rem", opacity: 0.5, marginTop: "0.5rem" }}>
                Supported: .html .css .js .png .jpg .svg .ico .woff .ttf
              </p>
>>>>>>> main
            </div>

            <button
              className="primary-button full"
              onClick={createProject}
            >
              Create Project →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ================= REUSABLE COMPONENTS =================

function Input({ label, type, placeholder, value, setValue }) {
  return (
    <div className="input-group">
      <label>{label}</label>
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
    </div>
  );
}

function Feature({ icon, title, text }) {
  return (
    <div className="feature-card">
      <div className="feature-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{text}</p>
    </div>
  );
}

function DashboardCard({ icon, title, value }) {
  return (
    <div className="dashboard-card">
      <div className="dashboard-card-icon">{icon}</div>
      <p>{title}</p>
      <h2>{value}</h2>
    </div>
  );
}

/**
 * A small colored dot + label showing service health.
 * status: null = loading, true = ok, false = down
 */
function HealthDot({ label, status }) {
  const color =
    status === null ? "#888" : status ? "#4ade80" : "#f87171";
  const dot =
    status === null ? "○" : status ? "●" : "●";

  return (
    <span style={{ display: "flex", alignItems: "center", gap: "0.3rem", fontSize: "0.85rem" }}>
      <span style={{ color }}>{dot}</span>
      <span>{label}</span>
    </span>
  );
}

export default App;