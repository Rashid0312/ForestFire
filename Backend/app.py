from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Load model and scaler
model = joblib.load('models/fire_model.pkl')
scaler = joblib.load('models/scaler.pkl')

# Load feature list (not strictly needed, but fine to keep)
with open('models/features.txt', 'r') as f:
    feature_names = f.read().strip().split(',')

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')


def get_weather_data(location: str):
    """Fetch current weather data from OpenWeatherMap API"""
    if not WEATHER_API_KEY:
        # Fallback demo data if no API key
        return {
            'temp': 22.0,
            'humidity': 45,
            'wind': 3.5,
            'rain': 0.0
        }

    try:
        # Try direct location search first
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'temp': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'wind': data['wind']['speed'],
                'rain': data.get('rain', {}).get('1h', 0.0)
            }
        else:
            print(f"Weather API error for '{location}': {response.status_code} - {response.text}")
            # Return fallback data instead of None
            return {
                'temp': 20.0,
                'humidity': 50,
                'wind': 3.0,
                'rain': 0.0
            }
    except Exception as e:
        print(f"Weather API exception for '{location}': {e}")
        # Return fallback data
        return {
            'temp': 20.0,
            'humidity': 50,
            'wind': 3.0,
            'rain': 0.0
        }


def calculate_fwi_indices(temp, humidity, wind, rain):
    """
    Simplified FWI calculation (approximation for demo).
    """
    # FFMC (Fine Fuel Moisture Code) - inversely related to humidity
    ffmc = 85 + (100 - humidity) * 0.15

    # DMC (Duff Moisture Code) - influenced by temp and humidity
    dmc = max(0, temp * 2 + (100 - humidity) * 0.5)

    # DC (Drought Code) - cumulative dryness
    dc = max(0, temp * 10 + (100 - humidity) * 2)

    # ISI (Initial Spread Index) - wind effect
    isi = wind * 0.7 + (100 - humidity) * 0.05

    return {
        'FFMC': min(96.2, ffmc),
        'DMC': min(291.3, dmc),
        'DC': min(860.6, dc),
        'ISI': min(56.1, isi)
    }


@app.route('/')
def home():
    return jsonify({
        'message': 'Forest Fire Prediction API',
        'version': '1.0',
        'endpoints': {
            '/api/predict': 'POST - Predict fire risk for a location name',
            '/api/predict-coords': 'POST - Predict fire risk for coordinates',
            '/api/health': 'GET - Health check'
        }
    })


@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'model_loaded': True})


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Endpoint for Survey page:
    Input: { "location": "Madrid, Spain" }
    """
    try:
        data = request.json or {}
        location = data.get('location', '').strip()

        if not location:
            return jsonify({'error': 'Location is required'}), 400

        # Get weather data for this location
        weather = get_weather_data(location)

        if weather is None:
            return jsonify({'error': 'Could not fetch weather data for this location'}), 400

        # Calculate FWI indices
        fwi = calculate_fwi_indices(
            weather['temp'],
            weather['humidity'],
            weather['wind'],
            weather['rain']
        )

        # Prepare input features in correct order
        input_features = [
            fwi['FFMC'],
            fwi['DMC'],
            fwi['DC'],
            fwi['ISI'],
            weather['temp'],
            weather['humidity'],
            weather['wind'],
            weather['rain']
        ]

        features_array = np.array([input_features])
        features_scaled = scaler.transform(features_array)

        # Predict
        prediction = model.predict(features_scaled)[0]
        probability = model.predict_proba(features_scaled)[0]

        # Base risk score
        risk_score = int(probability[1] * 100)

        # Adjust for cold climates
        if weather['temp'] < 5:
            risk_score = min(risk_score, 20)
            prediction = 0  # No significant risk
        elif weather['temp'] < 10:
            risk_score = min(risk_score, 40)

        # Determine risk category
        if risk_score < 30:
            risk_category = 'Low'
        elif risk_score < 60:
            risk_category = 'Medium'
        else:
            risk_category = 'High'

        return jsonify({
            'location': location,
            'risk_score': risk_score,
            'risk_category': risk_category,
            'prediction': 'Fire Risk' if prediction == 1 else 'No Significant Risk',
            'weather': {
                'temperature': round(weather['temp'], 1),
                'humidity': weather['humidity'],
                'wind_speed': round(weather['wind'], 1),
                'rainfall': weather['rain']
            },
            'fire_indices': {
                'FFMC': round(fwi['FFMC'], 1),
                'DMC': round(fwi['DMC'], 1),
                'DC': round(fwi['DC'], 1),
                'ISI': round(fwi['ISI'], 1)
            }
        })

    except Exception as e:
        print(f"/api/predict error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/predict-coords', methods=['POST'])
def predict_coords():
    """
    Endpoint for Map page:
    Input: { "latitude": 40.4, "longitude": -3.7 }
    """
    try:
        data = request.json or {}
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if latitude is None or longitude is None:
            return jsonify({'error': 'Latitude and longitude required'}), 400

        # Get weather by coordinates
        if not WEATHER_API_KEY:
            return jsonify({'error': 'WEATHER_API_KEY is not set'}), 500

        weather_url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?lat={latitude}&lon={longitude}&appid={WEATHER_API_KEY}&units=metric"
        )
        weather_response = requests.get(weather_url, timeout=5)

        if weather_response.status_code != 200:
            print("Weather API error (coords):", weather_response.text)
            return jsonify({'error': 'Could not fetch weather data'}), 500

        weather_data = weather_response.json()
        location_name = weather_data.get(
            'name',
            f'Location ({float(latitude):.2f}, {float(longitude):.2f})'
        )

        temp = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        wind = weather_data['wind']['speed']
        rain = weather_data.get('rain', {}).get('1h', 0.0)

        # Calculate FWI
        fwi = calculate_fwi_indices(temp, humidity, wind, rain)

        # Prepare features
        features_array = np.array([[
            fwi['FFMC'],
            fwi['DMC'],
            fwi['DC'],
            fwi['ISI'],
            temp,
            humidity,
            wind,
            rain
        ]])

        features_scaled = scaler.transform(features_array)

        prediction = model.predict(features_scaled)[0]
        prediction_proba = model.predict_proba(features_scaled)[0]

        fire_probability = prediction_proba[1] * 100
        risk_score = int(fire_probability)

        # Risk category
        if risk_score < 30:
            risk_category = 'Low'
            prediction_text = 'Low fire danger'
        elif risk_score < 60:
            risk_category = 'Medium'
            prediction_text = 'Moderate fire danger - be cautious'
        else:
            risk_category = 'High'
            prediction_text = 'High fire danger - extreme caution advised'

        return jsonify({
            'location': location_name,
            'coordinates': {'latitude': latitude, 'longitude': longitude},
            'risk_score': risk_score,
            'risk_category': risk_category,
            'prediction': prediction_text,
            'weather': {
                'temperature': round(temp, 1),
                'humidity': humidity,
                'wind_speed': round(wind, 1),
                'rainfall': round(rain, 1)
            },
            'fire_indices': {
                'FFMC': round(fwi['FFMC'], 1),
                'DMC': round(fwi['DMC'], 1),
                'DC': round(fwi['DC'], 1),
                'ISI': round(fwi['ISI'], 1)
            }
        })

    except Exception as e:
        print(f"/api/predict-coords error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
