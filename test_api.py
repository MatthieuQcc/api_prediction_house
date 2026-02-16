# test_api.py
import requests

url = "http://localhost:8000/predict"

bien = {
    "lot1_surface_carrez": 75,
    "nombre_pieces_principales": 3,
    "latitude": 43.6047,
    "longitude": 1.4442,
    "has_terrain": 0
}

response = requests.post(url, json=bien)
print(response.json())