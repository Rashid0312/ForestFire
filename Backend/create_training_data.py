import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time

# Your OpenWeatherMap API key
WEATHER_API_KEY = "4e26f1f06107c946e49ea40a22ffb178"

print("=" * 60)
print("Creating ML Training Dataset from NASA Fire Data")
print("=" * 60)

# Load fire data
df_fires = pd.read_csv('data/nasa_fires_europe.csv')
print(f"\n📊 Loaded {len(df_fires)} fires")

# Sample 2000 fires (to avoid API limits and balance dataset)
df_sample = df_fires.sample(n=min(2000, len(df_fires)), random_state=42)
print(f"Sampled {len(df_sample)} fires for training")

# Prepare training data
training_data = []

print("\n🌡️ Fetching historical weather data...")
print("This will take ~10 minutes (2000 API calls)...\n")

for idx, row in df_sample.iterrows():
    if idx % 100 == 0:
        print(f"Progress: {idx}/{len(df_sample)} ({idx/len(df_sample)*100:.1f}%)")
    
    lat = row['latitude']
    lon = row['longitude']
    date = row['acq_date']
    
    # Get weather from OpenWeatherMap (current weather as proxy for historical)
    # Note: Free tier doesn't have historical, so we use current as approximation
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            weather = response.json()
            
            temp = weather['main']['temp']
            humidity = weather['main']['humidity']
            wind = weather['wind']['speed']
            rain = weather.get('rain', {}).get('1h', 0)
            
            # Calculate FWI indices (simplified)
            ffmc = 85 + ((100 - humidity) / 100) * 11
            dmc = max(0, (temp * 1.5) + ((100 - humidity) * 0.8) - (rain * 15))
            dc = max(0, (temp * 5) + ((100 - humidity) * 4) - (rain * 50))
            isi = (wind ** 0.5) * (ffmc / 30)
            
            training_data.append({
                'latitude': lat,
                'longitude': lon,
                'date': date,
                'temp': temp,
                'RH': humidity,
                'wind': wind,
                'rain': rain,
                'FFMC': ffmc,
                'DMC': dmc,
                'DC': dc,
                'ISI': isi,
                'fire': 1  # Fire occurred
            })
            
    except Exception as e:
        continue
    
    time.sleep(0.1)  # Rate limiting

print(f"\n✅ Collected weather for {len(training_data)} fire locations")

# Create negative samples (no fire)
print("\n❄️ Creating negative samples (no-fire locations)...")

np.random.seed(42)

for i in range(2000):  # Match number of fire samples
    # Random European location
    lat = np.random.uniform(35, 71)
    lon = np.random.uniform(-25, 45)
    
    # Get weather
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            weather = response.json()
            
            temp = weather['main']['temp']
            humidity = weather['main']['humidity']
            wind = weather['wind']['speed']
            rain = weather.get('rain', {}).get('1h', 0)
            
            # Calculate indices
            ffmc = 85 + ((100 - humidity) / 100) * 11
            dmc = max(0, (temp * 1.5) + ((100 - humidity) * 0.8) - (rain * 15))
            dc = max(0, (temp * 5) + ((100 - humidity) * 4) - (rain * 50))
            isi = (wind ** 0.5) * (ffmc / 30)
            
            training_data.append({
                'latitude': lat,
                'longitude': lon,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'temp': temp,
                'RH': humidity,
                'wind': wind,
                'rain': rain,
                'FFMC': ffmc,
                'DMC': dmc,
                'DC': dc,
                'ISI': isi,
                'fire': 0  # No fire
            })
    except:
        continue
    
    if i % 200 == 0:
        print(f"Progress: {i}/2000")
    
    time.sleep(0.1)

# Save training dataset
df_training = pd.DataFrame(training_data)
df_training.to_csv('data/fire_training_dataset.csv', index=False)

print("\n" + "=" * 60)
print("✅ Training dataset created!")
print("=" * 60)
print(f"\nTotal records: {len(df_training)}")
print(f"Fire events: {df_training['fire'].sum()} ({df_training['fire'].sum()/len(df_training)*100:.1f}%)")
print(f"No-fire events: {len(df_training) - df_training['fire'].sum()} ({(len(df_training) - df_training['fire'].sum())/len(df_training)*100:.1f}%)")

print("\n📊 Sample:")
print(df_training.head(10))

print("\n✅ Saved to: data/fire_training_dataset.csv")
print("\n🚀 Ready to retrain your model with European fire data!")

