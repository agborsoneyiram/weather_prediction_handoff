"""Fetch Historical from Open-Meteo"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import config, requests, pandas as pd

def fetch_historical():
    print("\n📡 FETCHING FROM OPEN-METEO")
    all_data = []
    
    for loc_key, loc_info in config.LOCATIONS.items():
        print(f"📍 {loc_info['name']}...", end=" ")
        params = {
            'latitude': loc_info['lat'],
            'longitude': loc_info['lon'],
            'start_date': config.START_DATE,
            'end_date': config.END_DATE,
            'hourly': 'temperature_2m,relative_humidity_2m,precipitation',
            'timezone': 'Africa/Accra'
        }
        try:
            r = requests.get(config.OPEN_METEO_API, params=params, timeout=60)
            data = r.json()['hourly']
            df = pd.DataFrame({
                'timestamp': pd.to_datetime(data['time']),
                'temp': data['temperature_2m'],
                'rhum': data['relative_humidity_2m'],
                'prcp': data['precipitation'],
                'location': loc_key
            })
            all_data.append(df)
            print(f"✅ {len(df):,}")
        except Exception as e:
            print(f"❌ {e}")
    
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        output = config.DATA_DIR / "historical" / "data.csv"
        combined.to_csv(output, index=False)
        print(f"✅ Total: {len(combined):,} | Saved: {output}")
        return combined

if __name__ == "__main__":
    fetch_historical()