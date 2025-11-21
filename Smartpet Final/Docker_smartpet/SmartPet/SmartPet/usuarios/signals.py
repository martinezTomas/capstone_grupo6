from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Carrito

@receiver(post_save, sender=User)
def crear_carrito_automatico(sender, instance, created, **kwargs):
    """
    Crea automáticamente un carrito vacío solo si no existe.
    Evita el error UNIQUE constraint failed.
    """
    if created:
        # get_or_create evita duplicados
        Carrito.objects.get_or_create(usuario=instance)
        print(f"🛒 Carrito creado automáticamente para {instance.username}")
