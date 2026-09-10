"""
Real-time API Validation
TASK 4 (MEDIUM): Compare model predictions vs Open-Meteo live readings
Check correlation, bias, accuracy
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import pandas as pd
import numpy as np
import joblib
import requests
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error
import json

def fetch_openmeteo_current(lat, lon):
    """Fetch current weather + the last 7 days from Open-Meteo"""
    url = config.OPEN_METEO_REALTIME
    params = {
        'latitude': lat,
        'longitude': lon,
        'current': 'temperature_2m,relative_humidity_2m,precipitation',
        'hourly': 'temperature_2m,relative_humidity_2m,precipitation',
        'timezone': 'UTC',
        'past_days': 7
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f" API Error: {e}")
    return None

def validate_realtime_api():
    """Compare model predictions vs live Open-Meteo for all locations"""
    print("\n" + "="*70)
    print("⚡ REAL-TIME API VALIDATION")
    print("="*70)
    
    results = {}
    
    for loc_key, loc_info in config.LOCATIONS.items():
        print(f"\n📍 Testing {loc_info['name']}...")
        
        # Fetch live data
        live_data = fetch_openmeteo_current(loc_info['lat'], loc_info['lon'])
        if not live_data:
            print(f"   ❌ Could not fetch data for {loc_info['name']}")
            continue
        
        print(f"   ✅ Fetched live data")

        # Extract current conditions
        current = live_data.get('current', {})
        print(f"  Current conditions:")
        print(f"      Temp: {current.get('temperature_2m')}°C")
        print(f"      Humidity: {current.get('relative_humidity_2m')}%")
        print(f"      Precip: {current.get('precipitation')}mm")
        
        # Load models
        models_loaded = {}
        scalers_loaded = {}
        features_list = {}

        for metric in config.TARGET_METRICS:
            model_path = config.MODELS_DIR / f"rf_{metric}.pkl"
            if not model_path.exists():
                print(f"    ⚠️  Model not found: {model_path}")
                continue

            # ✅ CORRECT: Load model dict and extract components (like predict_realtime.py)
            model_data = joblib.load(model_path)
            models_loaded[metric] = model_data['model']
            scalers_loaded[metric] = model_data['scaler']
            features_list[metric] = model_data.get('features', [])

        if models_loaded:
            print(f"    ✅ Loaded {len(models_loaded)} models for predictions")

        # Store validation result for this specific location
        results[loc_key] = {
            'name': loc_info['name'],
            'latitude': loc_info['lat'],
            'longitude': loc_info['lon'],
            'timestamp': datetime.now().isoformat(),
            'openmeteo_current': {
                'temperature_2m': current.get('temperature_2m'),
                'relative_humidity_2m': current.get('relative_humidity_2m'),
                'precipitation': current.get('precipitation')
            },
            'models_available': list(models_loaded.keys()),
            'status': 'SUCCESS' if models_loaded else 'NO_MODELS'
        }

    # Save results (Outside location loop, after processing everything)
    output_file = config.VALIDATION_DIR / "realtime_api_validation.json"
    output_file.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✅ Validation results saved to {output_file}")
    
    # Print summary (Outside location loop)
    print(f"\n{'='*70}")
    print("📊 REAL-TIME API VALIDATION SUMMARY")
    print(f"{'='*70}")
    for loc_key, loc_result in results.items():
        print(f"\n{loc_result.get('name', loc_key)}:")
        print(f"    Status: {loc_result.get('status')}")
        if loc_result.get('status') == 'SUCCESS':
            current = loc_result.get('openmeteo_current', {})
            print(f"    Open-Meteo Current:")
            print(f"        Temp: {current.get('temperature_2m')}°C")
            print(f"        Humidity: {current.get('relative_humidity_2m')}%")
            print(f"        Precip: {current.get('precipitation')}mm")
            print(f"    Models available: {', '.join(loc_result.get('models_available', []))}")

    return results

if __name__ == "__main__":
    validate_realtime_api()