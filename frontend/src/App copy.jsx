import { useState } from "react";

function App() {
  const [page, setPage] = useState("home");
  const [authMode, setAuthMode] = useState("login");
  const [showPassword, setShowPassword] = useState(false);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e) {
    e.preventDefault();

    if (authMode === "signup" && !name) {
      alert("Please enter your name.");
      return;
    }

    if (!email || !password) {
      alert("Please enter email and password.");
      return;
    }

    alert(
      authMode === "login"
        ? "Login successful! 🚀"
        : "Account created successfully! 🎉"
    );

    setPage("dashboard");
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#07111f",
        color: "#ffffff",
        fontFamily: "Arial, sans-serif",
      }}
    >
      {/* NAVBAR */}
      <nav
        style={{
          height: "72px",
          padding: "0 7%",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
          background: "#07111f",
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <button
          onClick={() => setPage("home")}
          style={{
            border: "none",
            background: "transparent",
            color: "#fff",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "12px",
          }}
        >
          <div
            style={{
              width: "42px",
              height: "42px",
              borderRadius: "12px",
              background: "#67e8f9",
              color: "#07111f",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: "bold",
            }}
          >
            W3
          </div>

          <div style={{ textAlign: "left" }}>
            <div style={{ fontSize: "20px", fontWeight: "bold" }}>
              Web3<span style={{ color: "#67e8f9" }}>Host</span>
            </div>

            <div
              style={{
                fontSize: "9px",
                color: "#7c8da6",
                letterSpacing: "2px",
              }}
            >
              DECENTRALIZED HOSTING
            </div>
          </div>
        </button>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "25px",
          }}
        >
          {page === "home" && (
            <>
              <a
                href="#features"
                style={{
                  color: "#a9b8cc",
                  textDecoration: "none",
                }}
              >
                Features
              </a>

              <a
                href="#about"
                style={{
                  color: "#a9b8cc",
                  textDecoration: "none",
                }}
              >
                About
              </a>

              <button
                onClick={() => {
                  setAuthMode("login");
                  setPage("auth");
                }}
                style={{
                  background: "#ffffff",
                  color: "#07111f",
                  border: "none",
                  borderRadius: "10px",
                  padding: "11px 22px",
                  fontWeight: "bold",
                  cursor: "pointer",
                }}
              >
                Login
              </button>
            </>
          )}
        </div>
      </nav>

      {/* HOME */}
      {page === "home" && (
        <>
          <section
            style={{
              padding: "110px 7% 100px",
              textAlign: "center",
            }}
          >
            <div
              style={{
                display: "inline-block",
                padding: "9px 18px",
                borderRadius: "30px",
                background: "rgba(103,232,249,0.08)",
                border: "1px solid rgba(103,232,249,0.25)",
                color: "#67e8f9",
                fontSize: "14px",
                marginBottom: "25px",
              }}
            >
              ● Next Generation Web Hosting
            </div>

            <h1
              style={{
                fontSize: "clamp(48px,7vw,88px)",
                lineHeight: 1.05,
                maxWidth: "950px",
                margin: "auto",
                fontWeight: 800,
              }}
            >
              Build.
              <span style={{ color: "#67e8f9" }}> Deploy.</span>
              <br />

              <span
                style={{
                  background:
                    "linear-gradient(90deg,#67e8f9,#60a5fa,#a78bfa)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                Host the Future.
              </span>
            </h1>

            <p
              style={{
                maxWidth: "680px",
                margin: "28px auto",
                color: "#a9b8cc",
                fontSize: "18px",
                lineHeight: 1.8,
              }}
            >
              Web3Host is a modern hosting platform designed for developers
              to upload, deploy and manage websites with a fast, secure and
              Web3-ready experience.
            </p>

            <button
              onClick={() => {
                setAuthMode("signup");
                setPage("auth");
              }}
              style={{
                padding: "15px 28px",
                borderRadius: "12px",
                border: "none",
                background: "linear-gradient(90deg,#67e8f9,#60a5fa)",
                color: "#07111f",
                fontWeight: "bold",
                fontSize: "15px",
                cursor: "pointer",
              }}
            >
              🚀 Start Deploying
            </button>
          </section>

          {/* FEATURES */}
          <section
            id="features"
            style={{
              padding: "80px 7%",
              borderTop: "1px solid rgba(255,255,255,0.06)",
            }}
          >
            <div style={{ textAlign: "center" }}>
              <p
                style={{
                  color: "#67e8f9",
                  letterSpacing: "3px",
                  fontWeight: "bold",
                }}
              >
                WHY WEB3HOST
              </p>

              <h2 style={{ fontSize: "42px" }}>
                Powerful Hosting Experience
              </h2>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit,minmax(220px,1fr))",
                gap: "20px",
                marginTop: "50px",
              }}
            >
              <Feature
                icon="⚡"
                title="Lightning Fast"
                text="Deploy projects quickly with a modern hosting experience."
              />

              <Feature
                icon="🛡️"
                title="Secure"
                text="Security-focused architecture for your web projects."
              />

              <Feature
                icon="🌎"
                title="Global"
                text="Access and manage your websites from anywhere."
              />

              <Feature
                icon="🔗"
                title="Web3 Ready"
                text="Built with the future of decentralized applications in mind."
              />
            </div>
          </section>

          {/* ABOUT */}
          <section
            id="about"
            style={{
              padding: "90px 7%",
              textAlign: "center",
              background: "rgba(255,255,255,0.02)",
            }}
          >
            <h2 style={{ fontSize: "40px" }}>
              Hosting Built for Developers
            </h2>

            <p
              style={{
                maxWidth: "700px",
                margin: "20px auto",
                color: "#a9b8cc",
                lineHeight: 1.8,
              }}
            >
              Upload your project, deploy it and manage everything from one
              simple platform.
            </p>
          </section>
        </>
      )}

      {/* AUTH */}
      {page === "auth" && (
        <section
          style={{
            minHeight: "calc(100vh - 72px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "50px 20px",
          }}
        >
          <div
            style={{
              width: "100%",
              maxWidth: "450px",
              padding: "40px",
              borderRadius: "25px",
              border: "1px solid rgba(255,255,255,0.1)",
              background: "#0c1a2b",
              boxShadow: "0 20px 80px rgba(0,0,0,0.35)",
            }}
          >
            <div style={{ textAlign: "center" }}>
              <div
                style={{
                  width: "60px",
                  height: "60px",
                  margin: "auto",
                  borderRadius: "16px",
                  background: "#67e8f9",
                  color: "#07111f",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: "bold",
                  fontSize: "20px",
                }}
              >
                W3
              </div>

              <h2 style={{ fontSize: "32px", marginTop: "20px" }}>
                {authMode === "login"
                  ? "Welcome Back"
                  : "Create Account"}
              </h2>

              <p style={{ color: "#7c8da6" }}>
                {authMode === "login"
                  ? "Login to your Web3Host account"
                  : "Create your Web3Host account"}
              </p>
            </div>

            <form onSubmit={handleSubmit} style={{ marginTop: "30px" }}>
              {authMode === "signup" && (
                <Input
                  label="Full Name"
                  type="text"
                  placeholder="Your Name"
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

              <div style={{ marginTop: "18px" }}>
                <label
                  style={{
                    display: "block",
                    marginBottom: "8px",
                    color: "#cbd5e1",
                  }}
                >
                  Password
                </label>

                <div style={{ position: "relative" }}>
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={{
                      width: "100%",
                      boxSizing: "border-box",
                      padding: "14px",
                      paddingRight: "70px",
                      borderRadius: "10px",
                      border: "1px solid rgba(255,255,255,0.1)",
                      background: "#07111f",
                      color: "#fff",
                      outline: "none",
                    }}
                  />

                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{
                      position: "absolute",
                      right: "10px",
                      top: "50%",
                      transform: "translateY(-50%)",
                      border: "none",
                      background: "transparent",
                      color: "#67e8f9",
                      cursor: "pointer",
                    }}
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                style={{
                  width: "100%",
                  marginTop: "25px",
                  padding: "14px",
                  border: "none",
                  borderRadius: "10px",
                  background: "linear-gradient(90deg,#67e8f9,#60a5fa)",
                  color: "#07111f",
                  fontWeight: "bold",
                  fontSize: "15px",
                  cursor: "pointer",
                }}
              >
                {authMode === "login" ? "Login" : "Create Account"}
              </button>
            </form>

            <div
              style={{
                textAlign: "center",
                marginTop: "25px",
                color: "#7c8da6",
              }}
            >
              {authMode === "login"
                ? "Don't have an account?"
                : "Already have an account?"}

              <button
                onClick={() =>
                  setAuthMode(
                    authMode === "login" ? "signup" : "login"
                  )
                }
                style={{
                  border: "none",
                  background: "transparent",
                  color: "#67e8f9",
                  fontWeight: "bold",
                  cursor: "pointer",
                  marginLeft: "7px",
                }}
              >
                {authMode === "login" ? "Sign Up" : "Login"}
              </button>
            </div>

            <button
              onClick={() => setPage("home")}
              style={{
                width: "100%",
                marginTop: "20px",
                padding: "12px",
                borderRadius: "10px",
                border: "1px solid rgba(255,255,255,0.1)",
                background: "transparent",
                color: "#a9b8cc",
                cursor: "pointer",
              }}
            >
              ← Back to Home
            </button>
          </div>
        </section>
      )}

      {/* DASHBOARD */}
      {page === "dashboard" && (
        <section
          style={{
            minHeight: "calc(100vh - 72px)",
            padding: "80px 7%",
          }}
        >
          <p
            style={{
              color: "#67e8f9",
              letterSpacing: "3px",
              fontWeight: "bold",
            }}
          >
            DASHBOARD
          </p>

          <h1 style={{ fontSize: "45px" }}>
            Welcome to Web3Host 🚀
          </h1>

          <p style={{ color: "#a9b8cc" }}>
            Your account is ready. Deployment features will be added next.
          </p>

          <div
            style={{
              marginTop: "40px",
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit,minmax(220px,1fr))",
              gap: "20px",
            }}
          >
            <DashboardCard title="Projects" value="0" icon="📁" />
            <DashboardCard title="Deployments" value="0" icon="🚀" />
            <DashboardCard title="Storage" value="0 MB" icon="💾" />
            <DashboardCard title="Status" value="Active" icon="✅" />
          </div>

          <button
            onClick={() => setPage("home")}
            style={{
              marginTop: "35px",
              padding: "13px 25px",
              border: "none",
              borderRadius: "10px",
              background: "#67e8f9",
              color: "#07111f",
              fontWeight: "bold",
              cursor: "pointer",
            }}
          >
            ← Home
          </button>
        </section>
      )}

      {/* FOOTER */}
      {page !== "dashboard" && (
        <footer
          style={{
            padding: "30px 7%",
            borderTop: "1px solid rgba(255,255,255,0.1)",
            textAlign: "center",
            color: "#7c8da6",
          }}
        >
          Web3Host © 2026
        </footer>
      )}
    </div>
  );
}

function Input({ label, type, placeholder, value, setValue }) {
  return (
    <div style={{ marginTop: "18px" }}>
      <label
        style={{
          display: "block",
          marginBottom: "8px",
          color: "#cbd5e1",
        }}
      >
        {label}
      </label>

      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        style={{
          width: "100%",
          boxSizing: "border-box",
          padding: "14px",
          borderRadius: "10px",
          border: "1px solid rgba(255,255,255,0.1)",
          background: "#07111f",
          color: "#fff",
          outline: "none",
        }}
      />
    </div>
  );
}

function Feature({ icon, title, text }) {
  return (
    <div
      style={{
        padding: "28px",
        borderRadius: "18px",
        border: "1px solid rgba(255,255,255,0.1)",
        background: "#0c1a2b",
      }}
    >
      <div style={{ fontSize: "32px" }}>{icon}</div>

      <h3 style={{ fontSize: "20px" }}>{title}</h3>

      <p
        style={{
          color: "#7c8da6",
          lineHeight: 1.7,
        }}
      >
        {text}
      </p>
    </div>
  );
}

function DashboardCard({ title, value, icon }) {
  return (
    <div
      style={{
        padding: "25px",
        borderRadius: "18px",
        border: "1px solid rgba(255,255,255,0.1)",
        background: "#0c1a2b",
      }}
    >
      <div style={{ fontSize: "28px" }}>{icon}</div>

      <p style={{ color: "#7c8da6" }}>{title}</p>

      <h2 style={{ fontSize: "30px" }}>{value}</h2>
    </div>
  );
}

export default App;