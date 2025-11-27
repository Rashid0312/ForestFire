import requests
import pandas as pd
import time
from datetime import datetime

MAP_KEY = "2da038f02350a34943952b98722f1fc0"

print("=" * 60)
print("NASA FIRMS Historical Fire Data (Standard Processing)")
print("=" * 60)

EUROPE_BBOX = "-25,35,45,71"

all_fires = []

# Download fire season months using MODIS_SP (Standard Processing - has historical data)
years = [2020, 2021, 2022, 2023, 2024]
fire_months = [
    ('06', '01'),  # June
    ('06', '15'),
    ('07', '01'),  # July
    ('07', '15'),
    ('08', '01'),  # August
    ('08', '15'),
    ('09', '01'),  # September
]

chunk_count = 0

for year in years:
    print(f"\n🔥 Year {year}:")
    
    for month, day in fire_months:
        chunk_count += 1
        date_str = f"{year}-{month}-{day}"
        
        print(f"  {date_str}...", end=" ")
        
        # Use MODIS_SP for historical data (not NRT)
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/MODIS_SP/{EUROPE_BBOX}/10/{date_str}"
        
        try:
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200 and len(response.text) > 200:
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))
                
                if len(df) > 0:
                    all_fires.append(df)
                    print(f"✅ {len(df)} fires")
                else:
                    print("⚪ 0")
            else:
                print(f"⚪ 0")
                
        except Exception as e:
            print(f"❌ {e}")
        
        time.sleep(1)

# Combine
if all_fires:
    print("\n" + "=" * 60)
    print("Processing...")
    print("=" * 60)
    
    df_all = pd.concat(all_fires, ignore_index=True)
    
    print(f"\n✅ Total fires: {len(df_all)}")
    print(f"Date range: {df_all['acq_date'].min()} to {df_all['acq_date'].max()}")
    
    # Filter high confidence
    df_high = df_all[df_all['confidence'] >= 50].copy()
    print(f"High confidence (≥50%): {len(df_high)}")
    
    # Save
    df_high.to_csv('data/nasa_fires_europe.csv', index=False)
    
    print("\n✅ Saved to: data/nasa_fires_europe.csv")
    print("\n📊 Sample:")
    print(df_high[['latitude', 'longitude', 'acq_date', 'brightness', 'confidence']].head())
    
    print("\n🎉 SUCCESS! Ready to train your model!")
    
else:
    print("\n❌ No fires downloaded")
