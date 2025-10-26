# --- Python Standard Library ---
import json                     # Para trabajar con datos en formato JSON (usado en APIs de carrito y webhooks)
import requests                 # Para hacer llamadas a APIs externas (Chilexpress)

# --- Django Core ---
from django.conf import settings                # Para acceder a variables de configuración (claves de API, etc.)
from django.db import transaction               # Para asegurar que múltiples operaciones de BD se completen juntas (ej. al crear pedido)
from django.db.models import Sum, Case, When    # Para cálculos y ordenamiento avanzado en la base de datos (ej. "más vendidos")
from django.http import JsonResponse, HttpResponseBadRequest # Para devolver respuestas en formato JSON (APIs carrito) y errores HTTP
from django.shortcuts import render, redirect, get_object_or_404 # Funciones comunes para manejar vistas, redirecciones y buscar objetos
from django.urls import reverse                   # Para generar URLs dinámicamente a partir de sus nombres
from django.views.decorators.csrf import csrf_exempt # Para deshabilitar la protección CSRF en vistas específicas (necesario para webhooks de MP)

# --- Django Contrib ---
from django.contrib import messages             # Para mostrar mensajes temporales al usuario (éxito, error, info)
from django.contrib.admin.views.decorators import staff_member_required # Decorador para restringir vistas solo a administradores
from django.contrib.auth import authenticate, login as auth_login # Funciones para manejar la autenticación de usuarios (login)
from django.contrib.auth.decorators import login_required # Decorador para restringir vistas solo a usuarios logueados
from django.contrib.auth.forms import AuthenticationForm # Formulario predefinido de Django para el login
from django.contrib.auth.models import User     # Modelo de usuario predefinido de Django

# --- Third-Party Libraries ---
import mercadopago              # SDK oficial de Mercado Pago para interactuar con su API

# --- Local Application Imports (Tu proyecto) ---
from .forms import RegistroUserForm, ProductoForm # Formularios personalizados definidos en forms.py
from .models import Producto, Carrito, ItemCarrito, Pedido, ItemPedido # Modelos de tu base de datos definidos en models.py



# --- Página principal ---
def index(request):
    # --- Lógica para "Más Vendidos" ---
    
    # 1. Obtenemos los items de pedidos que SÍ han sido completados
    items_vendidos = ItemPedido.objects.filter(pedido__completado=True)
    
    # 2. Agrupamos por producto, sumamos la cantidad de cada uno,
    #    ordenamos del más vendido al menos vendido, y tomamos los 3 primeros.
    top_items = items_vendidos.values('producto_id').annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:3]

    # 3. Obtenemos la lista de IDs de esos 3 productos
    top_producto_ids = [item['producto_id'] for item in top_items]

    # --- Lógica de Fallback (si no hay ventas) ---
    
    if top_producto_ids:
        # 4. Si hay ventas, buscamos esos productos y los ordenamos
        #    en el mismo orden en que los encontramos (del más al menos vendido)
        
        # Creamos una lista de "When" para ordenar por la lista de IDs
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(top_producto_ids)])
        
        # Filtramos los productos y los ordenamos
        productos_para_mostrar = Producto.objects.filter(pk__in=top_producto_ids).order_by(preserved_order)
    
    else:
        # 5. Si no hay ventas (ej. tienda nueva), mostramos 3 productos 
        #    cualquiera para que la página no se vea vacía (ej. los últimos agregados)
        productos_para_mostrar = Producto.objects.all().order_by('-id')[:3]

    
    # 6. Enviamos solo esa lista de 3 productos a la plantilla
    context = {
        'productos': productos_para_mostrar
    }
    
    return render(request, 'pages/index.html', context)

# --- Página nosotros ---
def nosotros_view(request):
    return render(request, "pages/nosotros.html")

# --- Página catálogo ---
def catalogo_view(request):
    productos = Producto.objects.all()

    # Leer los parámetros GET del formulario
    categoria = request.GET.get('categoria')
    subcategoria = request.GET.get('subcategoria')
    especie = request.GET.get('especie')
    marca = request.GET.get('marca')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')

    # Aplicar los filtros si existen
    if categoria:
        productos = productos.filter(categoria=categoria)
    if subcategoria:
        productos = productos.filter(subcategoria=subcategoria)
    if especie:
        productos = productos.filter(especie=especie)
    if marca and marca.strip():
        productos = productos.filter(marca__icontains=marca)
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    context = {
        'productos': productos,
        'categoria_actual': categoria,
        'subcategoria_actual': subcategoria,
        'especie_actual': especie,
        'marca_actual': marca,
        'precio_min': precio_min,
        'precio_max': precio_max,
    }

    return render(request, 'pages/catalogo.html', context)

# --- VISTAS PARA GESTIÓN DE PRODUCTOS (ADMIN) ---

@staff_member_required # Solo admins
def lista_productos_admin(request):
    """ Muestra la lista de todos los productos para administrar. """
    productos = Producto.objects.all().order_by('nombre') # Ordenados alfabéticamente
    context = {'productos': productos}
    return render(request, 'paneladmin/lista_productos_admin.html', context)

@staff_member_required
def crear_producto_admin(request):
    """ Muestra el formulario para crear un nuevo producto y lo procesa. """
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Producto creado exitosamente.')
            return redirect('lista_productos_admin') # Vuelve a la lista
        else:
            messages.error(request, '❌ Hubo errores en el formulario.')
    else:
        form = ProductoForm()

    context = {'form': form, 'titulo': 'Crear Nuevo Producto'} # Añadimos título
    return render(request, 'paneladmin/crear_producto_admin.html', context)

@staff_member_required
def modificar_producto_admin(request, pk):
    """ Muestra el formulario para editar un producto existente y lo procesa. """
    producto = get_object_or_404(Producto, pk=pk) # Busca el producto por su ID (pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto) # Carga datos existentes
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Producto "{producto.nombre}" actualizado.')
            return redirect('lista_productos_admin')
        else:
            messages.error(request, '❌ Hubo errores al actualizar.')
    else:
        form = ProductoForm(instance=producto) # Muestra el form con datos actuales

    context = {'form': form, 'titulo': f'Modificar Producto: {producto.nombre}', 'producto': producto}
    return render(request, 'paneladmin/modificar_producto_admin.html', context)

@staff_member_required
def eliminar_producto_admin(request, pk):
    """ Muestra confirmación y elimina un producto. """
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre_producto = producto.nombre # Guarda el nombre antes de borrar
        producto.delete()
        messages.success(request, f'🗑️ Producto "{nombre_producto}" eliminado.')
        return redirect('lista_productos_admin')

    context = {'producto': producto}
    return render(request, 'paneladmin/confirmar_eliminar_admin.html', context)

# --- TERMINo VISTAS PARA GESTIÓN DE PRODUCTOS (ADMIN) ---

# --- Login ---
def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if user is not None:
            auth_login(request, user)
            return redirect('index')
    return render(request, 'registration/login.html', {'form': form})


# --- Registro de usuario ---
def registrar(request):
    form = RegistroUserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        usuario = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
        )
        if usuario is not None:
            auth_login(request, usuario)
            return redirect('index')
    return render(request, 'registration/register.html', {'form': form})


# --- Carrito ---
def carrito_view(request):
    return render(request, 'pages/carrito.html')


@login_required
def agregar_al_carrito(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            producto_id = data.get('id')
            cantidad = int(data.get('cantidad', 1))
            peso = data.get('peso')

            producto = get_object_or_404(Producto, id=producto_id)
            carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

            item, created = ItemCarrito.objects.get_or_create(
                carrito=carrito,
                producto=producto,
                peso=peso,
                defaults={'cantidad': cantidad}
            )

            if not created:
                item.cantidad += cantidad
                item.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)


@login_required
def ver_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    data = [
        {
            'id': str(item.producto.id),
            'nombre': item.producto.nombre,
            'precio': int(item.producto.precio),
            'imagen': item.producto.imagen.url,
            'cantidad': item.cantidad,
            'peso': item.peso,
        } for item in items
    ]
    return JsonResponse(data, safe=False)


@login_required
def eliminar_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        producto_id = data.get('id')
        ItemCarrito.objects.filter(carrito__usuario=request.user, producto_id=producto_id).delete()
        return JsonResponse({'status': 'success'})


@login_required
def actualizar_cantidad(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        producto_id = data.get('id')
        accion = data.get('accion')
        item = get_object_or_404(ItemCarrito, carrito__usuario=request.user, producto_id=producto_id)
        if accion == 'sumar':
            item.cantidad += 1
        elif accion == 'restar' and item.cantidad > 1:
            item.cantidad -= 1
        item.save()
        return JsonResponse({'status': 'success'})


@login_required
def vaciar_carrito(request):
    if request.method == 'POST':
        Carrito.objects.get(usuario=request.user).items.all().delete()
        return JsonResponse({'status': 'success'})


# --- Crear Pedido ---
# (Esta vista ahora es redundante, ya que la lógica se movió a 'pago_mercadopago',
# pero se mantiene "sin borrar" como pediste. Probablemente ya no la uses.)
@login_required
@transaction.atomic
def crear_pedido(request):
    if request.method == 'POST':
        carrito = get_object_or_404(Carrito, usuario=request.user)
        items_carrito = carrito.items.all()

        if not items_carrito:
            messages.error(request, 'Tu carrito está vacío.')
            return redirect('carrito')

        # Verificación de Stock
        for item_c in items_carrito:
            if item_c.producto.stock < item_c.cantidad:
                messages.error(request, f"No hay stock para '{item_c.producto.nombre}'.")
                return redirect('carrito')

        # 1. Creamos el pedido pero como "pendiente" (completado=False)
        pedido = Pedido.objects.create(usuario=request.user, completado=False)
        
        # 2. Bucle para crear los items del pedido y calcular el total
        total_pedido = 0
        for item_c in items_carrito:
            ItemPedido.objects.create(
                pedido=pedido,
                producto=item_c.producto,
                cantidad=item_c.cantidad,
                peso=item_c.peso
            )
            # Sumamos al total
            total_pedido += item_c.producto.precio * item_c.cantidad
        
        # 3. Guardamos el total calculado en el pedido
        pedido.total = total_pedido
        pedido.save()

        # 4. Redirigimos al inicio del flujo de pago
        # (Aquí puedes poner 'iniciar_pago' de Transbank o el de Mercado Pago)
        
        # 🔔 NOTA: Esta vista redirige a 'iniciar_pago'. Si tu URL de 'pago_mercadopago'
        # se llama 'iniciar_pago' en urls.py, esto funcionará.
        return redirect('iniciar_pago', pedido_id=pedido.id) 
        
    return redirect('index')


# --- Checkout ---
@login_required
def checkout(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    total = sum(item.producto.precio * item.cantidad for item in items)
    return render(request, 'pages/checkout.html', {'items': items, 'total': total})


@login_required
@transaction.atomic # ✅ Añadido para asegurar que el pedido se cree correctamente
def pago_mercadopago(request):
    
    # ✅ LÓGICA DE CREACIÓN DE PEDIDO (MOVIDA AQUÍ)
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items_carrito = carrito.items.all()

    if not items_carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("carrito")

    # 1. Verificación de Stock
    for item_c in items_carrito:
        if item_c.producto.stock < item_c.cantidad:
            messages.error(request, f"No hay stock para '{item_c.producto.nombre}'.")
            return redirect('carrito')

    # 2. Creamos el pedido pero como "pendiente" (completado=False)
    pedido = Pedido.objects.create(usuario=request.user, completado=False)
    
    total_pedido = 0
    items_para_mp = [] # Lista para los items de Mercado Pago

    for item_c in items_carrito:
        # 3. Creamos los Items del Pedido
        ItemPedido.objects.create(
            pedido=pedido,
            producto=item_c.producto,
            cantidad=item_c.cantidad,
            peso=item_c.peso
        )
        # 4. Sumamos al total
        total_pedido += item_c.producto.precio * item_c.cantidad
        
        # 5. Añadimos el item a la lista para MP
        items_para_mp.append({
            "title": item_c.producto.nombre,
            "quantity": int(item_c.cantidad),
            "unit_price": float(item_c.producto.precio),
            "currency_id": "CLP",
        })
    
    # 6. Guardamos el total calculado en el pedido
    pedido.total = total_pedido
    pedido.save()

    # --- FIN LÓGICA DE PEDIDO ---

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    # ✅ ¡URL CORREGIDA! Esta es la URL de tu Ngrok activo (image_9e0ce5.png)
    base_url = "https://rectangular-luanna-overliterarily.ngrok-free.dev"

    # Crear la preferencia de pago
    preference_data = {
        "items": items_para_mp, # ✅ Usamos la lista de items creada
        "back_urls": {
            "success": f"{base_url}/mercadopago/success/", # MP añadirá ?external_reference=...
            "failure": f"{base_url}/mercadopago/failure/",
            "pending": f"{base_url}/mercadopago/pending/",
        },
        "auto_return": "approved",
        "binary_mode": True,
        
        # ✅ ¡IMPORTANTE! Enviamos el ID de nuestro Pedido a Mercado Pago
        "external_reference": str(pedido.id),
        
        # ✅ ¡IMPORTANTE! URL para notificaciones (Webhooks)
        "notification_url": f"{base_url}/mercadopago/webhook/"
    }

    preference_response = sdk.preference().create(preference_data)
    print("⚙️ MERCADOPAGO RESPONSE:", preference_response)  # 👀 para depurar

    preference = preference_response.get("response", {})

    # Verificar si MercadoPago devuelve init_point (link de pago)
    if "init_point" in preference:
        return redirect(preference["init_point"])
    else:
        error_msg = preference.get("message", "No se pudo generar el enlace de pago.")
        messages.error(request, f"Error MercadoPago: {error_msg}")
        return redirect("checkout")

# --- Rutas de retorno de MercadoPago ---

@login_required
@transaction.atomic # ✅ Añadido para procesar el pedido de forma segura
def mp_success(request):
    
    # ✅ OBTENEMOS LOS DATOS DE LA URL
    pedido_id = request.GET.get('external_reference')
    payment_id = request.GET.get('payment_id') # Opcional: para guardar registro
    
    if not pedido_id:
        messages.error(request, "Error: No se encontró referencia del pedido.")
        return redirect("index")

    try:
        # 2. Buscamos el pedido
        pedido = Pedido.objects.get(id=pedido_id, usuario=request.user)
    except Pedido.DoesNotExist:
        messages.error(request, "Error: Pedido no válido.")
        return redirect("index")

    # 3. Verificamos si ya fue procesado (ej. por el webhook)
    if pedido.completado:
        messages.info(request, f"Tu compra (Pedido #{pedido.id}) ya había sido procesada.")
        return render(request, "pages/mercadopago_success.html", {"pedido": pedido})

    # --- ✅ LÓGICA DE NEGOCIO FALTANTE ---

    # 4. Marcamos el pedido como completado
    pedido.completado = True
    # pedido.id_pago_mp = payment_id # Opcional: guardar el ID de pago en tu modelo Pedido
    pedido.save()

    # 5. Descontamos el stock
    items_pedido = pedido.items.all()
    for item in items_pedido:
        producto = item.producto
        if producto.stock >= item.cantidad:
            producto.stock -= item.cantidad
            producto.save()
        else:
            # Manejar caso de sobreventa (aunque ya validamos antes)
            messages.warning(request, f"Stock de {producto.nombre} inconsistente.")

    # 6. Vaciamos el carrito de compras
    try:
        carrito = Carrito.objects.get(usuario=request.user)
        carrito.items.all().delete()
    except Carrito.DoesNotExist:
        pass # El carrito ya estaba vacío o no existe, no hay problema

    messages.success(request, f"✅ ¡Pago realizado con éxito! Tu Pedido es el #{pedido.id}.")
    # Enviamos el pedido a la plantilla por si quieres mostrar el ID
    return render(request, "pages/mercadopago_success.html", {"pedido": pedido})


@login_required
def mp_failure(request):
    # 🔔 NOTA: El pedido se creó pero quedó como "completado=False" (pendiente).
    # Podrías implementar lógica para que el usuario reintente el pago de ese pedido.
    pedido_id = request.GET.get('external_reference')
    messages.error(request, f"❌ El pago fue rechazado o falló (Pedido #{pedido_id}).")
    return render(request, "pages/mercadopago_failure.html")


@login_required
def mp_pending(request):
    # 🔔 NOTA: El pedido se creó pero quedó como "completado=False" (pendiente).
    pedido_id = request.GET.get('external_reference')
    messages.info(request, f"⏳ El pago está pendiente de aprobación (Pedido #{pedido_id}).")
    return render(request, "pages/mercadopago_pending.html")


# 🔔 VISTA DE WEBHOOK (MUY RECOMENDADA)
# Esta vista recibe notificaciones de Mercado Pago "por detrás"
# y es la forma más segura de confirmar un pago, ya que 'mp_success'
# puede fallar si el usuario cierra la pestaña.
@csrf_exempt # MP no envía token CSRF
def mp_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if data.get("type") == "payment":
                payment_id = data.get("data", {}).get("id")
                
                print(f"🔔 WEBHOOK RECIBIDO: Tipo 'payment', ID: {payment_id}")
                
                # --- Lógica de Webhook ---
                # Aquí deberías usar el SDK de MP para obtener el pago:
                # sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
                # payment_info = sdk.payment().get(payment_id)
                # payment = payment_info.get("response", {})
                
                # pedido_id = payment.get("external_reference")
                # if payment.get("status") == "approved":
                #    (Aquí iría la misma lógica de 'mp_success':
                #     buscar pedido por ID, marcar completado, descontar stock)
                #    (Esto asegura que el pedido se procese incluso si el
                #     usuario cierra el navegador)
                
        except Exception as e:
            print(f"❌ ERROR WEBHOOK: {e}")
            return JsonResponse({"status": "error"}, status=400)

    # Avisar a MercadoPago que recibimos la notificación
    return JsonResponse({"status": "received"}, status=200)


# --- Vistas de Chilexpress (sin cambios) ---
def buscar_calle(request):
    """
    Consulta la API de Chilexpress (GeoReference) para buscar calles según comuna y nombre.
    """
    url = f"{settings.CHILEXPRESS_BASE_URL}/georeference/api/v1.0/streets/search"
    headers = {
        "Ocp-Apim-Subscription-Key": settings.CHILEXPRESS_GEO_KEY,
        "Content-Type": "application/json",
        "Cache-Control": "no-cache"
    }

    # Datos de ejemplo o dinámicos según lo que pongas en tu formulario
    payload = {
        "countyName": "SANTIAGO CENTRO",
        "streetName": "DOCTOR ALLENDE PADIN",
        "pointsOfInterestEnabled": True,
        "streetNameEnabled": True,
        "roadType": 0
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

#Función para buscar calles desde un formulario de Chilexpress  
def buscar_calle_view(request):
    calles = []
    comuna = ""
    calle = ""

    if request.method == "POST":
        comuna = request.POST.get("comuna", "").upper()
        calle = request.POST.get("calle", "").upper()
        print("🔍 Recibido POST:", comuna, calle)

        url = f"{settings.CHILEXPRESS_BASE_URL}/georeference/api/v1.0/streets/search"
        headers = {
            "Ocp-Apim-Subscription-Key": settings.CHILEXPRESS_GEO_KEY,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }
        payload = {
            "countyName": comuna,
            "streetName": calle,
            "pointsOfInterestEnabled": True,
            "streetNameEnabled": True,
            "roadType": 0
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            calles = data.get("streets", [])
        except requests.exceptions.RequestException as e:
            calles = [{"error": str(e)}]

    return render(request, "pages/buscar_calle.html", {
        "calles": calles,
        "comuna": comuna,
        "calle": calle
    })

def detalle_producto(request, producto_id):
    # Busca el producto según el ID, o lanza error 404 si no existe
    producto = get_object_or_404(Producto, id=producto_id)

    # También podrías traer productos similares (por especie, por ejemplo)
    productos_relacionados = Producto.objects.filter(especie=producto.especie).exclude(id=producto.id)[:4]

    return render(request, 'pages/detalle_producto.html', {
        'producto': producto,
        'productos_relacionados': productos_relacionados
    })