import os
import math
import pandas as pd
import requests
from django.conf import settings

# Load the CSV once when the server starts up
CSV_PATH = os.path.join(settings.BASE_DIR, 'fuel-prices-for-be-assessment.csv')
fuel_df = pd.read_csv(CSV_PATH)

# Clean up column names just in case of spaces
fuel_df.columns = fuel_df.columns.str.strip()

def get_coordinates(city_name):
    """Calls OpenRouteService Geocoder to turn a city name into [longitude, latitude]."""
    url = f"https://api.openrouteservice.org/geocode/search?api_key={settings.ORS_API_KEY}&text={city_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('features'):
            return data['features'][0]['geometry']['coordinates']
    return None

def get_route_data(start_coords, finish_coords):
    """Calls OpenRouteService Directions API ONCE with the geojson endpoint."""
    url = f"https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {
        'Authorization': settings.ORS_API_KEY,
        'Content-Type': 'application/json'
    }
    body = {
        "coordinates": [start_coords, finish_coords]
    }
    response = requests.post(url, json=body, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_distance_miles(lon1, lat1, lon2, lat2):
    """Calculates straight-line distance in miles between two GPS points using Haversine formula."""
    R = 3958.8 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def calculate_optimal_fuel_stops(route_coords):
    """
    Tracks the truck along route coordinates. Every ~400 miles, 
    finds a low-cost fuel stop and calculates total fuel costs at 10 MPG.
    """
    target_stop_distance = 400  # Refuel safety threshold
    mpg = 10.0                  # Vehicle efficiency requirement
    
    stops_made = []
    current_tank_miles = 0
    accumulated_distance = 0
    total_fuel_cost = 0.0
    
    sorted_fuel = fuel_df.sort_values(by='Retail Price').reset_index(drop=True)
    stop_picker_index = 0

    last_stop_distance = 0

    for i in range(1, len(route_coords)):
        p1 = route_coords[i-1]
        p2 = route_coords[i]
        segment_miles = get_distance_miles(p1[0], p1[1], p2[0], p2[1])
        
        accumulated_distance += segment_miles
        current_tank_miles += segment_miles
        
        if current_tank_miles >= target_stop_distance:
            best_stop = sorted_fuel.iloc[stop_picker_index % len(sorted_fuel)].to_dict()
            
            # Explicitly target the truck stop name column while bypassing ID columns
            stop_name_key = next((col for col in best_stop.keys() if col.lower() == 'truckstop' or ('truck' in col.lower() and 'id' not in col.lower())), 'Truckstop')
            
            # Calculate leg distance and cost for this tank portion
            leg_distance = accumulated_distance - last_stop_distance
            gallons_used = leg_distance / mpg
            price_per_gallon = float(best_stop.get('Retail Price'))
            leg_cost = gallons_used * price_per_gallon
            total_fuel_cost += leg_cost

            stops_made.append({
                "location": f"{best_stop.get('City')}, {best_stop.get('State')}",
                "stop_at_mile": round(accumulated_distance, 2),
                "fuel_price": price_per_gallon,
                "truckstop": best_stop.get(stop_name_key) or "Unknown Truckstop",
                "leg_cost": round(leg_cost, 2)
            })
            
            last_stop_distance = accumulated_distance
            stop_picker_index += 1
            current_tank_miles = 0  # Reset tank after refueling

    # Handle final leg to destination if any miles remain after the last stop
    if accumulated_distance > last_stop_distance:
        final_leg_distance = accumulated_distance - last_stop_distance
        final_gallons = final_leg_distance / mpg
        # Use a standard cheap price or the last stop's price for the remaining miles
        final_price = float(sorted_fuel.iloc[stop_picker_index % len(sorted_fuel)].get('Retail Price'))
        final_cost = final_gallons * final_price
        total_fuel_cost += final_cost

    return stops_made, round(accumulated_distance, 2), round(total_fuel_cost, 2)