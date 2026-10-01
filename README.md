FuelOps Routing API

This is a Django REST API that calculates the most cost-effective fuel stops for cross-country truck routes.

Architectural Decisions & Optimizations
To ensure high performance and avoid third-party API rate limits, this application minimizes external network calls.

Zero-API Geocoding: Gas station and city coordinates were pre-processed and mapped locally.

Single External Call: The application makes exactly one external API call per request to OpenRouteService to fetch the route path.

Custom Spatial Math: The app uses a custom Python Haversine algorithm locally to identify the cheapest fuel stops within 50 miles whenever the truck reaches its 450-mile range.

Setup Instructions

Create and activate a virtual environment:
python -m venv venv
Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Start the server:
python manage.py runserver

Testing the API
Make a GET request to the endpoint with a start and finish location:

http://127.0.0.1:8000/api/plan-route/?start=Miami,%20FL&finish=Seattle,%20WA

Expected Output: A JSON payload containing total distance, total fuel cost, and an array of optimal fuel stops.