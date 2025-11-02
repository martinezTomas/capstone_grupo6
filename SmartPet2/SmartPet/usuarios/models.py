from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    # --- Opciones de elección ---
    CATEGORIAS = [
        ('alimento', 'Alimento'),
        ('accesorio', 'Accesorio'),
        ('higiene', 'Higiene'),
        ('salud', 'Salud'),
        ('juguete', 'Juguete'),
        ('ropa', 'Ropa'),
        ('cama', 'Cama'),
    ]

    ESPECIES = [
        ('perro', 'Perro'),
        ('gato', 'Gato'),
        ('pez', 'Pez'),
        ('ave', 'Ave'),
        ('roedor', 'Roedor'),
        ('reptil', 'Reptil'),
        ('otros', 'Otros'),
    ]

    SUBCATEGORIAS = [
        ('alimentos_secos', 'Alimentos Secos'),
        ('alimentos_humedos', 'Alimentos Húmedos'),
        ('antiparasitarios', 'Antiparasitarios'),
        ('camas', 'Camas y Escondites'),
        ('rascadores', 'Rascadores'),
        ('arenas', 'Arenas'),
        ('juguetes', 'Juguetes'),
        ('fuentes', 'Fuentes para Beber'),
        ('collares', 'Collares y Arnés'),
        ('placas', 'Placas Identificadoras'),
        ('higiene', 'Higiene'),
        ('repelentes', 'Limpieza y Repelentes'),
        ('calmantes', 'Productos Calmantes'),
    ]

    # --- Datos principales ---
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/')

    # --- Clasificación del producto ---
    categoria = models.CharField(
        max_length=100,
        choices=CATEGORIAS,
        default='alimento'
    )
    subcategoria = models.CharField(
        max_length=100,
        choices=SUBCATEGORIAS,
        blank=True,
        null=True
    )
    especie = models.CharField(
        max_length=50,
        choices=ESPECIES,
        default='perro'
    )
    marca = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # --- Datos de envío (para Chilexpress) ---
    alto_cm = models.PositiveIntegerField(
        default=10,
        help_text="Altura del paquete en cm"
    )
    ancho_cm = models.PositiveIntegerField(
        default=10,
        help_text="Ancho del paquete en cm"
    )
    largo_cm = models.PositiveIntegerField(
        default=10,
        help_text="Largo del paquete en cm"
    )
    peso_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        help_text="Peso del paquete en kg"
    
    )
    visible = models.BooleanField(
        default=True, 
        help_text="Define si el producto es visible en el catálogo"
        )
    # --- Métodos útiles ---
    def __str__(self):
        """ Devuelve una representación legible del producto. """
        return f"{self.nombre} ({self.get_especie_display()})"

    def dimensiones_str(self):
        """ Retorna una cadena legible con las dimensiones. """
        return f"{self.alto_cm}x{self.ancho_cm}x{self.largo_cm} cm"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
# NOTA IMPORTANTE:
# No es necesario crear un campo 'idproducto'. Django crea un campo 'id'
# numérico y automático para cada modelo, que es la llave primaria.
# Usaremos ese 'id' que Django nos da.

class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    peso = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    # CAMPOS NUEVOS PARA DIRECCIÓN DE ENVÍO
    region = models.CharField(max_length=100, default='')
    comuna = models.CharField(max_length=100, default='')
    calle = models.CharField(max_length=100, default='')
    numero = models.CharField(max_length=20, default='')
    depto_oficina = models.CharField(max_length=100, blank=True, null=True, help_text="Opcional")

    def __str__(self):
        return f"Pedido #{self.id} de {self.usuario.username}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    peso = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
# Create your models here.
