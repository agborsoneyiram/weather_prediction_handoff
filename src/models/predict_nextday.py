"""Next-Day Prediction System"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import joblib
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def get_current_weather_openmeteo(location='kasoa'):
    """Get current weather from Open-Meteo"""
    loc = config.LOCATIONS[location]
    
    params = {
        'latitude': loc['lat'],
        'longitude': loc['lon'],
        'current': 'temperature_2m,relative_humidity_2m,precipitation',
        'hourly': 'temperature_2m,relative_humidity_2m,precipitation',
        'timezone': 'Africa/Accra',
        'past_hours': 24
    }
    
    try:
        response = requests.get(config.OPEN_METEO_REALTIME, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        current = data['current']
        hourly = data['hourly']
        
        return {
            'timestamp': datetime.now(),
            'location': location,
            'current': {
                'temp': current['temperature_2m'],
                'rhum': current['relative_humidity_2m'],
                'prcp': current.get('precipitation', 0)
            },
            'recent_24h': {
                'temp': hourly['temperature_2m'][:24],
                'rhum': hourly['relative_humidity_2m'][:24],
                'prcp': hourly['precipitation'][:24]
            }
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_features_for_prediction(current_data, metric):
    """Create same features used during training"""
    tomorrow = datetime.now() + timedelta(hours=24)
    recent_values = current_data['recent_24h'][metric]
    
    features = {}
    
    features['hour'] = tomorrow.hour
    features['month'] = tomorrow.month
    features['day_of_week'] = tomorrow.weekday()
    features['hour_sin'] = np.sin(2 * np.pi * tomorrow.hour / 24)
    features['hour_cos'] = np.cos(2 * np.pi * tomorrow.hour / 24)
    features['month_sin'] = np.sin(2 * np.pi * tomorrow.month / 12)
    features['month_cos'] = np.cos(2 * np.pi * tomorrow.month / 12)
    features['is_weekend'] = 1 if tomorrow.weekday() >= 5 else 0
    
    for lag in config.LAG_HOURS:
        if len(recent_values) >= lag:
            features[f'{metric}_lag_{lag}h'] = recent_values[-lag]
        else:
            features[f'{metric}_lag_{lag}h'] = recent_values[0]
    
    for window in config.ROLLING_WINDOWS:
        window_data = recent_values[-window:] if len(recent_values) >= window else recent_values
        features[f'{metric}_rolling_mean_{window}h'] = np.mean(window_data)
        features[f'{metric}_rolling_std_{window}h'] = np.std(window_data)
    
    if len(recent_values) >= 2:
        features[f'{metric}_diff_1h'] = recent_values[-1] - recent_values[-2]
    else:
        features[f'{metric}_diff_1h'] = 0
    
    return features

def predict_next_day(location='kasoa'):
    """Main prediction function"""
    
    print("\n" + "="*70)
    print(f"🔮 PREDICTING TOMORROW'S WEATHER - {location.upper()}")
    print("="*70)
    
    print("\n📡 Step 1: Getting current weather from Open-Meteo...")
    current_data = get_current_weather_openmeteo(location)
    
    if not current_data:
        print("❌ Failed to get current weather")
        return None
    
    print(f"✅ Current conditions:")
    print(f"   Temperature: {current_data['current']['temp']}°C")
    print(f"   Humidity: {current_data['current']['rhum']}%")
    print(f"   Rainfall: {current_data['current']['prcp']}mm")
    
    print(f"\n🤖 Step 2: Running ML predictions...")
    
    predictions = {}
    tomorrow = datetime.now() + timedelta(hours=24)
    
    for metric in config.TARGET_METRICS:
        model_path = config.MODELS_DIR / f"rf_{metric}.pkl"
        
        if not model_path.exists():
            print(f"   ⚠️ Model not found for {metric}")
            continue
        
        model_data = joblib.load(model_path)
        model = model_data['model']
        scaler = model_data['scaler']
        feature_names = model_data['features']
        
        features = create_features_for_prediction(current_data, metric)
        feature_vector = np.array([[features.get(f, 0) for f in feature_names]])
        
        scaled = scaler.transform(feature_vector)
        prediction = model.predict(scaled)[0]
        
        predictions[metric] = round(float(prediction), 2)
        
        unit = {'temp': '°C', 'rhum': '%', 'prcp': 'mm'}[metric]
        print(f"   ✅ {metric.upper()}: {predictions[metric]}{unit}")
    
    summary = generate_weather_summary(predictions)
    
    print(f"\n🌤️ Summary: {summary}")
    print("="*70)
    
    return {
        'location': location,
        'timestamp': datetime.now(),
        'predictions': predictions,
        'summary': summary
    }

def generate_weather_summary(predictions):
    """Generate summary"""
    temp = predictions.get('temp', 0)
    rhum = predictions.get('rhum', 0)
    prcp = predictions.get('prcp', 0)
    
    parts = []
    
    if temp >= 35:
        parts.append("Very hot")
    elif temp >= 30:
        parts.append("Hot")
    elif temp >= 25:
        parts.append("Warm")
    else:
        parts.append("Moderate temperature")
    
    if rhum >= 85:
        parts.append("very humid")
    elif rhum >= 70:
        parts.append("humid")
    
    if prcp >= 20:
        parts.append("heavy rain ⚠️")
    elif prcp >= 10:
        parts.append("moderate rain")
    elif prcp >= 2:
        parts.append("light rain possible")
    else:
        parts.append("no rain")
    
    return ", ".join(parts)

if __name__ == "__main__":
    print("\n🌍 Running predictions for Kasoa and Accra...\n")
    
    kasoa = predict_next_day('kasoa')
    accra = predict_next_day('accra')
    
    print("\n✅ Predictions complete!")