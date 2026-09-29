import pandas as pd
import requests
import time

# Paste your OpenRouteService API key here
API_KEY = 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjM3Y2I1MmFmMjEwZjQ2YmM4ODkxOWUzMzhmMmUxNzI0IiwiaCI6Im11cm11cjY0In0='

print("Loading CSV...")
df = pd.read_csv('fuel-prices-for-be-assessment.csv')

# Add empty columns for the new data
df['Latitude'] = None
df['Longitude'] = None

print(f"Geocoding {len(df)} truck stops. This will take some time due to API rate limits...")

for index, row in df.iterrows():
    # Build the address string
    address = f"{row['Address']}, {row['City']}, {row['State']}"
    url = f"https://api.openrouteservice.org/geocode/search?api_key={API_KEY}&text={address}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('features'):
                coords = data['features'][0]['geometry']['coordinates']
                # OpenRouteService returns [Longitude, Latitude]
                df.at[index, 'Longitude'] = coords[0]
                df.at[index, 'Latitude'] = coords[1]
        
        # Print progress to the terminal so you know it isn't frozen
        if index % 10 == 0:
            print(f"Processed {index} / {len(df)} rows...")
            
        # Free API tiers strictly limit how fast you can ask for data (usually 40 requests per minute).
        # We must pause for 1.5 seconds between each request so the server doesn't block you.
        time.sleep(1.5) 
        
    except Exception as e:
        print(f"Error on row {index}: {e}")

# Save the new enriched CSV
df.to_csv('geocoded_fuel_prices.csv', index=False)
print("Complete! Saved as geocoded_fuel_prices.csv")