"""
Prediction Tracker - Records daily predictions and validates them
Outputs in Excel-ready format showing predicted vs actual
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
import json

def get_current_weather(location='kasoa'):
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

def create_features(current_data, metric):
    """Create prediction features"""
    tomorrow = datetime.now() + timedelta(hours=24)
    recent = current_data['recent_24h'][metric]
    
    features = {
        'hour': tomorrow.hour,
        'month': tomorrow.month,
        'day_of_week': tomorrow.weekday(),
        'hour_sin': np.sin(2 * np.pi * tomorrow.hour / 24),
        'hour_cos': np.cos(2 * np.pi * tomorrow.hour / 24),
        'month_sin': np.sin(2 * np.pi * tomorrow.month / 12),
        'month_cos': np.cos(2 * np.pi * tomorrow.month / 12),
        'is_weekend': 1 if tomorrow.weekday() >= 5 else 0,
    }
    
    for lag in config.LAG_HOURS:
        if len(recent) >= lag:
            features[f'{metric}_lag_{lag}h'] = recent[-lag]
        else:
            features[f'{metric}_lag_{lag}h'] = recent[0]
    
    for window in config.ROLLING_WINDOWS:
        window_data = recent[-window:] if len(recent) >= window else recent
        features[f'{metric}_rolling_mean_{window}h'] = np.mean(window_data)
        features[f'{metric}_rolling_std_{window}h'] = np.std(window_data)
    
    if len(recent) >= 2:
        features[f'{metric}_diff_1h'] = recent[-1] - recent[-2]
    else:
        features[f'{metric}_diff_1h'] = 0
    
    return features

def record_prediction(location='kasoa'):
    """
    Make prediction TODAY and save it
    Next day, we'll validate it
    """
    print(f"\n{'='*70}")
    print(f"📝 RECORDING PREDICTION FOR {location.upper()}")
    print(f"{'='*70}")
    
    # Get current weather
    current_data = get_current_weather(location)
    if not current_data:
        print("❌ Failed to get weather")
        return
    
    print(f"\n📡 Current: {current_data['current']['temp']}°C, {current_data['current']['rhum']}% RH")
    
    # Make predictions
    predictions = {}
    for metric in config.TARGET_METRICS:
        model_path = config.MODELS_DIR / f"rf_{metric}.pkl"
        if not model_path.exists():
            continue
        
        model_data = joblib.load(model_path)
        model = model_data['model']
        scaler = model_data['scaler']
        feature_names = model_data['features']
        
        features = create_features(current_data, metric)
        feature_vector = np.array([[features.get(f, 0) for f in feature_names]])
        
        scaled = scaler.transform(feature_vector)
        prediction = model.predict(scaled)[0]
        predictions[metric] = round(float(prediction), 2)
    
    # Save to tracking file
    today = datetime.now().date()
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    
    tracking_file = config.OUTPUTS_DIR / "predictions" / f"tracking_{location}.csv"
    tracking_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create record
    record = {
        'Date': str(tomorrow),
        'Predicted_Temp': predictions.get('temp'),
        'Predicted_Humidity': predictions.get('rhum'),
        'Predicted_Rain': predictions.get('prcp'),
        'Recorded_Date': str(today),
        'Recorded_Time': datetime.now().strftime('%H:%M:%S'),
        'Actual_Temp': None,
        'Actual_Humidity': None,
        'Actual_Rain': None,
        'Temp_Error': None,
        'Humidity_Error': None,
        'Rain_Error': None,
        'Temp_Status': None,
        'Humidity_Status': None,
        'Rain_Status': None
    }
    
    df = pd.DataFrame([record])
    
    if tracking_file.exists():
        df.to_csv(tracking_file, mode='a', header=False, index=False)
    else:
        df.to_csv(tracking_file, index=False)
    
    print(f"\n✅ Prediction recorded for {tomorrow}:")
    print(f"   🌡️  Temperature: {predictions.get('temp')}°C")
    print(f"   💧 Humidity: {predictions.get('rhum')}%")
    print(f"   🌧️  Rainfall: {predictions.get('prcp')}mm")
    print(f"\n💾 Saved to: {tracking_file}")

def validate_yesterday(location='kasoa'):
    """
    Check yesterday's prediction against actual values
    Update the tracking file with actual data and errors
    """
    print(f"\n{'='*70}")
    print(f"✅ VALIDATING YESTERDAY'S PREDICTION - {location.upper()}")
    print(f"{'='*70}")
    
    # Get actual weather from yesterday
    yesterday = (datetime.now() - timedelta(days=1)).date()
    
    # Fetch from Open-Meteo historical
    loc = config.LOCATIONS[location]
    
    params = {
        'latitude': loc['lat'],
        'longitude': loc['lon'],
        'start_date': str(yesterday),
        'end_date': str(yesterday),
        'hourly': 'temperature_2m,relative_humidity_2m,precipitation',
        'timezone': 'Africa/Accra'
    }
    
    try:
        response = requests.get(config.OPEN_METEO_API, params=params, timeout=30)
        data = response.json()
        
        # Calculate daily averages
        temps = data['hourly']['temperature_2m']
        humids = data['hourly']['relative_humidity_2m']
        precips = data['hourly']['precipitation']
        
        actual_temp = np.mean(temps)
        actual_humidity = np.mean(humids)
        actual_rain = np.sum(precips)
        
        print(f"\n📊 Actual values for {yesterday}:")
        print(f"   🌡️  Temperature: {actual_temp:.2f}°C")
        print(f"   💧 Humidity: {actual_humidity:.2f}%")
        print(f"   🌧️  Rainfall: {actual_rain:.2f}mm")
        
        # Load tracking file and update
        tracking_file = config.OUTPUTS_DIR / "predictions" / f"tracking_{location}.csv"
        
        if not tracking_file.exists():
            print(f"⚠️ No predictions file found for {location}")
            return
        
        df = pd.read_csv(tracking_file)
        
        # Find the row for this date
        mask = df['Date'] == str(yesterday)
        if mask.sum() == 0:
            print(f"⚠️ No prediction found for {yesterday}")
            return
        
        # Update the row
        temp_error = actual_temp - df.loc[mask, 'Predicted_Temp'].values[0]
        humidity_error = actual_humidity - df.loc[mask, 'Predicted_Humidity'].values[0]
        rain_error = actual_rain - df.loc[mask, 'Predicted_Rain'].values[0]
        
        # Determine status (Good/OK/Wrong)
        def get_status(error, threshold):
            if abs(error) <= threshold:
                return "✓ Good"
            elif abs(error) <= threshold * 2:
                return "~ OK"
            else:
                return "✗ Wrong"
        
        temp_status = get_status(temp_error, 0.5)
        humidity_status = get_status(humidity_error, 3)
        rain_status = get_status(rain_error, 1)
        
        # Update DataFrame
        df.loc[mask, 'Actual_Temp'] = round(actual_temp, 2)
        df.loc[mask, 'Actual_Humidity'] = round(actual_humidity, 2)
        df.loc[mask, 'Actual_Rain'] = round(actual_rain, 2)
        df.loc[mask, 'Temp_Error'] = round(temp_error, 2)
        df.loc[mask, 'Humidity_Error'] = round(humidity_error, 2)
        df.loc[mask, 'Rain_Error'] = round(rain_error, 2)
        df.loc[mask, 'Temp_Status'] = temp_status
        df.loc[mask, 'Humidity_Status'] = humidity_status
        df.loc[mask, 'Rain_Status'] = rain_status
        
        # Save updated file
        df.to_csv(tracking_file, index=False)
        
        print(f"\n✅ Validation complete for {yesterday}:")
        print(f"   🌡️  Error: {temp_error:+.2f}°C ({temp_status})")
        print(f"   💧 Error: {humidity_error:+.2f}% ({humidity_status})")
        print(f"   🌧️  Error: {rain_error:+.2f}mm ({rain_status})")
        print(f"\n💾 Updated: {tracking_file}")
        
        # Show tracking table
        print(f"\n📋 TRACKING TABLE:")
        print(df[['Date', 'Predicted_Temp', 'Actual_Temp', 'Temp_Error', 'Temp_Status']].to_string(index=False))
        
    except Exception as e:
        print(f"❌ Error validating: {e}")

def show_tracking_table(location='kasoa'):
    """Display the tracking table"""
    tracking_file = config.OUTPUTS_DIR / "predictions" / f"tracking_{location}.csv"
    
    if not tracking_file.exists():
        print(f"⚠️ No tracking data for {location}")
        return
    
    df = pd.read_csv(tracking_file)
    
    print(f"\n{'='*70}")
    print(f"📊 PREDICTION TRACKING TABLE - {location.upper()}")
    print(f"{'='*70}\n")
    
    # Temperature table
    print("🌡️  TEMPERATURE:")
    print(df[['Date', 'Predicted_Temp', 'Actual_Temp', 'Temp_Error', 'Temp_Status']].to_string(index=False))
    
    # Humidity table
    print("\n💧 HUMIDITY:")
    print(df[['Date', 'Predicted_Humidity', 'Actual_Humidity', 'Humidity_Error', 'Humidity_Status']].to_string(index=False))
    
    # Rainfall table
    print("\n🌧️  RAINFALL:")
    print(df[['Date', 'Predicted_Rain', 'Actual_Rain', 'Rain_Error', 'Rain_Status']].to_string(index=False))
    
    print(f"\n💾 Full data: {tracking_file}")
    print(f"✅ Can open in Excel for presentation")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true', help='Record today\'s prediction')
    parser.add_argument('--validate', action='store_true', help='Validate yesterday\'s prediction')
    parser.add_argument('--show', action='store_true', help='Show tracking table')
    parser.add_argument('--location', default='kasoa', help='Location (kasoa or accra)')
    
    args = parser.parse_args()
    
    if args.record:
        record_prediction(args.location)
    elif args.validate:
        validate_yesterday(args.location)
    elif args.show:
        show_tracking_table(args.location)
    else:
        print("\nUsage:")
        print("  Record prediction:  python prediction_tracker.py --record --location kasoa")
        print("  Validate yesterday: python prediction_tracker.py --validate --location kasoa")
        print("  Show table:         python prediction_tracker.py --show --location kasoa")