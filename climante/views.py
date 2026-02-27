from datetime import datetime
import geocoder
import requests
from django.http import HttpResponse
from django.template import loader
from climante.models import Worldcities
import random


def get_client_ip(request):
    """Obtener la IP real del cliente desde los headers"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def temp_somewhere(request):
    # Intentar obtener de la base de datos
    try:
        random_item = Worldcities.objects.all().order_by('?').first()
        if random_item:
            city = random_item.city
            country = random_item.country
            location = [random_item.lat, random_item.lng]
        else:
            raise Exception("Database is empty")
    except Exception:
        # Ciudades de ejemplo si falla la DB
        ciudades = [
            {'city': 'Bogotá', 'country': 'Colombia', 'lat': 4.7110, 'lng': -74.0721},
            {'city': 'París', 'country': 'Francia', 'lat': 48.8566, 'lng': 2.3522},
            {'city': 'Tokio', 'country': 'Japón', 'lat': 35.6762, 'lng': 139.6503},
            {'city': 'Nueva York', 'country': 'USA', 'lat': 40.7128, 'lng': -74.0060},
            {'city': 'Londres', 'country': 'Reino Unido', 'lat': 51.5074, 'lng': -0.1278},
            {'city': 'Madrid', 'country': 'España', 'lat': 40.4168, 'lng': -3.7038},
            {'city': 'Sídney', 'country': 'Australia', 'lat': -33.8688, 'lng': 151.2093},
            {'city': 'Ciudad de México', 'country': 'México', 'lat': 19.4326, 'lng': -99.1332},
            {'city': 'Berlín', 'country': 'Alemania', 'lat': 52.5200, 'lng': 13.4050},
            {'city': 'Roma', 'country': 'Italia', 'lat': 41.9028, 'lng': 12.4964},
        ]
        ciudad = random.choice(ciudades)
        city = ciudad['city']
        country = ciudad['country']
        location = [ciudad['lat'], ciudad['lng']]
    
    try:
        temp = get_temp(location)
    except Exception:
        temp = "N/A"
    
    template = loader.get_template('index.html')
    context = {'city': city, 'country': country, 'temp': temp}
    return HttpResponse(template.render(context, request))


def temp_here(request):
    try:
        # Obtener IP del cliente
        client_ip = get_client_ip(request)
        
        # Intentar geocodificar la IP
        g = geocoder.ip(client_ip)
        
        if g.ok and g.latlng:
            location = g.latlng
            city = g.city or "Tu ubicación"
            country = g.country or "Desconocido"
        else:
            # Si falla la geocodificación, usar ubicación por defecto
            raise Exception("Geocoding failed")
            
    except Exception:
        # Fallback: usar Bogotá como ubicación por defecto
        location = [4.7110, -74.0721]
        city = "Bogotá"
        country = "Colombia"
    
    try:
        temp = get_temp(location)
    except Exception:
        temp = "N/A"
    
    template = loader.get_template('index.html')
    context = {'city': city, 'country': country, 'temp': temp}
    return HttpResponse(template.render(context, request))


def get_temp(location):
    """Obtener temperatura de una ubicación usando Open-Meteo API"""
    try:
        endpoint = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': location[0],
            'longitude': location[1],
            'current': 'temperature_2m'
        }
        
        response = requests.get(endpoint, params=params, timeout=5)
        response.raise_for_status()
        
        meteo_data = response.json()
        temp = meteo_data['current']['temperature_2m']
        
        return round(temp, 1)
    except Exception as e:
        # Si falla la API, retornar N/A
        return "N/A"
