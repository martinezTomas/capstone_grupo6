import pytest
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse

@pytest.mark.django_db
def test_api_envia_correo_recuperacion_password(client):
    """
    Verifica que la API personalizada de restablecimiento de contraseña
    envía correctamente un correo electrónico.
    """
    # Crear usuario de prueba
    usuario = User.objects.create_user(
        username="cliente_test",
        email="cliente_test@example.com",
        password="12345"
    )

    # Llamar a la API (usamos la ruta real)
    url = reverse('api_password_reset_request')  # asegúrate que tu urls.py tenga este name
    response = client.post(url, data={'email': usuario.email}, content_type='application/json')

    # Verificar respuesta
    assert response.status_code == 200, f"Respuesta inesperada: {response.status_code}"
    data = response.json()
    assert data['success'] is True, "La API no respondió correctamente"

    # Verificar que se haya enviado un correo
    assert len(mail.outbox) == 1, "No se envió ningún correo de restablecimiento"

    correo = mail.outbox[0]
    assert usuario.email in correo.to
    assert "restablece" in correo.subject.lower()
    assert "http" in correo.body

    print("\n✅ API de restablecimiento envió correctamente el correo a:", usuario.email)
