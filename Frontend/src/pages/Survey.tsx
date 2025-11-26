import { useState } from 'react';
import axios from 'axios';
import Dither from "../components/Dither";
import "./Survey.css";

interface WeatherData {
  temperature: number;
  humidity: number;
  wind_speed: number;
  rainfall: number;
}

interface FireIndices {
  FFMC: number;
  DMC: number;
  DC: number;
  ISI: number;
}

interface PredictionResult {
  location: string;
  risk_score: number;
  risk_category: string;
  prediction: string;
  weather: WeatherData;
  fire_indices: FireIndices;
}

export default function Survey() {
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!location.trim()) {
      setError('Please enter a location');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post('http://localhost:5001/api/predict', {
        location: location
      });
      
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to get prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (category: string) => {
    switch (category?.toLowerCase()) {
      case 'low': return '#22c55e';
      case 'medium': return '#f59e0b';
      case 'high': return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <div className="survey-container">
      <div className="survey-background">
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
      
      <div className="survey-content">
        <div className="survey-header">
          <h1>Wildfire Risk Assessment</h1>
          <p>Enter your location to get real-time fire danger prediction</p>
        </div>

        <form onSubmit={handleSubmit} className="survey-form">
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter location (e.g., Madrid, Spain)"
            className="location-input"
            disabled={loading}
          />
          <button 
            type="submit" 
            className="submit-btn"
            disabled={loading}
          >
            {loading ? 'Checking...' : 'Check Fire Risk'}
          </button>
        </form>

        {error && (
          <div className="error-box">
            {error}
          </div>
        )}

        {result && (
          <div className="results-section">
            <div className="risk-card" style={{ borderColor: getRiskColor(result.risk_category) }}>
              <div className="location-title">{result.location}</div>
              
              <div className="risk-score" style={{ color: getRiskColor(result.risk_category) }}>
                {result.risk_score}
              </div>
              <div className="score-label">Risk Score</div>
              
              <div className="risk-badge" style={{ backgroundColor: getRiskColor(result.risk_category) }}>
                {result.risk_category} Risk
              </div>
              
              <div className="prediction-label">{result.prediction}</div>
            </div>

            <div className="info-grid">
              <div className="info-card">
                <h3>Weather Conditions</h3>
                <div className="info-row">
                  <span>🌡️ Temperature</span>
                  <span>{result.weather.temperature}°C</span>
                </div>
                <div className="info-row">
                  <span>💧 Humidity</span>
                  <span>{result.weather.humidity}%</span>
                </div>
                <div className="info-row">
                  <span>💨 Wind Speed</span>
                  <span>{result.weather.wind_speed} km/h</span>
                </div>
                <div className="info-row">
                  <span>🌧️ Rainfall</span>
                  <span>{result.weather.rainfall} mm</span>
                </div>
              </div>

              <div className="info-card">
                <h3>Fire Weather Indices</h3>
                <div className="info-row">
                  <span>FFMC</span>
                  <span>{result.fire_indices.FFMC}</span>
                </div>
                <div className="info-row">
                  <span>DMC</span>
                  <span>{result.fire_indices.DMC}</span>
                </div>
                <div className="info-row">
                  <span>DC</span>
                  <span>{result.fire_indices.DC}</span>
                </div>
                <div className="info-row">
                  <span>ISI</span>
                  <span>{result.fire_indices.ISI}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
