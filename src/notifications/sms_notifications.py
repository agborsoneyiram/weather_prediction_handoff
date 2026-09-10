"""
SMS Notification System
Sends weather alerts every 5 hours or when conditions are critical

Requirements:
1. Twilio account (free trial available)
2. Phone number verification
3. Set environment variables: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import os
from datetime import datetime
from twilio.rest import Client

class WeatherSMS:
    """
    SMS Alert System for Weather Predictions
    
    Setup Instructions:
    1. Go to twilio.com/try-twilio
    2. Sign up (free trial)
    3. Get your Account SID, Auth Token, and Twilio phone number
    4. Set environment variables or update this file
    """
    
    def __init__(self):
        # Get Twilio credentials from environment variables
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'your_account_sid_here')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'your_auth_token_here')
        self.twilio_phone = os.getenv('TWILIO_PHONE', '+1234567890')
        
        # Initialize Twilio client
        try:
            self.client = Client(self.account_sid, self.auth_token)
            self.enabled = True
        except Exception as e:
            print(f"⚠️ SMS not configured: {e}")
            print("   Set up Twilio credentials to enable SMS")
            self.enabled = False
    
    def format_weather_message(self, forecast):
        """
        Format prediction into SMS message (160 chars max)
        
        Example:
        ☀️ Kasoa Weather - Tomorrow
        🌡️ 29°C | 💧 75% | 🌧️ 2mm
        Warm, humid, light rain possible
        """
        
        location = forecast['location'].title()
        pred = forecast['predictions']
        
        message = f"☀️ {location} Weather - Tomorrow\n"
        message += f"🌡️ {pred['temp']}°C | 💧 {pred['rhum']}% "
        message += f"{forecast['summary']}"
        
        return message
    
    def format_alert_message(self, forecast, alert_type):
        """
        Format critical weather alert
        
        Alert types:
        - heavy_rain: Rainfall > 20mm
        - extreme_heat: Temperature > 35°C
        - flood_risk: Heavy rain + high humidity
        """
        
        location = forecast['location'].title()
        pred = forecast['predictions']
        
        alerts = {
            'heavy_rain': f"⚠️ HEAVY RAIN ALERT\n{location}: {pred['prcp']}mm expected tomorrow. Flood risk HIGH.",
            'extreme_heat': f"🔥 HEAT ALERT\n{location}: {pred['temp']}°C expected tomorrow. Stay hydrated!",
            'flood_risk': f"🌊 FLOOD RISK\n{location}: Heavy rain ({pred['prcp']}mm) + high humidity. Avoid low areas."
        }
        
        return alerts.get(alert_type, "Weather Alert")
    
    def send_sms(self, to_number, message):
        """
        Send SMS via Twilio
        
        to_number: Phone number with country code (e.g., '+233501234567' for Ghana)
        message: Text message (max 160 chars for single SMS)
        """
        
        if not self.enabled:
            print("⚠️ SMS not enabled - would have sent:")
            print(f"   To: {to_number}")
            print(f"   Message: {message}")
            return False
        
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=to_number
            )
            
            print(f"✅ SMS sent to {to_number}")
            print(f"   Message SID: {message.sid}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send SMS: {e}")
            return False
    
    def send_daily_forecast(self, forecast, recipients):
        """
        Send daily forecast to list of recipients
        
        recipients: List of phone numbers ['233501234567', '+233509876543']
        """
        
        message = self.format_weather_message(forecast)
        
        print(f"\n📱 Sending daily forecast to {len(recipients)} recipients...")
        
        success_count = 0
        for recipient in recipients:
            # Add country code if missing
            if not recipient.startswith('+'):
                recipient = '+233' + recipient  # Ghana country code
            
            if self.send_sms(recipient, message):
                success_count += 1
        
        print(f"✅ Sent to {success_count}/{len(recipients)} recipients")
    
    def check_and_send_alerts(self, forecast, recipients):
        """
        Check if conditions warrant an alert and send if needed
        
        Alert conditions:
        - Heavy rain (>20mm): Flood warning
        - Extreme heat (>35°C): Heat warning
        - Heavy rain + high humidity: Flood risk
        """
        
        pred = forecast['predictions']
        alerts_sent = []
        
        # Check heavy rain
        if pred['prcp'] >= 20:
            message = self.format_alert_message(forecast, 'heavy_rain')
            for recipient in recipients:
                if not recipient.startswith('+'):
                    recipient = '+233' + recipient
                self.send_sms(recipient, message)
            alerts_sent.append('heavy_rain')
        
        # Check extreme heat
        if pred['temp'] >= 35:
            message = self.format_alert_message(forecast, 'extreme_heat')
            for recipient in recipients:
                if not recipient.startswith('+'):
                    recipient = '+233' + recipient
                self.send_sms(recipient, message)
            alerts_sent.append('extreme_heat')
        
        # Check flood risk (heavy rain + high humidity)
        if pred['prcp'] >= 15 and pred['rhum'] >= 85:
            message = self.format_alert_message(forecast, 'flood_risk')
            for recipient in recipients:
                if not recipient.startswith('+'):
                    recipient = '+233' + recipient
                self.send_sms(recipient, message)
            alerts_sent.append('flood_risk')
        
        return alerts_sent

def demo_sms_system():
    """Demo SMS system with sample forecast"""
    
    print("\n" + "="*70)
    print("📱 SMS NOTIFICATION SYSTEM DEMO")
    print("="*70)
    
    # Initialize SMS system
    sms = WeatherSMS()
    
    # Sample forecast
    sample_forecast = {
        'location': 'kasoa',
        'predictions': {
            'temp': 32,
            'rhum': 78,
            'prcp': 5
        },
        'summary': 'Hot, humid, light rain possible'
    }
    
    # Demo recipients (replace with real numbers for testing)
    demo_recipients = [
        '+233501234567',  # Replace with actual number
        '+233509876543'   # Replace with actual number
    ]
    
    print("\n📋 Demo Forecast:")
    print(f"   Location: {sample_forecast['location']}")
    print(f"   Temperature: {sample_forecast['predictions']['temp']}°C")
    print(f"   Humidity: {sample_forecast['predictions']['rhum']}%")
    print(f"   Rainfall: {sample_forecast['predictions']['prcp']}mm")
    
    print("\n📱 Formatted SMS Message:")
    message = sms.format_weather_message(sample_forecast)
    print(message)
    
    print("\n" + "="*70)
    print("⚠️ SMS NOT ACTUALLY SENT (Demo mode)")
    print("="*70)
    
    print("\n💡 To enable SMS:")
    print("   1. Sign up at twilio.com/try-twilio")
    print("   2. Get your Account SID and Auth Token")
    print("   3. Set environment variables:")
    print("      set TWILIO_ACCOUNT_SID=your_sid")
    print("      set TWILIO_AUTH_TOKEN=your_token")
    print("      set TWILIO_PHONE=+1234567890")
    print("   4. Run this script again")

if __name__ == "__main__":
    demo_sms_system()