import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from usuarios.models import Producto, Carrito, ItemCarrito


# 🧪 TEST: Agregar producto al carrito
@pytest.mark.django_db
def test_agregar_producto_al_carrito(client):
    user = User.objects.create_user(username="testuser", password="12345")
    client.login(username="testuser", password="12345")

    # Imagen simulada
    imagen_falsa = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
    producto = Producto.objects.create(nombre="Fit Fórmula", precio=10000, stock=10, imagen=imagen_falsa)

    response = client.post(
        "/carrito/agregar/",
        data={
            "id": producto.id,
            "cantidad": 2,
            "peso": "10kg",
        },
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"

    carrito = Carrito.objects.get(usuario=user)
    item = ItemCarrito.objects.get(carrito=carrito, producto=producto)

    assert item.cantidad == 2
    assert item.producto.nombre == "Fit Fórmula"


# 🧪 TEST: Ver el contenido del carrito
@pytest.mark.django_db
def test_ver_carrito(client):
    user = User.objects.create_user(username="testuser2", password="12345")
    client.login(username="testuser2", password="12345")

    # Imagen simulada
    imagen_falsa = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
    producto = Producto.objects.create(nombre="Bravery Salmon", precio=20000, stock=5, imagen=imagen_falsa)

    carrito = Carrito.objects.create(usuario=user)
    ItemCarrito.objects.create(carrito=carrito, producto=producto, cantidad=1, peso="5kg")

    response = client.get("/carrito/datos/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Bravery Salmon"
    assert data[0]["precio"] == 20000


# 🧪 TEST: Actualizar cantidad (sumar y restar)
@pytest.mark.django_db
def test_actualizar_cantidad(client):
    user = User.objects.create_user(username="testuser3", password="12345")
    client.login(username="testuser3", password="12345")

    imagen_falsa = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
    producto = Producto.objects.create(nombre="Dog Chow", precio=15000, stock=5, imagen=imagen_falsa)

    carrito = Carrito.objects.create(usuario=user)
    item = ItemCarrito.objects.create(carrito=carrito, producto=producto, cantidad=1, peso="5kg")

    # Sumar cantidad
    response = client.post(
        "/carrito/actualizar/",
        data={"id": producto.id, "accion": "sumar"},
        content_type="application/json",
    )
    assert response.status_code == 200
    item.refresh_from_db()
    assert item.cantidad == 2

    # Restar cantidad
    response = client.post(
        "/carrito/actualizar/",
        data={"id": producto.id, "accion": "restar"},
        content_type="application/json",
    )
    assert response.status_code == 200
    item.refresh_from_db()
    assert item.cantidad == 1


# 🧪 TEST: Eliminar producto del carrito
@pytest.mark.django_db
def test_eliminar_item(client):
    user = User.objects.create_user(username="testuser4", password="12345")
    client.login(username="testuser4", password="12345")

    imagen_falsa = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
    producto = Producto.objects.create(nombre="Royal Canin", precio=25000, stock=3, imagen=imagen_falsa)

    carrito = Carrito.objects.create(usuario=user)
    ItemCarrito.objects.create(carrito=carrito, producto=producto, cantidad=1, peso="10kg")

    response = client.post(
        "/carrito/eliminar/",
        data={"id": producto.id},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert not ItemCarrito.objects.filter(carrito=carrito).exists()


# 🧪 TEST: Vaciar todo el carrito
@pytest.mark.django_db
def test_vaciar_carrito(client):
    user = User.objects.create_user(username="testuser5", password="12345")
    client.login(username="testuser5", password="12345")

    imagen_falsa = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
    producto1 = Producto.objects.create(nombre="Bravery Iberian Pork", precio=18000, stock=10, imagen=imagen_falsa)
    producto2 = Producto.objects.create(nombre="Master Dog", precio=12000, stock=10, imagen=imagen_falsa)

    carrito = Carrito.objects.create(usuario=user)
    ItemCarrito.objects.create(carrito=carrito, producto=producto1, cantidad=1, peso="5kg")
    ItemCarrito.objects.create(carrito=carrito, producto=producto2, cantidad=2, peso="10kg")

    response = client.post("/carrito/vaciar/", content_type="application/json")

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert ItemCarrito.objects.filter(carrito=carrito).count() == 0
