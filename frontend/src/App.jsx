import "./App.css";
import DesignStudio from "./components/DesignStudio";
function App() {
  return (
    <div className="app">
      {/* Navigation */}
      <header className="navbar">
        <div className="logo">AURA<span>AI</span></div>

        <nav>
          <a href="#process">Process</a>
          <a href="#designer">Designer</a>
          <a href="#about">About</a>
        </nav>

        <button className="nav-button">Start Designing</button>
      </header>

      {/* Hero */}
      <main>
        <section className="hero">
          <div className="hero-content">
            <p className="eyebrow">AI INTERIOR DESIGN STUDIO</p>

            <h1>
              Your space.
              <br />
              <em>Reimagined.</em>
            </h1>

            <p className="hero-description">
              Transform your room with an AI designer that understands
              your space, your taste, and your budget.
            </p>

            <a href="#designer" className="hero-button">
              Design My Room <span>→</span>
            </a>
          </div>

          <div className="hero-image">
            <div className="image-overlay">
              <span>01</span>
              <span>AI / INTERIOR</span>
            </div>
          </div>
        </section>

        {/* Intro */}
        <section className="intro">
          <p className="section-label">01 — THE IDEA</p>

          <h2>
            Interior design,
            <br />
            <span>made intelligent.</span>
          </h2>

          <p className="intro-text">
            Upload your room. Tell us what you love. Our AI analyzes
            your space and creates a design that fits your vision.
          </p>
        </section>

        {/* Process */}
        <section className="process" id="process">
          <p className="section-label">02 — THE PROCESS</p>

          <div className="process-grid">
            <div className="process-card">
              <span>01</span>
              <h3>Show us your space</h3>
              <p>Upload a photo of the room you want to transform.</p>
            </div>

            <div className="process-card">
              <span>02</span>
              <h3>Tell us your taste</h3>
              <p>Choose your style, budget, and preferred colors.</p>
            </div>

            <div className="process-card">
              <span>03</span>
              <h3>Let AI design</h3>
              <p>
                Our AI analyzes your room and creates a personalized
                design plan.
              </p>
            </div>

            <div className="process-card">
              <span>04</span>
              <h3>See the transformation</h3>
              <p>
                Generate a realistic visualization of your redesigned
                space.
              </p>
            </div>
          </div>
        </section>
        
        <DesignStudio />
        {/* Designer CTA */}
        <section className="designer" id="designer">
          <div>
            <p className="section-label">03 — YOUR SPACE</p>

            <h2>
              Ready to
              <br />
              <em>transform it?</em>
            </h2>

            <p>
              Your room is the starting point.
              <br />
              Your imagination is the limit.
            </p>

            <button className="hero-button">
              Start Designing <span>→</span>
            </button>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer id="about">
        <div className="logo">AURA<span>AI</span></div>

        <p>Intelligent interior design, reimagined.</p>

        <span>© 2026 AURA AI</span>
      </footer>
    </div>
  );
}

export default App;