from django.contrib import admin
from .models import Producto, Carrito, ItemCarrito, Pedido, ItemPedido

# Clase para mejorar la vista de Producto en el admin
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio') # Muestra el nombre y precio en columnas
    search_fields = ('nombre',) # Añade una barra de búsqueda por nombre

# Clase para mejorar la vista de Pedido en el admin
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'creado_en', 'completado')
    list_filter = ('completado', 'creado_en') # Añade filtros por estado y fecha

# Registra los modelos usando las clases personalizadas
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Pedido, PedidoAdmin)

# Registra los otros modelos de forma simple
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
admin.site.register(ItemPedido)
