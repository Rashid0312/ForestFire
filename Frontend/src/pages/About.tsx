import Dither from "../components/Dither";
import "./About.css";

export default function About() {
  return (
    <div className="about-container">
      <div className="about-bg">
        <Dither
          waveColor={[1, 0.2, 0.2]}
          disableAnimation={false}
          enableMouseInteraction
          mouseRadius={0.1}
          colorNum={4}
          waveAmplitude={0.3}
          waveFrequency={3}
          waveSpeed={0.1}
        />
      </div>

      <div className="about-content">
        <h1>About ForestFire</h1>

        <div className="about-grid">
          <section className="about-section">
            <h2>What We Do</h2>
            <p>
              ForestFire visualizes wildfire risk globally. Search cities or countries, view country risk,
              and explore regional variation via tiles powered by live weather + an ML model (0–100 risk).
            </p>
          </section>

          <section className="about-section">
            <h2>Tech Stack</h2>
            <p>
              React, TypeScript, Vite, Leaflet (frontend) • Python, Flask, scikit‑learn, XGBoost (backend/ML) • Docker, Compose.
            </p>
          </section>
        </div>

        <section className="about-section team-section">
          <h2>About the Developer</h2>
          <div className="team-list">
            <a
              href="https://www.linkedin.com/in/abdirashiid-sammantar-3b7863238/"
              target="_blank"
              rel="noopener noreferrer"
              className="team-member"
            >
              Abdirashiid Sammantar
            </a>
          </div>
        </section>
      </div>
    </div>
  );
}
