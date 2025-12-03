# 🔥 ForestFire – Interactive Wildfire Risk Map

ForestFire is an interactive web application that visualizes wildfire risk across the globe using machine learning models, live weather data, and an interactive map interface.

## ✨ Features

- **Location-based Risk Analysis:** Search any city or country to see its wildfire risk score
- **Country-level Risk Visualization:** Countries are color-coded based on risk levels (Low / Medium / High)
- **Regional Risk Tiles:** View sub-country variations with detailed regional tiles inside the searched country
- **Point-based Predictions:** Click anywhere on the map to get detailed weather data and fire indices for that specific location
- **Real-time Weather Integration:** Live weather data including temperature, humidity, wind speed, and rainfall
- **Interactive Controls:** Toggle visibility of different map layers and clear selections

---

## 💻 Tech Stack

### Frontend
- **React** with TypeScript
- **Vite** for fast development and building
- **React-Leaflet & Leaflet** for interactive mapping
- **Nginx** for production serving

### Backend
- **Python 3.10+** with Flask
- **Flask-CORS** for cross-origin requests
- **scikit-learn** and **XGBoost** for machine learning
- **pandas** and **numpy** for data processing
- **joblib** for model serialization

### Infrastructure
- **Docker** and **Docker Compose** for containerization
- **OpenWeather API** for live weather data

---

## 🚀 Quick Start (Docker – Recommended)

This is the simplest way to get the application running.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- OpenWeather API key ([Get one free here](https://openweathermap.org/api))

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Rashid0312/ForestFire.git
cd ForestFire

# 2. Create environment file
cp .env.example .env

# 3. Edit .env and add your API key
# WEATHER_API_KEY=your_openweather_api_key_here

# 4. Build and start all services
docker-compose build
docker-compose up
```

**Access the application:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5001

**To stop:**
```bash
docker-compose down
```

---

## 🛠️ Local Development (Without Docker)

Use this method if you want hot-reload and to work directly on the code.

### Backend Setup

**Prerequisites:** Python 3.10+, pip

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set: WEATHER_API_KEY=your_openweather_api_key_here

# Run backend server
python app.py                 # Runs on http://localhost:5001
```

### Frontend Setup

**Prerequisites:** Node.js v18+, npm

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev                   # Typically http://localhost:5173
```

**Note:** Make sure your frontend API URLs point to `http://localhost:5001/api/...` for local development.

---

## 📂 Project Structure

```
ForestFire/
├── backend/
│   ├── app.py                    # Flask API with prediction endpoints
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile
│   └── ...                       # ML models, utilities, etc.
├── frontend/
│   ├── src/
│   │   ├── pages/Survey.tsx      # Main interactive map page
│   │   └── ...
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── nginx.conf                # Production web server config
├── docker-compose.yml            # Multi-container orchestration
├── .env.example                  # Environment variables template
└── README.md
```

---

## 🌐 API Documentation

### POST `/api/predict`

Predict wildfire risk from a human-readable location (city or country).

**Request:**
```json
{
  "location": "Madrid, Spain"
}
```

**Response:**
```json
{
  "location": "Madrid, Spain",
  "risk_score": 73,
  "risk_category": "High",
  "weather": {
    "temperature": 32.1,
    "humidity": 28,
    "wind_speed": 14.3,
    "rainfall": 0.0
  },
  "fire_indices": {
    "FFMC": 90.2,
    "DMC": 45.1,
    "DC": 320.5,
    "ISI": 12.3
  }
}
```

### POST `/api/predict-coords`

Predict wildfire risk from latitude/longitude coordinates.

**Request:**
```json
{
  "latitude": 40.4168,
  "longitude": -3.7038
}
```

**Response:** Same format as `/api/predict`

---

## 🗺️ How to Use the Map

### Search Functionality
1. Type a city or country in the search bar (e.g., `Madrid, Spain`, `Sweden`)
2. The application will:
   - Display the risk score for that location
   - Color the entire country based on risk category
   - Zoom the map to that country
   - Generate regional tiles showing local risk variations

### Interactive Map Features
- **Click anywhere** on the map to get point-specific predictions
- **Markers** show exact locations with detailed weather data in popups
- **Regional tiles** display color-coded risk levels:
  - 🟢 **Green:** Low risk
  - 🟠 **Orange:** Medium risk
  - 🔴 **Red:** High risk

### Sidebar Controls
- **Toggle layers:** Show/hide country fills and regional tiles
- **My Location:** Use browser geolocation to check risk at your current position
- **Clear All:** Remove all markers, tiles, and reset the map
- **View Details:** See complete information about the last search

---

## 🔑 Environment Variables

Create a `.env` file in the project root or `backend/` directory:

```env
WEATHER_API_KEY=your_openweather_api_key_here
```

Get your free API key from [OpenWeather](https://openweathermap.org/api).

---

## 🤝 Contributing

We welcome contributions to ForestFire!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🔮 Future Enhancements

- Finer grid overlays for smoother regional risk patterns
- Time-series forecasts for multi-day wildfire risk predictions
- User-selectable basemaps and risk thresholds
- Additional data layers (vegetation density, population, infrastructure)
- Historical fire data integration
- Mobile app version

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 👨‍💻 Author

**Rashid0312**

- GitHub: [@Rashid0312](https://github.com/Rashid0312)
- Project Link: [https://github.com/Rashid0312/ForestFire](https://github.com/Rashid0312/ForestFire)

---

## 🙏 Acknowledgments

- OpenWeather API for providing weather data
- Leaflet.js for the mapping library
- All contributors who help improve this project
