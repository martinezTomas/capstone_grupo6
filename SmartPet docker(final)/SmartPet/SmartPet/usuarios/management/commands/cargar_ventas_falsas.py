import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from usuarios.models import Pedido, ItemPedido, Producto, Region, Comuna # Ajusta imports

class Command(BaseCommand):
    help = 'Carga 50 pedidos falsos para probar el dashboard'

    def handle(self, *args, **kwargs):
        user = User.objects.first() # Usamos el primer usuario (tú)
        productos = list(Producto.objects.all())
        
        if not productos:
            self.stdout.write(self.style.ERROR('¡Crea productos primero!'))
            return

        self.stdout.write("Generando ventas falsas...")

        for i in range(50):
            # 1. Fecha aleatoria (últimos 30 días)
            dias_atras = random.randint(0, 30)
            fecha_falsa = timezone.now() - timedelta(days=dias_atras)

            # 2. Tipo envío aleatorio
            tipo = random.choice(['ENVIO', 'RETIRO'])
            estado = Pedido.ESTADO_APROBADO # Para que salgan en el reporte

            # 3. Crear Pedido
            pedido = Pedido.objects.create(
                usuario=user,
                estado=estado,
                tipo_envio=tipo,
                nombre_cliente=f"Cliente Falso {i}",
                email_cliente="falso@test.com",
                # Hack: Forzamos la fecha de creación (Django auto_now_add la bloquea, pero esto suele funcionar en scripts brutos o editamos directo)
            )
            # Forzar la fecha en la BD
            pedido.fecha_pedido = fecha_falsa
            pedido.save()

            # 4. Añadir Items (1 a 3 productos por pedido)
            total_pedido = 0
            for _ in range(random.randint(1, 3)):
                prod = random.choice(productos)
                cantidad = random.randint(1, 5)
                precio = prod.precio
                
                ItemPedido.objects.create(
                    pedido=pedido,
                    producto=prod,
                    cantidad=cantidad,
                    precio_unitario_congelado=precio
                )
                total_pedido += precio * cantidad

            # Guardar total
            pedido.total = total_pedido
            pedido.save()

        self.stdout.write(self.style.SUCCESS('¡50 Pedidos falsos creados con éxito!'))