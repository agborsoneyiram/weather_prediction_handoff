"""
Arduino Sensor Integration
Reads real sensor data from DHT22 + Rain Gauge

Hardware Setup:
- DHT22: Temperature + Humidity sensor
- Rain Gauge: Tipping bucket type
- Arduino Uno connected via USB

This REPLACES Open-Meteo with real physical measurements
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import serial
import json
import pandas as pd
from datetime import datetime
import time

class ArduinoWeatherStation:
    """
    Interface with Arduino weather sensors
    
    Arduino should send JSON format:
    {"temp": 28.5, "humidity": 75.2, "rainfall": 0.0}
    """
    
    def __init__(self, port='COM3', baudrate=9600):
        """
        Initialize serial connection to Arduino
        
        port: COM port (Windows) or /dev/ttyUSB0 (Linux)
        baudrate: 9600 is standard for Arduino
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.connected = False
        
    def connect(self):
        """Establish connection with Arduino"""
        try:
            self.serial_connection = serial.Serial(
                self.port,
                self.baudrate,
                timeout=2
            )
            time.sleep(2)  # Wait for Arduino to reset
            self.connected = True
            print(f"✅ Connected to Arduino on {self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Arduino: {e}")
            print("   Make sure Arduino is plugged in and port is correct")
            self.connected = False
            return False
    
    def read_sensors(self):
        """
        Read current sensor values from Arduino
        
        Returns dict: {'temp': float, 'rhum': float, 'prcp': float}
        """
        
        if not self.connected:
            print("⚠️ Arduino not connected")
            return None
        
        try:
            # Read line from Arduino
            if self.serial_connection.in_waiting > 0:
                line = self.serial_connection.readline().decode('utf-8').strip()
                
                # Parse JSON
                data = json.loads(line)
                
                reading = {
                    'timestamp': datetime.now(),
                    'temp': data.get('temp'),
                    'rhum': data.get('humidity'),
                    'prcp': data.get('rainfall', 0),
                    'source': 'arduino'
                }
                
                print(f"📟 Arduino Reading:")
                print(f"   Temp: {reading['temp']}°C")
                print(f"   Humidity: {reading['rhum']}%")
                print(f"   Rainfall: {reading['prcp']}mm")
                
                return reading
            else:
                return None
                
        except json.JSONDecodeError as e:
            print(f"⚠️ Invalid data from Arduino: {e}")
            return None
        except Exception as e:
            print(f"❌ Error reading sensors: {e}")
            return None
    
    def calibrate_sensors(self, duration_minutes=30):
        """
        30-day calibration protocol
        Compare Arduino vs Open-Meteo readings
        
        For thesis: Run this for 30 days to validate Arduino accuracy
        """
        
        print(f"\n📊 CALIBRATION MODE - {duration_minutes} minutes")
        print("   Comparing Arduino vs Open-Meteo...")
        
        calibration_data = []
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            # Read Arduino
            arduino_reading = self.read_sensors()
            
            if arduino_reading:
                # Also get Open-Meteo reading for comparison
                try:
                    import requests
                    from predict_realtime import get_current_weather_openmeteo
                    
                    openmeteo_reading = get_current_weather_openmeteo('kasoa')
                    
                    comparison = {
                        'timestamp': datetime.now(),
                        'arduino_temp': arduino_reading['temp'],
                        'openmeteo_temp': openmeteo_reading['current']['temp'],
                        'temp_diff': abs(arduino_reading['temp'] - openmeteo_reading['current']['temp']),
                        'arduino_rhum': arduino_reading['rhum'],
                        'openmeteo_rhum': openmeteo_reading['current']['rhum'],
                        'rhum_diff': abs(arduino_reading['rhum'] - openmeteo_reading['current']['rhum'])
                    }
                    
                    calibration_data.append(comparison)
                    
                    print(f"\n🔍 Comparison:")
                    print(f"   Temp diff: {comparison['temp_diff']:.2f}°C")
                    print(f"   Humidity diff: {comparison['rhum_diff']:.2f}%")
                    
                except Exception as e:
                    print(f"⚠️ Could not get Open-Meteo comparison: {e}")
            
            time.sleep(60)  # Read every minute
        
        # Save calibration results
        if calibration_data:
            df = pd.DataFrame(calibration_data)
            output = config.DATA_DIR / "arduino" / "calibration_results.csv"
            df.to_csv(output, index=False)
            
            print(f"\n✅ Calibration complete!")
            print(f"   Average temp difference: {df['temp_diff'].mean():.2f}°C")
            print(f"   Average humidity difference: {df['rhum_diff'].mean():.2f}%")
            print(f"   Saved to: {output}")
        
        return calibration_data
    
    def save_reading(self, reading):
        """Save Arduino reading to database"""
        
        df = pd.DataFrame([reading])
        output = config.DATA_DIR / "arduino" / "sensor_readings.csv"
        
        if output.exists():
            df.to_csv(output, mode='a', header=False, index=False)
        else:
            df.to_csv(output, index=False)
    
    def disconnect(self):
        """Close serial connection"""
        if self.serial_connection:
            self.serial_connection.close()
            print("✅ Disconnected from Arduino")

def arduino_sample_code():
    """
    Arduino Code (upload this to your Arduino)
    Copy this into Arduino IDE
    """
    
    code = '''
// Weather Station Arduino Code
// DHT22 + Rain Gauge

#include <DHT.h>

#define DHTPIN 2        // DHT22 data pin
#define DHTTYPE DHT22
#define RAIN_PIN 3      // Rain gauge interrupt pin

DHT dht(DHTPIN, DHTTYPE);

volatile int rainTips = 0;  // Count rain gauge tips
const float mmPerTip = 0.2; // 0.2mm per tip

void setup() {
  Serial.begin(9600);
  dht.begin();
  
  // Attach interrupt for rain gauge
  pinMode(RAIN_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(RAIN_PIN), rainTip, FALLING);
}

void rainTip() {
  rainTips++;
}

void loop() {
  // Read DHT22
  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  // Calculate rainfall
  float rainfall = rainTips * mmPerTip;
  
  // Check if readings are valid
  if (!isnan(temp) && !isnan(humidity)) {
    // Send as JSON
    Serial.print("{");
    Serial.print("\\"temp\\":");
    Serial.print(temp);
    Serial.print(",\\"humidity\\":");
    Serial.print(humidity);
    Serial.print(",\\"rainfall\\":");
    Serial.print(rainfall);
    Serial.println("}");
  }
  
  delay(5000);  // Read every 5 seconds
}
'''
    
    print("\n" + "="*70)
    print("📟 ARDUINO CODE")
    print("="*70)
    print(code)
    print("="*70)
    print("\n💡 Instructions:")
    print("   1. Install DHT sensor library in Arduino IDE")
    print("   2. Connect DHT22 data pin to Arduino pin 2")
    print("   3. Connect rain gauge to Arduino pin 3")
    print("   4. Upload this code to Arduino")
    print("   5. Run Python script to read data")

if __name__ == "__main__":
    print("\n📟 ARDUINO WEATHER STATION")
    print("="*70)
    
    # Show Arduino code first
    arduino_sample_code()
    
    print("\n\n🔌 Attempting to connect to Arduino...")
    
    # Try to connect
    station = ArduinoWeatherStation(port='COM3')  # Change port as needed
    
    if station.connect():
        print("\n✅ Arduino connected! Reading sensors...")
        
        # Read for 1 minute as demo
        for i in range(12):  # 12 readings over 1 minute
            reading = station.read_sensors()
            if reading:
                station.save_reading(reading)
            time.sleep(5)
        
        station.disconnect()
    else:
        print("\n⚠️ Arduino not connected - Demo mode")
        print("   Hardware will be deployed in Kasoa for 30-day calibration")
        print("   This code is ready to use when sensors arrive")