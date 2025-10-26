import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm  # <-- CORREGIDO
from .forms import RegistroUserForm                     # <-- CORREGIDO
from .models import Producto, Carrito, ItemCarrito, Pedido, ItemPedido
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction

def index(request):
    # 1. Obtenemos todos los objetos Producto de la base de datos
    productos = Producto.objects.all()
    
    # 2. Creamos un 'contexto' para enviar los productos a la plantilla
    context = {
        'productos': productos
    }
    
    # 3. Renderizamos la plantilla y le enviamos el contexto
    return render(request, 'pages/index.html', context)

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None) 
    if request.method == "POST" and form.is_valid(): 
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        ) 
        if user is not None:
            auth_login(request, user)  # crea la sesión 
            return redirect('index') 
    return render(request, 'registration/login.html', {'form': form}) 

def registrar(request):
    form = RegistroUserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()  # crea el usuario 
        usuario = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
        )  # autentica con datos validados 
        if usuario is not None:
            auth_login(request, usuario)  # inicia sesión tras registrarse 
            return redirect('index')
    return render(request, 'registration/register.html', {'form': form})

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
    data = [{'id': str(item.producto.id), 'nombre': item.producto.nombre, 'precio': int(item.producto.precio), 'imagen': item.producto.imagen.url, 'cantidad': item.cantidad, 'peso': item.peso} for item in items]
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

# --- Vista para Finalizar Compra ---

@login_required
@transaction.atomic
def crear_pedido(request):
    if request.method == 'POST':
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        items_carrito = carrito.items.all()

        if not items_carrito:
            messages.error(request, 'No puedes realizar un pedido con el carrito vacío.')
            return redirect('carrito')

        # Verificación de Stock
        for item_c in items_carrito:
            producto = item_c.producto
            if producto.stock < item_c.cantidad:
                messages.error(request, f"No hay suficiente stock para '{producto.nombre}'. Solo quedan {producto.stock} unidades.")
                return redirect('carrito')

        # Si hay stock, creamos el pedido
        pedido = Pedido.objects.create(usuario=request.user, completado=True)
        for item_c in items_carrito:
            producto = item_c.producto
            ItemPedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=item_c.cantidad,
                peso=item_c.peso
            )
            # Descontamos el stock
            producto.stock -= item_c.cantidad
            producto.save()
        
        items_carrito.delete() # Limpiamos el carrito
        messages.success(request, '¡Tu pedido ha sido realizado con éxito!')
        return redirect('index')
    return redirect('index')

