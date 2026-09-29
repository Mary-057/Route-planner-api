from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from .services import get_coordinates, get_route_data, calculate_optimal_fuel_stops


def route_planner(request):
    start_city = request.GET.get('start')
    finish_city = request.GET.get('finish')

    if not start_city or not finish_city:
        return JsonResponse({"error": "Please provide both 'start' and 'finish' cities in the URL."}, status=400)

    start_coords = get_coordinates(start_city)
    finish_coords = get_coordinates(finish_city)

    if not start_coords or not finish_coords:
        return JsonResponse({"error": "Could not find coordinates for one or both cities."}, status=400)

    route_data = get_route_data(start_coords, finish_coords)
    if not route_data:
        return JsonResponse({"error": "Could not calculate a route between these locations."}, status=400)

    # Extract route coordinates from GeoJSON response (Strictly ONE API call!)
    coordinates_path = route_data['features'][0]['geometry']['coordinates']

    # Run our fuel-stop optimization logic (unpacking all 3 values)
    fuel_stops, total_miles, total_fuel_cost = calculate_optimal_fuel_stops(coordinates_path)

    return JsonResponse({
        "start_location": start_city,
        "finish_location": finish_city,
        "total_miles": total_miles,
        "total_fuel_cost_usd": total_fuel_cost,
        "optimal_fuel_stops": fuel_stops,
        "message": "Route and optimal fuel stops calculated successfully with a single API call!"
    }, json_dumps_params={'indent': 4})