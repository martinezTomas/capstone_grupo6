from django.urls import path
from . import views 
from .views import login_view, index, registrar

urlpatterns = [
    #--- Ruta para la página principal ---
    path('', index, name='index'), 
    path('nosotros/', views.nosotros_view, name='nosotros'),
    # --- Rutas para el catálogo de productos ---
    path('catalogo/', views.catalogo_view, name='catalogo'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    # --- Rutas para autenticación usuario ---
    path('login/', login_view, name='login'),
    path('register/', views.registrar, name='register'),
    # --- Rutas para el carrito de compras ---
    path('carrito/', views.carrito_view, name='carrito'),
    path('carrito/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/datos/', views.ver_carrito, name='ver_carrito'),
    path('carrito/eliminar/', views.eliminar_item, name='eliminar_item'),
    path('carrito/actualizar/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('pedido/crear/', views.crear_pedido, name='crear_pedido'),
    path('checkout/', views.checkout, name='checkout'),
    # --- Rutas para MercadoPago ---
    path('mercadopago/pago/', views.pago_mercadopago, name='pago_mercadopago'),
    path('mercadopago/success/', views.mp_success, name='mp_success'),
    path('mercadopago/failure/', views.mp_failure, name='mp_failure'),
    path('mercadopago/pending/', views.mp_pending, name='mp_pending'),
    # --- Ruta para buscar calle ---
    path('buscar-calle/', views.buscar_calle_view, name='buscar_calle_view'),
    # --- Rutas para gestión de productos (admin) ---
    path('gestion/productos/', views.lista_productos_admin, name='lista_productos_admin'),
    path('gestion/productos/crear/', views.crear_producto_admin, name='crear_producto_admin'),
    path('gestion/productos/modificar/<int:pk>/', views.modificar_producto_admin, name='modificar_producto_admin'),
    path('gestion/productos/eliminar/<int:pk>/', views.eliminar_producto_admin, name='eliminar_producto_admin'),
    


]