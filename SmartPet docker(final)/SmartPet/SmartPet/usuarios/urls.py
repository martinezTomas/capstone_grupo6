# usuarios/urls.py

from django.urls import path
# Importa auth_views para la vista estándar de logout
from django.contrib.auth import views as auth_views
from . import views
# No necesitas la línea de abajo si ya usas views.index, views.login_view etc.
# from .views import login_view, index, registrar

urlpatterns = [
    #--- Páginas principales ---
    path('', views.index, name='index'),
    path('nosotros/', views.nosotros_view, name='nosotros'),

    # --- Catálogo de productos ---
    path('catalogo/', views.catalogo_view, name='catalogo'),
    path('ofertas/', views.catalogo_view, {'solo_ofertas': True}, name='ofertas'),
    #
    path('api/subcategorias/formulario/', views.get_subcategorias, name='api_subcategorias_formulario'),
    #
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),

    # --- Autenticación de usuarios ---
    path('login/', views.login_view, name='login'),
    path('register/', views.registrar, name='register'),
    # AÑADIDO: URL estándar de Django para logout. Redirige al inicio.
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    # --- Recuperación de contraseña ---
    path('reset-password/<str:token>/', views.reset_password_view, name='reset_password'),
    path('api/password-reset/', views.api_password_reset_request, name='api_password_reset_request'),

    # --- perfil de usuario ---
    path('mi-perfil/', views.mi_perfil_ver, name='mi_perfil_ver'), 
    path('mi-perfil/editar/', views.mi_perfil_editar, name='mi_perfil_editar'), 
     # --- Cambiar contraseña ---
    path('cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    # --- (perfil de usuario) Gestión de pedidos ---
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('mis-pedidos/<int:pedido_id>/', views.mi_pedido_detalle, name='mi_pedido_detalle'),
    # --- (perfil de usuario) Gestión de mascotas ---
    path('mi-perfil/mascotas/', views.mis_mascotas, name='mis_mascotas'),
    path('mi-perfil/mascotas/<slug:slug>/', views.mascota_detalle, name='mascota_detalle'),
    path('ajax/cargar-razas/', views.cargar_razas_ajax, name='cargar_razas_ajax'),
    path('mi-perfil/mascotas/<slug:slug>/modificar/', views.mascota_modificar, name='mascota_modificar'),
    path('mi-perfil/mascotas/<slug:slug>/eliminar/', views.mascota_eliminar, name='mascota_eliminar'),

    # --- Carrito de compras (Página y API) ---
    path('carrito/', views.carrito_view, name='carrito'), # Vista de la página del carrito

    # Estandaricé las rutas API bajo /api/carrito/
    path('api/carrito/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),   # API para agregar item
    path('api/carrito/ver/', views.ver_carrito, name='ver_carrito'),           # API para ver contenido (antes /datos/)
    path('api/carrito/eliminar/', views.eliminar_item, name='eliminar_item'),       # API para eliminar item
    path('api/carrito/actualizar/', views.actualizar_cantidad, name='actualizar_cantidad'), # API para actualizar cantidad
    path('api/carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),         # API para vaciar carrito
    path('api/subcategorias/formulario/', views.obtener_subcategorias, name='api_subcategorias_formulario'), # API para obtener subcategorias en la creacion de productos

    # --- Flujo de Pago ---
    path('checkout/', views.checkout, name='checkout'), # Página de checkout (GET)
    path('api/cotizar-checkout/', views.cotizar_checkout_api, name='api_cotizar_checkout'), # API para cotizar en checkout (POST)

    # --- API para obtener comunas (Usada por checkout.html) ---
    path('api/get-comunas/', views.get_comunas, name='get_comunas'),
    path('api/get-regiones/', views.get_regiones_api, name='api_get_regiones'),

    # --- API para simular despacho (Usada en detalle-producto.html) ---
    path('api/simular-despacho/', views.simular_despacho_api, name='api_simular_despacho'),

    # ✅ CORRECCIÓN 1: Esta es la URL a la que apunta el formulario de checkout (POST).
    # Cambié la ruta a '/iniciar-pago/' y, lo más importante,
    # cambié el name='pago_mercadopago' a name='iniciar_pago'.
    # Esto arregla el error NoReverseMatch en checkout.html.
    path('iniciar-pago/', views.pago_mercadopago, name='iniciar_pago'),
    #

    # --- MercadoPago (Callbacks y Webhook) ---
    path('mercadopago/success/', views.mp_success, name='mp_success'), # Redirección si éxito
    path('mercadopago/failure/', views.mp_failure, name='mp_failure'), # Redirección si falla
    path('mercadopago/pending/', views.mp_pending, name='mp_pending'), # Redirección si pendiente
    
    # Recibe notificaciones de backend desde MercadoPago.
    path('mercadopago/webhook/', views.mp_webhook, name='mp_webhook'),
    #

    # --- API Chilexpress ---
    #path('buscar-calle/', views.buscar_calle_view, name='buscar_calle_view'), # Página con formulario
    # Opcional: Si tienes un endpoint API JSON separado para Chilexpress
    #path('api/buscar-calle-json/', views.buscar_calle, name='api_buscar_calle'),
    
    # --- Gestión de productos (Admin) ---
    # Estandarizamos las rutas bajo /gestion/productos/
    path('gestion/productos/', views.lista_productos_admin, name='lista_productos_admin'),
    path('gestion/productos/crear/', views.crear_producto_admin, name='crear_producto_admin'),
    path('gestion/productos/modificar/<int:pk>/', views.modificar_producto_admin, name='modificar_producto_admin'),
    path('gestion/productos/eliminar/<int:pk>/', views.eliminar_producto_admin, name='eliminar_producto_admin'),
    path('gestion/productos/<int:pk>/activar/', views.activar_producto_admin, name='activar_producto_admin'),
    # AJAX agregar marca y especie
    path('api/crear-marca-rapida/', views.crear_marca_ajax, name='crear_marca_ajax'),
    path('api/crear-especie-rapida/', views.crear_especie_ajax, name='crear_especie_ajax'),
    path('api/razas/', views.get_razas_por_especie, name='api_get_razas'),

    # --- Dashboard de administración ---
    path('panel-admin/reportes/ventas/', views.dashboard_admin, name='dashboard_admin'),

    # --- Gestión de usuarios (Admin) ---
    path('gestion/usuarios/', views.gestion_usuarios, name='gestion_usuarios'),
    path('panel-admin/usuarios/editar/<int:pk>/', views.editar_usuario_admin, name='editar_usuario_admin'),

    # --- Gestión de pedidos (Admin) ---
    path('gestion/pedidos/', views.gestion_pedidos, name='gestion_pedidos'),
    path('gestion/pedidos/<int:pedido_id>/', views.pedido_detalle, name='pedido_detalle'),


] 