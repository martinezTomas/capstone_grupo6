from django.urls import path
from . import views 
from .views import login_view, index, registrar

urlpatterns = [
    path('', index, name='index'), 
    path('login/', login_view, name='login'),
    path('register/', views.registrar, name='register'),
    path('carrito/', views.carrito_view, name='carrito'),
    path('carrito/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/datos/', views.ver_carrito, name='ver_carrito'),
    path('carrito/eliminar/', views.eliminar_item, name='eliminar_item'),
    path('carrito/actualizar/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('pedido/crear/', views.crear_pedido, name='crear_pedido'),
]