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

# Load feature list
with open('models/features.txt', 'r') as f:
    features = f.read().strip().split(',')

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')

def get_weather_data(location):
    """Fetch current weather data from OpenWeatherMap API"""
    if not WEATHER_API_KEY:
        # Return mock data if no API key
        return {
            'temp': 22.0,
            'humidity': 45,
            'wind': 3.5,
            'rain': 0.0
        }
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code == 200:
            return {
                'temp': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'wind': data['wind']['speed'],
                'rain': data.get('rain', {}).get('1h', 0.0)
            }
        else:
            return None
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def calculate_fwi_indices(temp, humidity, wind, rain):
    """
    Simplified FWI calculation (approximation for demo)
    In production, use proper FWI calculation libraries
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
            '/api/predict': 'POST - Predict fire risk for a location',
            '/api/health': 'GET - Health check'
        }
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'model_loaded': True})

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        location = data.get('location', '')
        
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        # Get weather data
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
        
        # Scale and predict
        features_array = np.array([input_features])
        features_scaled = scaler.transform(features_array)
        
        prediction = model.predict(features_scaled)[0]
        probability = model.predict_proba(features_scaled)[0]
        
        # Calculate risk score (0-100)
        risk_score = int(probability[1] * 100)  # Probability of fire
        
        # Adjust for cold climates
        if weather['temp'] < 5:
            risk_score = min(risk_score, 20)
            risk_category = 'Low'
            prediction = 0  # No significant risk
        elif weather['temp'] < 10:
            risk_score = min(risk_score, 40)
        
        # Determine risk category based on adjusted score
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
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
