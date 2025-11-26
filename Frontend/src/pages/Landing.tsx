import { Link } from "react-router-dom";
import "./Landing.css";
import Dither from "../components/Dither";

export default function Landing() {
  return (
    <div className="landing-container">
      <div className="landing-background">
        <Dither
        waveColor={[1, 0.2, 0.2]}
        disableAnimation={false}
        enableMouseInteraction={true}
        mouseRadius={0.1}
        colorNum={4}
        waveAmplitude={0.3}
        waveFrequency={3}
        waveSpeed={0.1}
  />
      </div>
      
      <div className="landing-content">
        <h1>Forest Fire Prediction</h1>
        <p>AI-powered wildfire risk assessment and monitoring</p>
        <div className="button-group">
          <Link to="/survey" className="btn btn-primary">
            Get Started
          </Link>
          <Link to="/dashboard" className="btn btn-primary">
            Learn more
          </Link>
        </div>
      </div>
    </div>
  );
}
