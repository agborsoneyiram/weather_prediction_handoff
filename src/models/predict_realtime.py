"""
Real-Time Prediction System
Gets current weather from Open-Meteo → ML model → Tomorrow's forecast

This is the CORE of your system:
1. Open-Meteo provides current conditions (virtual sensor)
2. ML model uses current + past 24h to predict next 24h
3. Can be replaced with Arduino data later
"""

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
    """
    Get current weather from Open-Meteo API
    This acts as VIRTUAL SENSOR until Arduino is deployed
    """
    
    loc = config.LOCATIONS[location]
    
    params = {
        'latitude': loc['lat'],
        'longitude': loc['lon'],
        'current': 'temperature_2m,relative_humidity_2m,precipitation',
        'hourly': 'temperature_2m,relative_humidity_2m,precipitation',
        'timezone': 'Africa/Accra',
        'past_hours': 24  # Get past 24h for ML context
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
        print(f"❌ Error fetching real-time data: {e}")
        return None

def create_features_for_prediction(current_data, metric):
    """
    Create same features used during training
    This ensures model gets data in correct format
    """
    
    tomorrow = datetime.now() + timedelta(hours=24)
    recent_values = current_data['recent_24h'][metric]
    
    features = {}
    
    # Time features for TOMORROW (what we're predicting)
    features['hour'] = tomorrow.hour
    features['month'] = tomorrow.month
    features['day_of_week'] = tomorrow.weekday()
    features['hour_sin'] = np.sin(2 * np.pi * tomorrow.hour / 24)
    features['hour_cos'] = np.cos(2 * np.pi * tomorrow.hour / 24)
    features['month_sin'] = np.sin(2 * np.pi * tomorrow.month / 12)
    features['month_cos'] = np.cos(2 * np.pi * tomorrow.month / 12)
    features['is_weekend'] = 1 if tomorrow.weekday() >= 5 else 0
    
    # Lag features from recent data
    for lag in config.LAG_HOURS:
        if len(recent_values) >= lag:
            features[f'{metric}_lag_{lag}h'] = recent_values[-lag]
        else:
            features[f'{metric}_lag_{lag}h'] = recent_values[0]
    
    # Rolling features
    for window in config.ROLLING_WINDOWS:
        window_data = recent_values[-window:] if len(recent_values) >= window else recent_values
        features[f'{metric}_rolling_mean_{window}h'] = np.mean(window_data)
        features[f'{metric}_rolling_std_{window}h'] = np.std(window_data)
    
    # Difference feature
    if len(recent_values) >= 2:
        features[f'{metric}_diff_1h'] = recent_values[-1] - recent_values[-2]
    else:
        features[f'{metric}_diff_1h'] = 0
    
    return features

def predict_next_day(location='kasoa'):
    """
    MAIN PREDICTION FUNCTION
    This is what runs every 30 minutes to update forecast
    """
    
    print("\n" + "="*70)
    print(f"🔮 PREDICTING TOMORROW'S WEATHER - {location.upper()}")
    print("="*70)
    
    # Step 1: Get current weather from Open-Meteo
    print("\n📡 Step 1: Getting current weather from Open-Meteo...")
    current_data = get_current_weather_openmeteo(location)
    
    if not current_data:
        print("❌ Failed to get current weather")
        return None
    
    print(f"✅ Current conditions:")
    print(f"   Temperature: {current_data['current']['temp']}°C")
    print(f"   Humidity: {current_data['current']['rhum']}%")
    print(f"   Rainfall: {current_data['current']['prcp']}mm")
    
    # Step 2: Load trained models and predict
    print(f"\n🤖 Step 2: Running ML predictions...")
    
    predictions = {}
    tomorrow = datetime.now() + timedelta(hours=24)
    
    for metric in config.TARGET_METRICS:
        # Load model
        model_path = config.MODELS_DIR / f"rf_{metric}.pkl"
        
        if not model_path.exists():
            print(f"   ⚠️ Model not found for {metric}")
            continue
        
        model_data = joblib.load(model_path)
        model = model_data['model']
        scaler = model_data['scaler']
        feature_names = model_data['features']
        
        # Create features
        features = create_features_for_prediction(current_data, metric)
        
        # Build feature vector in correct order
        feature_vector = np.array([[features.get(f, 0) for f in feature_names]])
        
        # Scale and predict
        scaled = scaler.transform(feature_vector)
        prediction = model.predict(scaled)[0]
        
        predictions[metric] = round(float(prediction), 2)
        
        # Display
        unit = {'temp': '°C', 'rhum': '%', 'prcp': 'mm'}[metric]
        print(f"   ✅ {metric.upper()}: {predictions[metric]}{unit}")
    
    # Step 3: Generate summary
    summary = generate_weather_summary(predictions)
    
    result = {
        'current_time': datetime.now().isoformat(),
        'prediction_for': tomorrow.isoformat(),
        'location': location,
        'current_conditions': current_data['current'],
        'predictions': predictions,
        'summary': summary
    }
    
    print(f"\n🌤️ Summary: {summary}")
    print("="*70)
    
    # Save prediction log
    save_prediction(result)
    
    return result

def generate_weather_summary(predictions):
    """Generate human-readable summary"""
    temp = predictions.get('temp', 0)
    rhum = predictions.get('rhum', 0)
    prcp = predictions.get('prcp', 0)
    
    parts = []
    
    # Temperature
    if temp >= 35:
        parts.append("Very hot")
    elif temp >= 30:
        parts.append("Hot")
    elif temp >= 25:
        parts.append("Warm")
    else:
        parts.append("Moderate temperature")
    
    # Humidity
    if rhum >= 85:
        parts.append("very humid")
    elif rhum >= 70:
        parts.append("humid")
    
    # Rainfall
    if prcp >= 20:
        parts.append("heavy rain expected ⚠️")
    elif prcp >= 10:
        parts.append("moderate rain expected")
    elif prcp >= 2:
        parts.append("light rain possible")
    else:
        parts.append("no rain expected")
    
    return ", ".join(parts)

def save_prediction(result):
    """Save prediction to log file"""
    log_file = config.OUTPUTS_DIR / "predictions" / "prediction_log.csv"
    
    df = pd.DataFrame([{
        'timestamp': result['current_time'],
        'prediction_for': result['prediction_for'],
        'location': result['location'],
        'predicted_temp': result['predictions'].get('temp'),
        'predicted_rhum': result['predictions'].get('rhum'),
        'predicted_prcp': result['predictions'].get('prcp'),
        'summary': result['summary']
    }])
    
    if log_file.exists():
        df.to_csv(log_file, mode='a', header=False, index=False)
    else:
        df.to_csv(log_file, index=False)

if __name__ == "__main__":
    # Run prediction for both locations
    print("\n🌍 Running predictions for Kasoa and Accra...\n")
    
    kasoa_forecast = predict_next_day('kasoa')
    accra_forecast = predict_next_day('accra')
    
    print("\n✅ Predictions complete!")
    print("\n💡 This script should run every 30 minutes to keep forecasts updated")
    print("   You can automate this with Windows Task Scheduler")