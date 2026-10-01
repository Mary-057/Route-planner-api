# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
import json

class RoutePlannerAPITests(TestCase):
    def setUp(self):
        self.client = Client()
       
        self.url = reverse('route_endpoint') 

    def test_route_generation_success(self):
        payload = {
            "start": "Lagos",
            "destination": "Abuja"
        }
        
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)