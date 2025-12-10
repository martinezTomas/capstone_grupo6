import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from usuarios.models import Producto, Carrito, ItemCarrito


@pytest.mark.django_db
def test_pago_mercadopago_exitoso(client, mocker):
    """Simula una respuesta exitosa desde MercadoPago"""
    # Crear usuario y loguearlo
    user = User.objects.create_user(username="mp_user", password="12345")
    client.login(username="mp_user", password="12345")

    # Crear producto e ítem en carrito
    imagen_falsa = SimpleUploadedFile("test.jpg", b"img", content_type="image/jpeg")
    producto = Producto.objects.create(nombre="Bravery", precio=20000, stock=5, imagen=imagen_falsa)
    carrito = Carrito.objects.create(usuario=user)
    ItemCarrito.objects.create(carrito=carrito, producto=producto, cantidad=1, peso="10kg")

    # Mock de la SDK de MercadoPago
    mock_sdk = mocker.MagicMock()
    mock_sdk.preference.return_value.create.return_value = {
        "response": {"init_point": "https://fake.mercadopago.com/checkout"}
    }

    mocker.patch("usuarios.views.mercadopago.SDK", return_value=mock_sdk)

    # Ejecutar vista
    response = client.get(reverse("pago_mercadopago"))

    # Verificar redirección al checkout de MercadoPago
    assert response.status_code == 302
    assert "https://fake.mercadopago.com/checkout" in response.url


@pytest.mark.django_db
def test_pago_mercadopago_falla(client, mocker):
    """Simula un fallo en la API de MercadoPago"""
    user = User.objects.create_user(username="mp_error", password="12345")
    client.login(username="mp_error", password="12345")

    imagen_falsa = SimpleUploadedFile("test.jpg", b"img", content_type="image/jpeg")
    producto = Producto.objects.create(nombre="Royal Canin", precio=25000, stock=5, imagen=imagen_falsa)
    carrito = Carrito.objects.create(usuario=user)
    ItemCarrito.objects.create(carrito=carrito, producto=producto, cantidad=1, peso="5kg")

    # Simulamos que la API de MercadoPago no devuelve init_point
    mock_sdk = mocker.MagicMock()
    mock_sdk.preference.return_value.create.return_value = {
        "response": {"message": "Error al generar preferencia"}
    }

    mocker.patch("usuarios.views.mercadopago.SDK", return_value=mock_sdk)

    # Ejecutar vista
    response = client.get(reverse("pago_mercadopago"))

    # Verificar que vuelve a la vista checkout (manejo de error)
    assert response.status_code == 302
    assert response.url == reverse("checkout")
