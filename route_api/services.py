import math
import pandas as pd
import requests

def haversine(lon1, lat1, lon2, lat2):
    """Calculates the distance in miles between two coordinate points."""
    lon1, lat1, lon2, lat2 = map(math.radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    a = math.sin((lat2 - lat1)/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1)/2)**2
    return 2 * 3956 * math.asin(math.sqrt(a))

def calculate_trip(start_input, end_input):
    cities_df = pd.read_csv('uscities.csv')
    
    def get_coords(loc_str):
        city, state = [x.strip() for x in loc_str.split(',')]
        match = cities_df[(cities_df['city'].str.lower() == city.lower()) & 
                          (cities_df['state_id'].str.lower() == state.lower())].iloc[0]
        return [float(match['lng']), float(match['lat'])]

    try:
        start_coords = get_coords(start_input)
        end_coords = get_coords(end_input)
    except IndexError:
        return {"error": "City not found. Format must be 'City, State'"}

    api_key = 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjM3Y2I1MmFmMjEwZjQ2YmM4ODkxOWUzMzhmMmUxNzI0IiwiaCI6Im11cm11cjY0In0=' # <--- Ensure your key is inside these quotes!
    headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
    body = {"coordinates": [start_coords, end_coords]}
    
    response = requests.post(
        'https://api.openrouteservice.org/v2/directions/driving-car/geojson', 
        json=body, headers=headers
    )
    
    if response.status_code != 200:
        return {"error": "Routing API failed.", "details": response.json()}
        
    route_data = response.json()
    
    fuel_df = pd.read_csv('stations_with_coords.csv')
    
    lat_col = 'Latitude' if 'Latitude' in fuel_df.columns else 'lat'
    lng_col = 'Longitude' if 'Longitude' in fuel_df.columns else 'lng'
    
    fuel_df = fuel_df.dropna(subset=[lat_col, lng_col])
    
    route_coords = route_data['features'][0]['geometry']['coordinates']
    mpg = 10 
    fuel_stops = []
    total_fuel_cost = 0
    current_distance = 0
    
    for i in range(1, len(route_coords)):
        prev_lon, prev_lat = route_coords[i-1]
        curr_lon, curr_lat = route_coords[i]
        
        segment_dist = haversine(prev_lon, prev_lat, curr_lon, curr_lat)
        current_distance += segment_dist
        
        if current_distance >= 450:
            fuel_df['dist_to_route'] = fuel_df.apply(
                lambda row: haversine(curr_lon, curr_lat, row[lng_col], row[lat_col]), axis=1
            )
            nearby = fuel_df[fuel_df['dist_to_route'] < 50]
            
            if not nearby.empty:
                cheapest = nearby.loc[nearby['Retail Price'].idxmin()]
                gallons_needed = current_distance / mpg
                cost = gallons_needed * cheapest['Retail Price']
                
                fuel_stops.append({
                    "station": cheapest['Truckstop Name'],
                    "city": cheapest['City'],
                    "state": cheapest['State'],
                    "price_per_gallon": cheapest['Retail Price'],
                    "cost_for_segment": round(cost, 2)
                })
                total_fuel_cost += cost
            
            current_distance = 0
            
    if current_distance > 0 and not fuel_df.empty:
        cheapest_overall = fuel_df.loc[fuel_df['Retail Price'].idxmin()]
        total_fuel_cost += (current_distance / mpg) * cheapest_overall['Retail Price']

    total_miles = route_data['features'][0]['properties']['summary']['distance'] / 1609.34

    return {
        "start": start_input,
        "finish": end_input,
        "total_distance_miles": round(total_miles, 2),
        "total_fuel_cost": round(total_fuel_cost, 2),
        "fuel_stops": fuel_stops
    }