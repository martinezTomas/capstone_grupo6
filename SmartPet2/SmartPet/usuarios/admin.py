from django.contrib import admin
from .models import Producto, Carrito, ItemCarrito, Pedido, ItemPedido

# Clase para mejorar la vista de Producto en el admin
class ProductoAdmin(admin.ModelAdmin):
    # Columnas visibles en el listado del admin
    list_display = (
        'nombre',
        'categoria',
        'especie',
        'marca',
        'precio',
        'stock',
        'alto_cm',
        'ancho_cm',
        'largo_cm',
        'peso_kg',
    )

    # Campos que se pueden editar directamente en la lista
    list_editable = (
        'precio',
        'stock',
        'alto_cm',
        'ancho_cm',
        'largo_cm',
        'peso_kg',
    )

    # Campos por los que se puede buscar
    search_fields = ('nombre', 'marca')

    # Filtros laterales en el panel derecho
    list_filter = ('categoria', 'especie', 'marca')

    # Ordenar los productos por nombre (o por lo que prefieras)
    ordering = ('nombre',)
# 1. Creamos un "inline" para los Items del Pedido
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    # Campos que se mostrarán en la tabla de items
    fields = ('producto', 'cantidad', 'peso') 
    # Hacemos que no se puedan editar desde aquí para evitar inconsistencias
    readonly_fields = ('producto', 'cantidad', 'peso') 
    # Evita que se puedan agregar o eliminar items desde esta vista
    extra = 0
    can_delete = False

# Clase para mejorar la vista de Pedido en el admin
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_pedido', 'total', 'completado')
    list_filter = ('completado', 'fecha_pedido') # Añade filtros por estado y fecha
    
    # 2. Añadimos el inline a la vista del Pedido
    inlines = [ItemPedidoInline]

# Registra los modelos usando las clases personalizadas
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Pedido, PedidoAdmin)

# Registra los otros modelos de forma simple
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
# No registramos ItemPedido por sí solo, porque ya lo vemos dentro de Pedido.