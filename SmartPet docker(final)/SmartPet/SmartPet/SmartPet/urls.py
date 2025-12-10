"""
URL configuration for SmartPet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# SmartPet/SmartPet/urls.py

from django.contrib import admin
from django.urls import path, include
# No necesitas importar LogoutView aquí si lo manejas en usuarios.urls
# from django.contrib.auth.views import LogoutView 
# No necesitas importar usuarios_views aquí si usas include
# from usuarios import views as usuarios_views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 
    # ✅ ELIMINADA: La línea path('', usuarios_views.index, name='home')
    # ya que 'include' se encargará de la raíz a través de usuarios.urls
    #
    
    # 
    # ✅ MANTENIDA: Esta línea incluye TODAS las URLs de tu app 'usuarios'
    # incluyendo la raíz ('') que definiste dentro de usuarios/urls.py con name='index'.
    path('', include('usuarios.urls')), 
    #
    
    # Ruta para el panel de administración
    path('admin/', admin.site.urls), 
    
    # (Ya no necesitas la línea de logout aquí si la tienes en usuarios.urls)
    # path('logout/', LogoutView.as_view(), name='logout'), 

]

# --- Configuración para servir archivos de medios (imágenes) en DESARROLLO ---
# Esto está correcto para que puedas ver las imágenes de productos mientras desarrollas.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

