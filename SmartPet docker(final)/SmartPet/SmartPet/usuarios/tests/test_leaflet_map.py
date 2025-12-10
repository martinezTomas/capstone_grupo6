 # Este test valida que el HTML tiene las coordenadas reales del marcador.
 # Que el popup del marcador muestra los datos de tu negocio.
 # Que el mapa Leaflet (L.map, L.marker, L.tileLayer) está presente.
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_pagina_muestra_mapa_leaflet(client):
    """
    Verifica que la página principal (o la que contiene el mapa)
    se renderiza correctamente e incluye el contenedor del mapa Leaflet.
    """
    response = client.get(reverse('index'))  # ajusta si el mapa está en otra vista
    assert response.status_code == 200

    html = response.content.decode()

    # El contenedor del mapa y el script de Leaflet deben estar presentes
    assert '<div id="map"' in html
    assert 'https://unpkg.com/leaflet/dist/leaflet.js' in html
    assert 'L.map(' in html or 'L.tileLayer(' in html


@pytest.mark.django_db
def test_mapa_contiene_coordenadas_smartpet(client):
    """
    Comprueba que el mapa renderizado contiene las coordenadas
    del marcador de SmartPetChile en Maipú.
    """
    response = client.get(reverse('index'))
    assert response.status_code == 200

    html = response.content.decode()

    # Buscamos las coordenadas exactas usadas en tu script Leaflet
    assert '-33.52292703075236' in html
    assert '-70.79676786070418' in html

    # Validamos que el marcador tiene el popup esperado
    assert 'SmartPetChile' in html
    assert 'Av. El Conquistador 741' in html
    assert '¡Te esperamos con tu mascota!' in html
