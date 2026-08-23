import { useEffect, useState } from "react";
import "./index.css";

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

  const [deployingId, setDeployingId] = useState(null);
  const [deploymentStep, setDeploymentStep] = useState("");

  // ================= PROJECT DETAILS =================
  const [selectedProject, setSelectedProject] = useState(null);

  // ================= NOTIFICATIONS =================
  const [notifications, setNotifications] = useState([]);

  // ================= WALLET =================
  const [walletConnected, setWalletConnected] = useState(false);

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

  // ================= NOTIFICATION =================
  function addNotification(message) {
    const notification = {
      id: Date.now(),
      message,
      time: new Date().toLocaleTimeString(),
    };

    setNotifications((prev) => [
      notification,
      ...prev,
    ]);
  }

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

    if (
      selectedProject &&
      selectedProject.id === id
    ) {
      setSelectedProject(null);
    }

    addNotification("Project deleted.");
  }

  // ================= COPY URL =================
  function copyUrl(url) {
    if (!navigator.clipboard) {
      alert(url);
      return;
    }

    navigator.clipboard
      .writeText(url)
      .then(() => {
        alert("🔗 Project URL copied!");
      })
      .catch(() => {
        alert(url);
      });
  }

  // ================= OPEN PROJECT =================
  function openProjectDetails(project) {
    setSelectedProject(project);
    setPage("project");
  }

  // ================= RELOAD SELECTED PROJECT =================
  useEffect(() => {
    if (!selectedProject) return;

    const updated = projects.find(
      (project) => project.id === selectedProject.id
    );

    if (updated) {
      setSelectedProject(updated);
    }
  }, [projects]);

  // ================= WALLET =================
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
    project.name
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  // ================= DEPLOYMENT PROGRESS =================
  function getProgress() {
    if (!deployingId) return 0;

    if (deploymentStep === "Preparing project...")
      return 20;

    if (deploymentStep === "Uploading files...")
      return 45;

    if (deploymentStep === "Building project...")
      return 70;

    if (
      deploymentStep ===
      "Deploying to Web3Host..."
    )
      return 90;

    return 10;
  }

  return (
    <div
      className={
        darkMode
          ? "app dark-mode"
          : "app"
      }
    >
      {/* ================= NAVBAR ================= */}

      <nav className="navbar">
        <button
          className="brand"
          onClick={() => setPage("home")}
        >
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
                {walletConnected
                  ? "Connected"
                  : "Connect Wallet"}
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
            <button
              className="nav-button"
              onClick={logout}
            >
              Logout
            </button>
          )}

          <button
            className="theme-button"
            onClick={() =>
              setDarkMode(!darkMode)
            }
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

              <a
                href="#features"
                className="secondary-button"
              >
                Explore Features
              </a>
            </div>

            <div className="hero-glow"></div>
          </section>

          {/* ================= STATS ================= */}

          <section className="stats">
            <div>
              <h2>99.9%</h2>
              <p>Uptime</p>
            </div>

            <div>
              <h2>⚡ Fast</h2>
              <p>Deployment</p>
            </div>

            <div>
              <h2>🔐 Secure</h2>
              <p>Infrastructure</p>
            </div>

            <div>
              <h2>🌍 Global</h2>
              <p>Accessibility</p>
            </div>
          </section>

          {/* ================= FEATURES ================= */}

          <section
            id="features"
            className="section"
          >
            <div className="section-heading">
              <p>WHY WEB3HOST</p>

              <h2>
                Powerful Hosting Experience
              </h2>

              <span>
                Everything you need to build and
                deploy modern websites.
              </span>
            </div>

            <div className="feature-grid">
              <Feature
                icon="⚡"
                title="Lightning Fast"
                text="Deploy your websites quickly with a developer-friendly workflow."
              />

              <Feature
                icon="🛡️"
                title="Secure"
                text="Your projects are protected with security-focused infrastructure."
              />

              <Feature
                icon="🌎"
                title="Global"
                text="Make your applications accessible from anywhere in the world."
              />

              <Feature
                icon="🔗"
                title="Web3 Ready"
                text="Built with the future of decentralized applications in mind."
              />

              <Feature
                icon="📦"
                title="Easy Deployment"
                text="Upload your project and manage deployments from one dashboard."
              />

              <Feature
                icon="📊"
                title="Analytics"
                text="Monitor deployments, visits, storage and project activity."
              />

              <Feature
                icon="🔔"
                title="Notifications"
                text="Stay updated about your projects and deployments."
              />

              <Feature
                icon="👤"
                title="Developer Profile"
                text="Manage your Web3Host account from one place."
              />

              <Feature
                icon="🔐"
                title="Authentication"
                text="Secure login and signup experience for developers."
              />

              <Feature
                icon="🌙"
                title="Dark Mode"
                text="Switch between light and dark themes for a better developer experience."
              />

              <Feature
                icon="🔍"
                title="Project Search"
                text="Find your projects quickly from the dashboard."
              />

              <Feature
                icon="💾"
                title="Local Project Storage"
                text="Project information is preserved using browser local storage."
              />
            </div>
          </section>

          {/* ================= ABOUT ================= */}

          <section
            id="about"
            className="about"
          >
            <div className="about-content">
              <p className="pink-label">
                BUILT FOR DEVELOPERS
              </p>

              <h2>
                One Platform.
                <br />
                <span>
                  Infinite Possibilities.
                </span>
              </h2>

              <p>
                Upload your project, deploy it
                and manage everything from one
                simple platform. Web3Host brings
                modern hosting and decentralized
                technology together.
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
                  <span>$</span> web3host deploy
                </p>

                <p className="terminal-muted">
                  Uploading project...
                </p>

                <p className="terminal-success">
                  ✓ Project deployed successfully
                </p>

                <p className="terminal-muted">
                  Your website is live 🚀
                </p>
              </div>
            </div>
          </section>

          {/* ================= FOOTER ================= */}

          <footer>
            <div>
              <strong>Web3Host</strong>

              <p>
                Decentralized hosting for the modern
                web.
              </p>
            </div>

            <p>
              © 2026 Web3Host. All rights reserved.
            </p>
          </footer>
        </>
      )}

      {/* ================= AUTH ================= */}

      {page === "auth" && (
        <section className="auth-page">
          <div className="auth-card">
            <div className="auth-logo">
              W3
            </div>

            <h2>
              {authMode === "login"
                ? "Welcome Back"
                : "Create Account"}
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
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) =>
                      setPassword(
                        e.target.value
                      )
                    }
                  />

                  <button
                    type="button"
                    onClick={() =>
                      setShowPassword(
                        !showPassword
                      )
                    }
                  >
                    {showPassword
                      ? "Hide"
                      : "Show"}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                className="primary-button full"
              >
                {authMode === "login"
                  ? "Login →"
                  : "Create Account →"}
              </button>
            </form>

            <div className="switch-auth">
              {authMode === "login"
                ? "Don't have an account?"
                : "Already have an account?"}

              <button
                onClick={() =>
                  setAuthMode(
                    authMode === "login"
                      ? "signup"
                      : "login"
                  )
                }
              >
                {authMode === "login"
                  ? "Sign Up"
                  : "Login"}
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
              <p className="pink-label">
                DASHBOARD
              </p>

              <h1>
                Welcome back{" "}
                {user?.name
                  ? user.name
                  : "Developer"}{" "}
                👋
              </h1>

              <p>
                Manage your projects and
                deployments from one place.
              </p>
            </div>

            <button
              className="primary-button"
              onClick={openProjectModal}
            >
              + New Project
            </button>
          </div>

          {/* ================= DASHBOARD STATS ================= */}

          <div className="dashboard-grid">
            <DashboardCard
              icon="📁"
              title="Projects"
              value={projects.length}
            />

            <DashboardCard
              icon="🚀"
              title="Deployments"
              value={
                projects.filter(
                  (p) =>
                    p.deployment === "Live"
                ).length
              }
            />

            <DashboardCard
              icon="💾"
              title="Storage"
              value={
                projects.length > 0
                  ? projects.length * 25 +
                  " MB"
                  : "0 MB"
              }
            />

            <DashboardCard
              icon="🟢"
              title="System Status"
              value="Active"
            />
          </div>

          {/* ================= NOTIFICATIONS ================= */}

          {notifications.length > 0 && (
            <div className="notification-panel">
              <div className="projects-heading">
                <div>
                  <h2>🔔 Notifications</h2>
                  <p>
                    Recent project activity
                  </p>
                </div>
              </div>

              {notifications
                .slice(0, 4)
                .map((notification) => (
                  <div
                    className="notification-item"
                    key={notification.id}
                  >
                    <span>
                      {notification.message}
                    </span>

                    <small>
                      {notification.time}
                    </small>
                  </div>
                ))}
            </div>
          )}

          {/* ================= PROJECTS ================= */}

          <div className="projects-section">
            <div className="projects-heading">
              <div>
                <h2>Your Projects</h2>

                <p>
                  Create and manage your
                  websites.
                </p>
              </div>

              <button
                className="outline-button"
                onClick={openProjectModal}
              >
                + Add Project
              </button>
            </div>

            {/* SEARCH */}

            {projects.length > 0 && (
              <div className="project-search">
                <input
                  type="text"
                  placeholder="🔍 Search projects..."
                  value={search}
                  onChange={(e) =>
                    setSearch(e.target.value)
                  }
                />
              </div>
            )}

            {/* EMPTY */}

            {projects.length === 0 ? (
              <div className="empty-project">
                <div className="empty-icon">
                  📦
                </div>

                <h3>
                  No projects yet
                </h3>

                <p>
                  Create your first project and
                  start deploying.
                </p>

                <button
                  className="primary-button"
                  onClick={openProjectModal}
                >
                  Create First Project
                </button>
              </div>
            ) : filteredProjects.length ===
              0 ? (
              <div className="empty-project">
                <div className="empty-icon">
                  🔍
                </div>

                <h3>
                  No project found
                </h3>

                <p>
                  Try searching with another
                  name.
                </p>
              </div>
            ) : (
              <div className="project-list">
                {filteredProjects.map(
                  (project) => (
                    <div
                      className="project-card"
                      key={project.id}
                    >
                      <div className="project-icon">
                        🌐
                      </div>

                      <div className="project-info">
                        <h3>
                          {project.name}
                        </h3>

                        <p>
                          {project.description}
                        </p>

                        <small>
                          📦{" "}
                          {project.fileName}
                        </small>

                        {project.deployment ===
                          "Live" && (
                            <div className="live-url">
                              🌐 {project.url}
                            </div>
                          )}
                      </div>

                      <span
                        className={
                          project.deployment ===
                            "Live"
                            ? "status live-status"
                            : "status"
                        }
                      >
                        ●{" "}
                        {project.deployment ===
                          "Live"
                          ? "Live"
                          : "Ready"}
                      </span>

                      <button
                        className="outline-button"
                        onClick={() =>
                          openProjectDetails(
                            project
                          )
                        }
                      >
                        Details
                      </button>

                      {project.deployment ===
                        "Live" && (
                          <button
                            className="copy-button"
                            onClick={() =>
                              copyUrl(
                                project.url
                              )
                            }
                          >
                            Copy URL
                          </button>
                        )}

                      <button
                        className="deploy-button"
                        disabled={
                          deployingId ===
                          project.id
                        }
                        onClick={() =>
                          deployProject(
                            project.id
                          )
                        }
                      >
                        {deployingId ===
                          project.id
                          ? "Deploying..."
                          : project.deployment ===
                            "Live"
                            ? "Redeploy"
                            : "Deploy"}
                      </button>

                      <button
                        className="delete-button"
                        onClick={() =>
                          deleteProject(
                            project.id
                          )
                        }
                      >
                        Delete
                      </button>
                    </div>
                  )
                )}
              </div>
            )}
          </div>

          {/* ================= DEPLOYMENT PROGRESS ================= */}

          {deployingId && (
            <div className="deployment-panel">
              <h2>
                🚀 Deployment in progress
              </h2>

              <p>
                {deploymentStep}
              </p>

              <div className="progress-track">
                <div
                  className="progress-bar"
                  style={{
                    width:
                      getProgress() + "%",
                  }}
                ></div>
              </div>

              <span>
                {getProgress()}%
              </span>
            </div>
          )}
        </section>
      )}

      {/* ================= PROJECT DETAILS ================= */}

      {page === "project" &&
        selectedProject && (
          <section className="project-details-page">
            <button
              className="back-button"
              onClick={() =>
                setPage("dashboard")
              }
            >
              ← Back to Dashboard
            </button>

            <div className="project-details-header">
              <div>
                <p className="pink-label">
                  PROJECT DETAILS
                </p>

                <h1>
                  {selectedProject.name}
                </h1>

                <p>
                  {selectedProject.description}
                </p>
              </div>

              <div
                className={
                  selectedProject.deployment ===
                    "Live"
                    ? "status live-status large-status"
                    : "status large-status"
                }
              >
                ●{" "}
                {selectedProject.deployment ===
                  "Live"
                  ? "Live"
                  : "Ready"}
              </div>
            </div>

            <div className="details-grid">
              <div className="details-card">
                <span>🌐 Live URL</span>

                <strong>
                  {selectedProject.url}
                </strong>

                {selectedProject.deployment ===
                  "Live" && (
                    <button
                      className="copy-button"
                      onClick={() =>
                        copyUrl(
                          selectedProject.url
                        )
                      }
                    >
                      Copy URL
                    </button>
                  )}
              </div>

              <div className="details-card">
                <span>📦 Project File</span>

                <strong>
                  {selectedProject.fileName}
                </strong>
              </div>

              <div className="details-card">
                <span>📅 Created</span>

                <strong>
                  {selectedProject.createdAt}
                </strong>
              </div>

              <div className="details-card">
                <span>🚀 Last Deployment</span>

                <strong>
                  {selectedProject.lastDeployment}
                </strong>
              </div>

              <div className="details-card">
                <span>👁️ Visits</span>

                <strong>
                  {selectedProject.visits}
                </strong>
              </div>

              <div className="details-card">
                <span>💾 Storage</span>

                <strong>
                  {selectedProject.storage} KB
                </strong>
              </div>
            </div>

            <div className="project-actions">
              <button
                className="primary-button"
                disabled={
                  deployingId ===
                  selectedProject.id
                }
                onClick={() =>
                  deployProject(
                    selectedProject.id
                  )
                }
              >
                {deployingId ===
                  selectedProject.id
                  ? "Deploying..."
                  : selectedProject.deployment ===
                    "Live"
                    ? "🔄 Redeploy"
                    : "🚀 Deploy Project"}
              </button>

              <button
                className="delete-button"
                onClick={() =>
                  deleteProject(
                    selectedProject.id
                  )
                }
              >
                🗑️ Delete Project
              </button>
            </div>

            {deployingId ===
              selectedProject.id && (
                <div className="deployment-panel">
                  <h2>
                    Deployment Progress
                  </h2>

                  <p>
                    {deploymentStep}
                  </p>

                  <div className="progress-track">
                    <div
                      className="progress-bar"
                      style={{
                        width:
                          getProgress() +
                          "%",
                      }}
                    ></div>
                  </div>

                  <span>
                    {getProgress()}%
                  </span>
                </div>
              )}
          </section>
        )}

      {/* ================= NEW PROJECT MODAL ================= */}

      {showProjectModal && (
        <div
          className="modal-overlay"
          onClick={() =>
            setShowProjectModal(false)
          }
        >
          <div
            className="project-modal"
            onClick={(e) =>
              e.stopPropagation()
            }
          >
            <button
              className="modal-close"
              onClick={() =>
                setShowProjectModal(false)
              }
            >
              ×
            </button>

            <div className="modal-icon">
              🚀
            </div>

            <h2>
              Create New Project
            </h2>

            <p className="modal-subtitle">
              Add your website and prepare it
              for deployment.
            </p>

            <div className="input-group">
              <label>
                Project Name
              </label>

              <input
                type="text"
                placeholder="my-awesome-website"
                value={projectName}
                onChange={(e) =>
                  setProjectName(
                    e.target.value
                  )
                }
              />
            </div>

            <div className="input-group">
              <label>
                Description
              </label>

              <textarea
                className="project-textarea"
                placeholder="Describe your project..."
                value={projectDescription}
                onChange={(e) =>
                  setProjectDescription(
                    e.target.value
                  )
                }
              ></textarea>
            </div>

            <div className="upload-box">
              <div className="upload-icon">
                📦
              </div>

              <h3>
                Upload Project
              </h3>

              <p>
                Select your project files
              </p>

              <label className="upload-button">
                Choose Files

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

// ================= INPUT =================

function Input({
  label,
  type,
  placeholder,
  value,
  setValue,
}) {
  return (
    <div className="input-group">
      <label>{label}</label>

      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) =>
          setValue(e.target.value)
        }
      />
    </div>
  );
}

// ================= FEATURE =================

function Feature({
  icon,
  title,
  text,
}) {
  return (
    <div className="feature-card">
      <div className="feature-icon">
        {icon}
      </div>

      <h3>{title}</h3>

      <p>{text}</p>
    </div>
  );
}

// ================= DASHBOARD CARD =================

function DashboardCard({
  icon,
  title,
  value,
}) {
  return (
    <div className="dashboard-card">
      <div className="dashboard-card-icon">
        {icon}
      </div>

      <p>{title}</p>

      <h2>{value}</h2>
    </div>
  );
}

export default App;