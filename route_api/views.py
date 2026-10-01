from django.http import JsonResponse
from . import services

def get_route(request):
    start = request.GET.get('start')
    finish = request.GET.get('finish')
    
    if not start or not finish:
        return JsonResponse({
            "error": "Please provide start and finish locations. Example: ?start=Houston, TX&finish=Dallas, TX"
        }, status=400)
        
    
    route_data = services.calculate_trip(start, finish)
    return JsonResponse(route_data)