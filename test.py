import requests
import csv
from datetime import datetime

# Accra Coordinates (You can loop these for all 16 regions later)
lat, lon = 5.6037, -0.1870

# Automatically get today's date in NASA format (YYYYMMDD)
end_date = datetime.now().strftime('%Y%m%d')
start_date = "20260101"  # You can change this to 20200101 for your full history

def fetch_weather(temporal_gap):
    url = f"https://power.larc.nasa.gov/api/temporal/{temporal_gap}/point?parameters=T2M,RH2M,PRECTOTCORR&community=AG&longitude={lon}&latitude={lat}&start={start_date}&end={end_date}&format=JSON"
    
    print(f"Fetching {temporal_gap} data up to {datetime.now().strftime('%Y/%m/%d %H:%M')}...")
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        params = data['properties']['parameter']
        filename = f'ghana_{temporal_gap}_data.csv'
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            # Header
            header = ['Date', 'Temperature_C', 'Humidity_Percent', 'Rain_mm']
            if temporal_gap == 'hourly':
                header.insert(1, 'Hour')
            writer.writerow(header)
            
            # Use T2M keys to loop through all timestamps
            for timestamp, temp in params['T2M'].items():
                # Reformat date from YYYYMMDD to YYYY/MM/DD
                raw_date = timestamp[:8]
                formatted_date = f"{raw_date[:4]}/{raw_date[4:6]}/{raw_date[6:]}"
                
                humidity = params['RH2M'][timestamp]
                rain = params['PRECTOTCORR'][timestamp]
                
                row = [formatted_date, temp, humidity, rain]
                if temporal_gap == 'hourly':
                    hour = timestamp[8:]
                    row.insert(1, hour)
                
                writer.writerow(row)
        print(f"Done! Created {filename}")
    else:
        print(f"Failed to fetch {temporal_gap} data. Error: {response.status_code}")

# Run for both
fetch_weather('hourly')
fetch_weather('daily')