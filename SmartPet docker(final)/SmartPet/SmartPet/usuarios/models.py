from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from datetime import date
import uuid

# ==============================================================
# --- MODELOS DE NORMALIZACIÓN ---
# ==============================================================

# --- MODELOS DE NORMALIZACIÓN UBICACIONES ---
    
class Region(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']


class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="comunas")

    id_chilexpress = models.CharField(
        max_length=10, 
        blank=True, 
        null=True, 
        help_text="El código de comuna (CGL) que usa Chilexpress"
    )

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']


# --- MODELOS DE NORMALIZACIÓN PRODUCTOS ---

class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, null=True, blank=True)    
    def __str__(self):
        return self.nombre
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    class Meta:
        ordering = ['nombre']

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, null=True, blank=True)
    class Meta:
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
    def __str__(self):
        return self.nombre
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

class Subcategoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="subcategorias")
    class Meta:
        verbose_name_plural = "Subcategorías"
        unique_together = ('nombre', 'categoria')
        ordering = ['categoria', 'nombre']
    def __str__(self):
        return f"{self.categoria.nombre} -> {self.nombre}"
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
class Especie(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=110, unique=True, null=True, blank=True)
    class Meta:
        verbose_name_plural = "Especies"
        ordering = ['nombre']
    def __str__(self):
        return self.nombre
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

class Raza(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True, null=True, blank=True)
    especie = models.ForeignKey(Especie, on_delete=models.CASCADE, related_name="razas")

    class Meta:
        verbose_name = "Raza"
        verbose_name_plural = "Razas"
        unique_together = ('nombre', 'especie')
        ordering = ['especie', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.especie.nombre})"

    def save(self, *args, **kwargs):
        if not self.slug:
            # Crea un slug único combinando especie y nombre
            self.slug = slugify(f"{self.especie.nombre} {self.nombre}")
        super().save(*args, **kwargs)


# --- MODELOS DE NORMALIZACIÓN MASCOTAS ---

class Edad(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)
    class Meta:
        verbose_name = "Edad"
        verbose_name_plural = "Edades"
        ordering = ['nombre']
    def __str__(self):
        return self.nombre
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Condicion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True ,null=True, blank=True)
    class Meta:
        verbose_name = "Condición"
        verbose_name_plural = "Condiciones"
        ordering = ['nombre']
    def __str__(self):
        return self.nombre
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Raza(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True, null=True, blank=True)
    especie = models.ForeignKey(Especie, on_delete=models.CASCADE, related_name="razas")
    class Meta:
        verbose_name = "Raza"
        verbose_name_plural = "Razas"
        unique_together = ('nombre', 'especie')
        ordering = ['especie', 'nombre']
    def __str__(self):
        return f"{self.nombre} ({self.especie.nombre})"
    def save(self, *args, **kwargs):
        if not self.slug:
            # Crea un slug único combinando especie y nombre
            self.slug = slugify(f"{self.especie.nombre} {self.nombre}")
        super().save(*args, **kwargs)


# ==============================================================
# --- MODELO PRODUCTO ---
# ==============================================================

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, null=True, blank=True)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    precio_anterior = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        null=True, 
        blank=True
    )
    en_oferta = models.BooleanField(default=False)

    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, related_name="productos"
    )
    subcategoria = models.ForeignKey(
        Subcategoria, on_delete=models.SET_NULL, blank=True, null=True, related_name="productos"
    )
    especie = models.ForeignKey(
        Especie, on_delete=models.SET_NULL, null=True, related_name="productos"
    )
    marca = models.ForeignKey(
        Marca, on_delete=models.SET_NULL, blank=True, null=True, related_name="productos"
    )
    edades = models.ManyToManyField(
        Edad, blank=True, related_name="productos"
    )
    condiciones = models.ManyToManyField(
        Condicion, blank=True, related_name="productos"
    )
    razas = models.ManyToManyField(
        Raza, blank=True, related_name="productos", verbose_name="Razas Específicas"
    )

    alto_cm = models.PositiveIntegerField(default=10, help_text="Altura del paquete en cm")
    ancho_cm = models.PositiveIntegerField(default=10, help_text="Ancho del paquete en cm")
    largo_cm = models.PositiveIntegerField(default=10, help_text="Largo del paquete en cm")
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, help_text="Peso del paquete en kg")

    visible = models.BooleanField(default=True, help_text="Define si el producto es visible en el catálogo")

    def __str__(self):
        marca_nombre = self.marca.nombre if self.marca else "Sin Marca"
        return f"{self.nombre} ({marca_nombre})"

    def dimensiones_str(self):
        return f"{self.alto_cm}x{self.ancho_cm}x{self.largo_cm} cm"

    def save(self, *args, **kwargs):
        # Genera el slug si no existe
        if not self.slug:
            self.slug = slugify(self.nombre)

        original_slug = self.slug
        counter = 1
        while Producto.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f'{original_slug}-{counter}'
            counter += 1
        
        is_new = self.pk is None # ¿Es un producto nuevo?

        if not is_new:
            # Si NO es nuevo, trae la versión "vieja" de la base de datos
            try:
                producto_antiguo = Producto.objects.get(pk=self.pk)
                
                # Compara el precio NUEVO (self.precio) con el VIEJO (producto_antiguo.precio)
                if self.precio < producto_antiguo.precio:
                    # ¡EL PRECIO BAJÓ! Es una oferta.
                    self.en_oferta = True
                    self.precio_anterior = producto_antiguo.precio
                
                # Si el precio subió o es igual al anterior
                elif self.precio >= producto_antiguo.precio:
                    # Ya no es oferta, limpiamos los campos
                    self.en_oferta = False
                    self.precio_anterior = None # Borra el precio tachado
                    
            except Producto.DoesNotExist:
                # Esto no debería pasar si is_new es False, pero es una protección
                pass 
        
        # Finalmente, llama al guardado normal
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']


# ==============================================================
# --- MODELO DE RESEÑAS ---
# ==============================================================

class Resena(models.Model):
    # Definimos las opciones para el rating (de 1 a 5 estrellas)
    RATING_CHOICES = (
        (1, '1 - Malo'),
        (2, '2 - Regular'),
        (3, '3 - Bueno'),
        (4, '4 - Muy Bueno'),
        (5, '5 - Excelente'),
    )

    # Enlace al producto que se está reseñando
    # related_name='resenas' nos permitirá hacer producto.resenas.all()
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='resenas')
    
    # Enlace al usuario que escribió la reseña
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resenas')
    
    # El rating de 1-5 estrellas
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=5)
    
    # El texto de la reseña
    comentario = models.TextField(max_length=1000, blank=True, null=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Reseñas"
        ordering = ['-fecha_creacion'] # Las más nuevas primero
        
        # ¡IMPORTANTE! Un usuario solo puede dejar UNA reseña por producto.
        unique_together = ('producto', 'usuario') 

    def __str__(self):
        return f"Reseña de {self.usuario.username} para {self.producto.nombre} ({self.rating} estrellas)"
    

# ==============================================================
# --- MODELO MASCOTA ---
# ==============================================================

class Mascota(models.Model):
    # --- Definición de etapas de vida ---
    ETAPA_CACHORRO_STR = 'Cachorro'
    ETAPA_ADULTO_STR = 'Adulto'
    ETAPA_SENIOR_STR = 'Senior'

    # --- Campos ---
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mascotas')
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la mascota")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de nacimiento")

    # --- Conexiones ---
    especie = models.ForeignKey(Especie, on_delete=models.PROTECT, related_name='mascotas')
    raza = models.ForeignKey(Raza, on_delete=models.SET_NULL, blank=True, null=True, related_name='mascotas')
    condiciones = models.ManyToManyField(Condicion, blank=True, verbose_name="Condiciones Médicas")

    # --- Foto ---
    foto = models.ImageField(
        upload_to='mascotas/',
        blank=True,
        null=True,
        verbose_name="Foto"
    )

    def __str__(self):
        return f"{self.nombre} ({self.usuario.username})"



    # --- Propiedades Mágicas (La clave del filtro) ---
    @property
    def edad_anos(self):
        try:
            hoy = date.today()
            return hoy.year - self.fecha_nacimiento.year - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        except:
            return 0

    @property
    def etapa_vida_str(self):
        """
        Calcula la etapa de vida (String) basado en la edad.
        Este string (ej: "Cachorro") lo usaremos para filtrar
        contra el modelo 'Edad' de tu amigo.
        """
        anos = self.edad_anos
        if anos < 1:
            return self.ETAPA_CACHORRO_STR
        elif anos < 7:
            return self.ETAPA_ADULTO_STR
        else:
            return self.ETAPA_SENIOR_STR

    @property
    def etapa_vida_obj(self):
        """
        Devuelve el objeto 'Edad' correspondiente (Cachorro, Adulto, Senior)
        """
        try:
            return Edad.objects.get(nombre=self.etapa_vida_str)
        except Edad.DoesNotExist:
            print(f"ADVERTENCIA: No existe la 'Edad' llamada '{self.etapa_vida_str}' en la base de datos.")
            return None
        
    def save(self, *args, **kwargs):
        if not self.slug:
            # Crea un slug base con el nombre
            base_slug = slugify(self.nombre)
            # Añade un ID único corto para evitar colisiones
            unique_id = str(uuid.uuid4()).split('-')[0][:5] 
            self.slug = f"{base_slug}-{unique_id}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"
        ordering = ['usuario', 'nombre']


# ==============================================================
# --- MODELOS CARRITO ---
# ==============================================================

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


# ==============================================================
# --- MODELOS PEDIDO ---
# ==============================================================

class Pedido(models.Model):
    
    # --- DEFINICIÓN DE ESTADOS (PEDIDO) ---
    ESTADO_PENDIENTE = 'PENDIENTE'
    ESTADO_APROBADO = 'APROBADO'
    ESTADO_ENVIADO = 'ENVIADO'
    ESTADO_ERROR = 'ERROR_ENVIO'
    
    ESTADO_PEDIDO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente de Pago'),
        (ESTADO_APROBADO, 'Pago Aprobado'),
        (ESTADO_ENVIADO, 'Enviado'),
        (ESTADO_ERROR, 'Error de Envío'),
    ]

    # --- DEFINICIÓN TIPO DE ENVÍO ---
    TIPO_ENVIO_CHOICES = [
        ('ENVIO', 'Despacho a Domicilio'),
        ('RETIRO', 'Retiro en Tienda'),
    ]

    # --- CAMPOS DE PEDIDO ---
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    tipo_envio = models.CharField(
        max_length=20,
        choices=TIPO_ENVIO_CHOICES,
        default='ENVIO', # Por defecto asumimos envío
        verbose_name="Tipo de Entrega"
    )

    nombre_cliente = models.CharField(max_length=100, default='')
    apellido_cliente = models.CharField(max_length=100, default='')
    rut_cliente = models.CharField(max_length=12, default='')
    telefono_cliente = models.CharField(max_length=15, default='')
    email_cliente = models.EmailField(max_length=100, default='')

    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True) # blank=True para Retiro
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True, blank=True) # blank=True para Retiro
    calle = models.CharField(max_length=100, default='', blank=True)
    numero = models.CharField(max_length=20, default='', blank=True)
    depto_oficina = models.CharField(max_length=100, blank=True, null=True, help_text="Opcional")

    id_mercadopago = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="ID Pago MP"
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_PEDIDO_CHOICES,
        default=ESTADO_PENDIENTE,
        verbose_name="Estado del Pedido"
    )

    tracking_number = models.CharField(
        max_length=100, 
        blank=True, null=True, 
        verbose_name="Número de Seguimiento"
    )

    etiqueta_pdf_url = models.URLField(
        max_length=500, 
        blank=True, null=True,
        verbose_name="URL Etiqueta PDF"
    )

    def __str__(self):
        return f"Pedido #{self.id} ({self.get_estado_display()}) - {self.get_tipo_envio_display()}"

    class Meta:
        ordering = ['-fecha_pedido']


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField(default=1)
    peso = models.CharField(max_length=10, blank=True, null=True)
    precio_unitario_congelado = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    def __str__(self):
        nombre_prod = self.producto.nombre if self.producto else "Producto Eliminado"
        return f"{self.cantidad} x {nombre_prod}"

    def get_subtotal(self):
        return self.cantidad * self.precio_unitario_congelado
    

# ==============================================================
# --- SEÑAL AUTOMÁTICA PARA CREAR CARRITO ---
# ==============================================================

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def crear_carrito_automatico(sender, instance, created, **kwargs):
    """
    Crea un carrito vacío automáticamente para cada nuevo usuario.
    Se ejecuta cada vez que se crea un usuario nuevo.
    """
    if created:
        Carrito.objects.create(usuario=instance)
        print(f"🛒 Carrito creado automáticamente para {instance.username}")
