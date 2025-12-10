import pytest
from django.contrib.auth.models import User
from usuarios.models import Producto, Resena

@pytest.mark.django_db
def test_usuario_puede_agregar_resena(client):
    """
    Verifica que un usuario autenticado puede añadir una reseña (feedback)
    a un producto y que esta se guarda correctamente.
    """
    # Crear usuario y loguearlo
    usuario = User.objects.create_user(username="cliente_test", password="12345")
    client.login(username="cliente_test", password="12345")

    # Crear producto de prueba
    producto = Producto.objects.create(
        nombre="Producto Test",
        descripcion="Un producto de prueba",
        precio=1990,
        stock=10,
        visible=True
    )

    # Enviar reseña vía POST
    data = {
    "rating": 5,
    "comentario": "Excelente producto, muy recomendado."
}
    response = client.post(f"/producto/{producto.id}/", data)

    # ✅ 1. La vista debería redirigir o responder correctamente
    assert response.status_code in [200, 302], f"Respuesta inesperada: {response.status_code}"

    # ✅ 2. Se debe haber creado una reseña
    resenas = Resena.objects.filter(producto=producto, usuario=usuario)
    assert resenas.exists(), "No se creó ninguna reseña en la base de datos"

    # ✅ 3. Validar contenido
    resena = resenas.first()
    assert resena.rating == 5
    assert "excelente" in resena.comentario.lower()

    print(f"\n✅ Reseña creada correctamente por '{usuario.username}' para '{producto.nombre}'")
    
