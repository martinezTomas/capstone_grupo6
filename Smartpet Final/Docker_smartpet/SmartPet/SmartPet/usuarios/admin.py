from django.contrib import admin
from .models import (
    Region, Comuna, Marca, Categoria, Subcategoria, Especie, 
    Edad, Condicion, Raza, Producto, Resena, Carrito, 
    ItemCarrito, Pedido, ItemPedido, Mascota
)

# ==============================================================
# --- ADMINS DE CATÁLOGO (CON SLUGS AUTOMÁTICOS) ---
# ==============================================================

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ['nombre']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ['nombre']

@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}
    list_display = ('nombre', 'categoria')
    list_filter = ('categoria',)
    search_fields = ('nombre',)

@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ['nombre']

# ==============================================================
# --- ADMINS DE FILTROS (LOS NUEVOS) ---
# ==============================================================

@admin.register(Edad)
class EdadAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Condicion)
class CondicionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Raza)
class RazaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}
    list_display = ('nombre', 'especie')
    list_filter = ('especie',)
    search_fields = ('nombre',)

# ==============================================================
# --- ADMIN DE PRODUCTO (CON FILTROS MEJORADOS) ---
# ==============================================================

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'marca', 'especie', 'precio', 'stock', 'visible')
    list_filter = ('especie', 'marca', 'categoria', 'en_oferta', 'visible')
    search_fields = ('nombre', 'marca__nombre')
    prepopulated_fields = {'slug': ('nombre',)}
    
    # ¡Esto hace que los ManyToMany se vean mil veces mejor!
    filter_horizontal = ('edades', 'condiciones', 'razas')
    
    # (Tu 'list_editable' es genial si lo usas mucho, puedes añadirlo de nuevo)
    # list_editable = ('precio', 'stock')

# ==============================================================
# --- ADMIN DE MASCOTA (EL NUEVO) ---
# ==============================================================

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'especie', 'raza', 'get_etapa_vida')
    list_filter = ('especie', 'raza')
    search_fields = ('nombre', 'usuario__username')
    
    # Mejora para el ManyToMany de condiciones
    filter_horizontal = ('condiciones',)
    
    # (Función para mostrar la edad calculada en la columna)
    @admin.display(description='Etapa de Vida')
    def get_etapa_vida(self, obj):
        return obj.etapa_vida_str

# ==============================================================
# --- ADMINS DE PEDIDOS (CON TU 'INLINE' MEJORADO) ---
# ==============================================================

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    fields = ('producto', 'cantidad', 'precio_unitario_congelado', 'get_subtotal') 
    readonly_fields = ('producto', 'cantidad', 'precio_unitario_congelado', 'get_subtotal')
    extra = 0
    can_delete = False

    # (Función para mostrar el subtotal de la línea)
    @admin.display(description='Subtotal')
    def get_subtotal(self, obj):
        return obj.get_subtotal()

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'fecha_pedido', 'total', 'estado')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('id', 'nombre_cliente', 'email_cliente')
    
    # --- ✅ ¡TU CÓDIGO FUE AÑADIDO AQUÍ! ---
    inlines = [ItemPedidoInline]
    
    # (Hacemos que los campos de cliente se oculten para limpiar la vista)
    fieldsets = (
        ('Info General', {
            'fields': ('id', 'fecha_pedido', 'usuario', 'total', 'estado')
        }),
        ('Datos de Envío', {
            'classes': ('collapse',), # (Empieza colapsado)
            'fields': ('nombre_cliente', 'apellido_cliente', 'rut_cliente', 'telefono_cliente', 'email_cliente', 
                       'region', 'comuna', 'calle', 'numero', 'depto_oficina')
        }),
        ('Datos de Pago y Logística', {
            'classes': ('collapse',),
            'fields': ('id_mercadopago', 'tracking_number', 'etiqueta_pdf_url')
        }),
    )
    # (Hacemos que los campos de Info General sean de solo lectura)
    readonly_fields = ('id', 'fecha_pedido', 'usuario', 'total')

# ==============================================================
# --- OTROS REGISTROS ---
# ==============================================================

# (Registros simples para el resto)
admin.site.register(ItemPedido)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
admin.site.register(Resena)
admin.site.register(Region)
admin.site.register(Comuna)