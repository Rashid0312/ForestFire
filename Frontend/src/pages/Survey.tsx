import { useState, useRef, useEffect } from 'react';
import { MapContainer, TileLayer, useMapEvents, Marker, Popup, GeoJSON } from 'react-leaflet';
import axios from 'axios';
import L, { LatLngBounds } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

import Dither from "../components/Dither";
import './Survey.css';

// Fix Leaflet's default marker icon paths for modern bundlers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// INTERFACES
interface PredictionResult {
  location: string;
  risk_score: number;
  risk_category: string;
  weather: { temperature: number; humidity: number; wind_speed: number; rainfall: number; };
  fire_indices: { FFMC: number; DMC: number; DC: number; ISI: number; };
}

interface LocationMarker {
  lat: number;
  lng: number;
  result: PredictionResult | null;
  loading: boolean;
  error: string;
}
interface CountryRisk {
  score: number;
  category: string;
}

// MAP CLICK HANDLER
function MapClickHandler({ onMapClick }: { onMapClick: (lat: number, lng: number) => void }) {
  useMapEvents({ click: (e) => onMapClick(e.latlng.lat, e.latlng.lng) });
  return null;
}

// MAIN COMPONENT
export default function Survey() {
  const [markers, setMarkers] = useState<LocationMarker[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchLocation, setSearchLocation] = useState('');
  const [searchResult, setSearchResult] = useState<PredictionResult | null>(null);
  const [countryRisks, setCountryRisks] = useState<Record<string, CountryRisk>>({});
  const [geoJsonData, setGeoJsonData] = useState<any>(null);
  const [visibleRisks, setVisibleRisks] = useState({ low: true, medium: true, high: true });
  const mapRef = useRef<any>(null);

  // Load GeoJSON world boundaries
  useEffect(() => {
    fetch('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson')
      .then(res => res.json())
      .then(data => setGeoJsonData(data))
      .catch(err => console.log('Could not load GeoJSON', err));
  }, []);

  // Helpers
  const getRiskColor = (category: string): string => {
    const colors = { low: '#22c55e', medium: '#f59e0b', high: '#ef4444' };
    return colors[category?.toLowerCase() as keyof typeof colors] || '#6b7280';
  };
  const extractCountryName = (location: string): string => {
    // Handles things like "Stockholm, Sweden" or just "Sweden"
    const parts = location.split(',').map(s => s.trim());
    return parts[parts.length - 1];
  };
  const zoomToCountry = (country: string) => {
    if (!geoJsonData || !mapRef.current) return;

    const matchFeature = geoJsonData.features.find(
      (f: any) =>
        (f.properties.ADMIN || f.properties.name).toLowerCase() === country.toLowerCase()
    );
    if (matchFeature) {
      const layer = new L.GeoJSON(matchFeature);
      const bounds: LatLngBounds = layer.getBounds();
      if (bounds.isValid()) {
        mapRef.current.fitBounds(bounds, { maxZoom: 6 });
      }
    }
  };

  // Handlers
  const handleMapClick = async (lat: number, lng: number) => {
    const newMarker: LocationMarker = { lat, lng, result: null, loading: true, error: '' };
    setMarkers(prev => [...prev, newMarker]);
    try {
      const response = await axios.post('http://localhost:5001/api/predict-coords', {
        latitude: lat,
        longitude: lng
      });
      setMarkers(prev =>
        prev.map(m =>
          m.lat === lat && m.lng === lng
            ? { ...m, result: response.data, loading: false }
            : m
        )
      );
      const country = extractCountryName(response.data.location);
      setCountryRisks(prev => ({
        ...prev,
        [country]: {
          score: response.data.risk_score,
          category: response.data.risk_category.toLowerCase()
        }
      }));
      zoomToCountry(country); // Zoom to country boundary
    } catch (err: any) {
      setMarkers(prev =>
        prev.map(m =>
          m.lat === lat && m.lng === lng
            ? { ...m, error: 'Failed to get prediction', loading: false }
            : m
        )
      );
    }
  };

  const handleSearch = async () => {
    if (!searchLocation.trim()) return;
    try {
      const response = await axios.post('http://localhost:5001/api/predict', {
        location: searchLocation
      });
      setSearchResult(response.data);
      const country = extractCountryName(response.data.location);
      setCountryRisks(prev => ({
        ...prev,
        [country]: {
          score: response.data.risk_score,
          category: response.data.risk_category.toLowerCase()
        }
      }));
      zoomToCountry(country); // Zoom to country boundary
      setSearchLocation('');
    } catch (err: any) {
      alert(`Could not find "${searchLocation}". Try "Madrid, Spain" or "Tokyo, Japan"`);
    }
  };

  const handleMyLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          handleMapClick(latitude, longitude);
          if (mapRef.current) {
            mapRef.current.setView([latitude, longitude], 10);
          }
        },
        () => alert('Could not get your location')
      );
    } else {
      alert('Geolocation not supported');
    }
  };
  const toggleRiskLevel = (level: string) => {
    setVisibleRisks(prev => ({ ...prev, [level]: !prev[level as keyof typeof prev] }));
  };
  const clearMarkers = () => {
    setMarkers([]);
    setCountryRisks({});
  };

  // GeoJSON styling
  const styleFeature = (feature: any) => {
    const countryName = feature.properties?.ADMIN || feature.properties?.name;
    const risk = countryRisks[countryName];
    if (!risk || !visibleRisks[risk.category as keyof typeof visibleRisks]) {
      return {
        fillColor: 'transparent',
        fillOpacity: 0,
        weight: 1,
        color: '#999',
        opacity: 0.3
      };
    }
    return {
      fillColor: getRiskColor(risk.category),
      fillOpacity: 0.6,
      weight: 2,
      color: '#fff',
      opacity: 1
    };
  };
  const onEachFeature = (feature: any, layer: any) => {
    const countryName = feature.properties?.ADMIN || feature.properties?.name;
    const risk = countryRisks[countryName];
    if (risk) {
      layer.bindPopup(
        `<strong>${countryName}</strong><br/>` +
        `Risk: ${risk.category}<br/>` +
        `Score: ${risk.score}/100`
      );
    }
  };

  // RENDER
  return (
    <div className="survey-page-container">
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
        <h1 className="survey-title">Interactive Fire Risk Map</h1>
        <p className="survey-subtitle">Click anywhere or search a city/country to check fire risk – country will be colored and zoomed</p>
        <div className="survey-container">
          <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>☰</button>
          {/* Sidebar */}
          <div className={`survey-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
            <div className="sidebar-header">
              <h3>🔥 Fire Viewer</h3>
              <button className="close-btn" onClick={() => setSidebarOpen(false)}>✕</button>
            </div>
            <div className="sidebar-section">
              <h4>Risk Levels</h4>
              <div className="section-content">
                {['low', 'medium', 'high'].map(level => (
                  <label key={level} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={visibleRisks[level as keyof typeof visibleRisks]}
                      onChange={() => toggleRiskLevel(level)}
                    />
                    <span className={`risk-dot ${level}`}></span>
                    {level.charAt(0).toUpperCase() + level.slice(1)} Risk
                  </label>
                ))}
              </div>
            </div>
            {/* Search */}
            <div className="sidebar-section">
              <h4>Search Location</h4>
              <input
                type="text"
                className="search-input"
                placeholder="e.g., Madrid, Spain"
                value={searchLocation}
                onChange={(e) => setSearchLocation(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button className="action-btn" onClick={handleSearch}>🔍 Search</button>
            </div>
            <div className="sidebar-section">
              <h4>Quick Actions</h4>
              <button className="action-btn secondary" onClick={handleMyLocation}>📍 My Location</button>
              <button className="action-btn secondary" onClick={clearMarkers}>🗑️ Clear All</button>
            </div>
            {searchResult && (
              <div className="sidebar-section result-info">
                <h4>Search Result</h4>
                <div className="result-card">
                  <h5>{searchResult.location}</h5>
                  <div className="result-score" style={{ color: getRiskColor(searchResult.risk_category) }}>
                    {searchResult.risk_score}
                  </div>
                  <div className="result-category">{searchResult.risk_category} Risk</div>
                  <div className="result-weather">
                    <p>🌡️ {searchResult.weather.temperature}°C</p>
                    <p>💧 {searchResult.weather.humidity}%</p>
                  </div>
                </div>
              </div>
            )}
          </div>
          {/* Map */}
          <div className="survey-map-section">
            <MapContainer center={[20, 0]} zoom={2} className="survey-map" ref={mapRef}>
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                attribution='&copy; OpenStreetMap contributors &copy; CARTO'
              />
              {geoJsonData && (
                <GeoJSON
                  data={geoJsonData}
                  style={styleFeature}
                  onEachFeature={onEachFeature}
                />
              )}
              <MapClickHandler onMapClick={handleMapClick} />
              {markers.map((marker, idx) =>
                marker.result && (
                  <Marker key={idx} position={[marker.lat, marker.lng]}>
                    <Popup>
                      <div className="popup-result">
                        <h3>{marker.result.location}</h3>
                        <div className="popup-risk-score" style={{ color: getRiskColor(marker.result.risk_category) }}>
                          {marker.result.risk_score}/100
                        </div>
                        <div className="popup-risk-label">Risk Score</div>
                        <div
                          className="popup-risk-badge"
                          style={{ backgroundColor: getRiskColor(marker.result.risk_category) }}
                        >
                          {marker.result.risk_category} Risk
                        </div>
                        <div className="popup-weather">
                          <h4>Weather</h4>
                          <p>🌡️ {marker.result.weather.temperature}°C</p>
                          <p>💧 {marker.result.weather.humidity}%</p>
                          <p>💨 {marker.result.weather.wind_speed} km/h</p>
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                )
              )}
            </MapContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
