import pandas as pd
import requests
import time

df = pd.read_csv('stations_with_coords.csv')

missing_mask = df['lat'].isna()
missing_count = missing_mask.sum()
print(f"Found {missing_count} stations missing coordinates. Starting Nominatim geocoding...")

headers = {
    'User-Agent': 'FuelOpsAssessment_DataPrep/1.0 (Student Project)'
}

count = 0
for index, row in df[missing_mask].iterrows():
    city = str(row['City']).strip()
    state = str(row['State']).strip()
    
    url = f"https://nominatim.openstreetmap.org/search?city={city}&state={state}&country=USA&format=json"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if len(data) > 0:
            df.at[index, 'lat'] = float(data[0]['lat'])
            df.at[index, 'lng'] = float(data[0]['lon'])
            
    except Exception as e:
        print(f"Failed to geocode {city}, {state}: {e}")
        
    count += 1
    
    if count % 100 == 0:
        print(f"Processed {count}/{missing_count}...")
        df.to_csv('stations_with_coords.csv', index=False)

    time.sleep(1.2)

df.to_csv('stations_with_coords.csv', index=False)
print("Complete! All possible coordinates have been filled and saved to stations_with_coords.csv.")