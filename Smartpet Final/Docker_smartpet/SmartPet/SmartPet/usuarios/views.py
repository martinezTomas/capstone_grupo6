# tu_app/views.py

# --- Python Standard Library ---
import json
import requests
from decimal import Decimal

# --- Django Core ---
from django.conf import settings
from django.db import transaction
from django.db.models import Sum, Count, Case, When, Q, F
from django.db.models.functions import TruncDay
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password


# --- Django Contrib ---
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

# --- Third-Party Libraries ---
import mercadopago

# --- Local Application Imports (Tu proyecto) ---
from .forms import RegistroUserForm, ProductoForm, UserUpdateForm, ResenaForm, MascotaForm
# IMPORTAMOS LOS NUEVOS MODELOS
from .models import (
    Producto, Carrito, ItemCarrito, Pedido, ItemPedido,
    Region, Comuna, Marca, Categoria, Subcategoria,
    Pedido, ItemCarrito, Resena, Mascota, Raza, Condicion, Edad, Especie
)


# --- Página principal ---
def index(request):
    # (Esta vista no necesita cambios, la lógica de "más vendidos" sigue igual)
    items_vendidos = ItemPedido.objects.exclude(pedido__estado=Pedido.ESTADO_PENDIENTE)
    top_items = items_vendidos.values('producto_id').annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:3]

    top_producto_ids = [item['producto_id'] for item in top_items]

    if top_producto_ids:
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(top_producto_ids)])
        productos_para_mostrar = Producto.objects.filter(pk__in=top_producto_ids).order_by(preserved_order)
    else:
        productos_para_mostrar = Producto.objects.filter(visible=True).order_by('-id')[:3] #  Asegurarse de mostrar solo visibles

    context = {
        'productos': productos_para_mostrar
    }
    return render(request, 'pages/index.html', context)

# --- Página nosotros ---
def nosotros_view(request):
    return render(request, "pages/nosotros.html")

# --- Página catálogo ---
def catalogo_view(request, solo_ofertas=False):
    """
    Muestra el catálogo de productos O solo las ofertas, 
    con filtros dinámicos corregidos para usar IDs en categorías.
    """
    
    # 1. Lógica de inicio (Ofertas vs Catálogo completo)
    if solo_ofertas:
        productos = Producto.objects.filter(visible=True, en_oferta=True)
        titulo_pagina = "🔥 ¡Ofertas Imperdibles!"
    else:
        productos = Producto.objects.filter(visible=True)
        titulo_pagina = "Nuestro Catálogo"

    # 2. Leer parámetros GET
    categoria_id = request.GET.get('categoria', '').strip()
    subcategoria_nombre = request.GET.get('subcategoria', '').strip()
    especie_nombre = request.GET.get('especie', '').strip()
    marca_nombre = request.GET.get('marca', '').strip()
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')

    # 3. Aplicar filtros
    
    # --- FILTRO CATEGORÍA ---
    if categoria_id:
        try:
            # Filtramos por ID (__id) en lugar de nombre
            productos = productos.filter(categoria__id=int(categoria_id))
        except ValueError:
            pass # Si alguien manipula la URL y pone texto, no hacemos nada

    # --- OTROS FILTROS (Se mantienen por nombre según tu HTML) ---
    if subcategoria_nombre:
        productos = productos.filter(subcategoria__nombre__iexact=subcategoria_nombre)
    
    if especie_nombre:
        productos = productos.filter(especie__nombre__iexact=especie_nombre)
        
    if marca_nombre:
        productos = productos.filter(marca__nombre__icontains=marca_nombre)
        
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
        
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    # 4. Cargar datos para los selects (Contexto)
    categorias = Categoria.objects.all().order_by('nombre')
    especies = Especie.objects.all().order_by('nombre')
    marcas = Marca.objects.all().order_by('nombre')
    
    # --- Lógica de Subcategorías (CORREGIDA) ---
    if categoria_id:
        # Si hay una categoría seleccionada, cargamos solo sus hijas
        subcategorias = Subcategoria.objects.filter(
            categoria__id=categoria_id
        ).order_by('nombre')
    else:
        # Si no, mostramos todas (o ninguna, según prefieras)
        subcategorias = Subcategoria.objects.all().order_by('nombre')

    # 5. Preparar Contexto
    # Convertimos categoria_id a entero para que el template pueda compararlo (if c.id == categoria_actual)
    categoria_actual_int = int(categoria_id) if categoria_id and categoria_id.isdigit() else None

    context = {
        'productos': productos,
        'categorias': categorias,
        'subcategorias': subcategorias,
        'especies': especies,
        'marcas': marcas,

        # Estados del filtro para mantener la selección
        'categoria_actual': categoria_actual_int, # Pasamos el entero
        'subcategoria_actual': subcategoria_nombre,
        'especie_actual': especie_nombre,
        'marca_actual': marca_nombre,
        'precio_min': precio_min,
        'precio_max': precio_max,
        
        'titulo_pagina': titulo_pagina 
    }

    return render(request, 'pages/catalogo.html', context)


#  API AJAX — Subcategorías dinámicas
def get_subcategorias(request):
    """
    Versión actualizada: Recibe un ID (categoria_id) y devuelve 
    las subcategorías correspondientes.
    """
    # 1. Obtenemos el ID que envía el JavaScript
    categoria_id = request.GET.get('categoria_id') 

    if not categoria_id:
        return JsonResponse({'subcategorias': []})

    try:
        # 2. Filtramos usando el ID (mucho más seguro y rápido)
        subcategorias = Subcategoria.objects.filter(
            categoria_id=categoria_id
        ).order_by('nombre')
        
        # 3. Preparamos los datos (ID y Nombre)
        data = list(subcategorias.values('id', 'nombre'))
        
        return JsonResponse({'subcategorias': data})
        
    except ValueError:
        return JsonResponse({'subcategorias': []})


# --- VISTA DE DETALLE DE PRODUCTO ---
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, visible=True)
    
    # Obtenemos todas las reseñas para este producto
    resenas = producto.resenas.all()
    
    # Inicializamos variables
    form = ResenaForm()
    ya_resenado = False
    
    # Verificamos si el usuario ya dejó una reseña
    if request.user.is_authenticated:
        if Resena.objects.filter(producto=producto, usuario=request.user).exists():
            ya_resenado = True

    # --- LÓGICA PARA PROCESAR EL FORMULARIO (CUANDO ES POST) ---
    if request.method == 'POST' and request.user.is_authenticated and not ya_resenado:
        form = ResenaForm(request.POST)
        if form.is_valid():
            # Creamos la reseña pero no la guardamos en la BD todavía
            nueva_resena = form.save(commit=False)
            
            # Asignamos el producto y el usuario manualmente
            nueva_resena.producto = producto
            nueva_resena.usuario = request.user
            
            # Ahora sí, guardamos en la BD
            nueva_resena.save()
            
            messages.success(request, '¡Gracias por tu reseña!')
            # Redirigimos a la misma página para evitar re-envíos
            return redirect('detalle_producto', producto_id=producto_id)
        else:
            messages.error(request, 'Hubo un error con tu formulario.')

    # --- CONTEXTO PARA LA PLANTILLA (CUANDO ES GET) ---
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria, 
        visible=True
    ).exclude(id=producto_id)[:4]

    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
        'resenas': resenas,        
        'form_resena': form,     
        'ya_resenado': ya_resenado,
    }
    return render(request, 'pages/detalle_producto.html', context)



# --- VISTAS PARA GESTIÓN DE PRODUCTOS (ADMIN) ---

@login_required
@staff_member_required
def lista_productos_admin(request):
    productos = Producto.objects.all().order_by('nombre')
    context = {'productos': productos}
    return render(request, 'paneladmin/gestion_producto/lista_productos_admin.html', context)

@login_required
@staff_member_required
def crear_producto_admin(request):
    """Crea un nuevo producto desde el panel admin normalizado."""
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Producto creado exitosamente.')
            return redirect('lista_productos_admin')
        else:
            messages.error(request, '❌ Por favor revisa los campos. Algunos datos no son válidos.')
    else:
        form = ProductoForm()

    context = {'form': form, 'titulo': 'Crear Nuevo Producto'}
    return render(request, 'paneladmin/gestion_producto/crear_producto_admin.html', context)

@login_required
@staff_member_required
def modificar_producto_admin(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f' Producto "{producto.nombre}" actualizado.')
            return redirect('lista_productos_admin')
        else:
            messages.error(request, '❌ Hubo errores al actualizar.')
    else:
        form = ProductoForm(instance=producto)
    context = {'form': form, 'titulo': f'Modificar Producto: {producto.nombre}', 'producto': producto}
    return render(request, 'paneladmin/gestion_producto/modificar_producto_admin.html', context)

# para obtener subcategorias en la creacion y actualizacion de productos
@login_required
@staff_member_required
def obtener_subcategorias(request):
    categoria_id = request.GET.get('categoria_id')
    if not categoria_id:
        return JsonResponse({'subcategorias': []})
    subcategorias = Subcategoria.objects.filter(
        categoria_id=categoria_id
    ).values('id', 'nombre')
    return JsonResponse({'subcategorias': list(subcategorias)})

@login_required
@staff_member_required
def eliminar_producto_admin(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.visible = False
        producto.save()
        messages.success(request, f'👁️ Producto "{producto.nombre}" ocultado del catálogo.')
        return redirect('lista_productos_admin')
    context = {'producto': producto}
    return render(request, 'paneladmin/gestion_producto/confirmar_eliminar_admin.html', context)

@login_required
@staff_member_required
def activar_producto_admin(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.visible = True
    producto.save()
    messages.success(request, f' Producto "{producto.nombre}" ahora es visible en el catálogo.')
    return redirect('lista_productos_admin')

# agregar marca y especie via ajax

@csrf_exempt 
def crear_marca_ajax(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            # get_or_create evita duplicados
            marca, created = Marca.objects.get_or_create(nombre=nombre)
            return JsonResponse({'id': marca.id, 'nombre': marca.nombre, 'created': created})
    return JsonResponse({'error': 'Faltan datos'}, status=400)

@csrf_exempt
def crear_especie_ajax(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            especie, created = Especie.objects.get_or_create(nombre=nombre)
            return JsonResponse({'id': especie.id, 'nombre': especie.nombre, 'created': created})
    return JsonResponse({'error': 'Faltan datos'}, status=400)


# --- VISTAS PARA GESTIÓN DE USUARIOS (ADMIN) ---

@login_required
@staff_member_required
def gestion_usuarios(request):
    # Obtenemos todos los usuarios, ordenados por ID
    usuarios = User.objects.all().order_by('id')
    
    context = {
        'usuarios': usuarios
    }
    # Usaremos una nueva plantilla para mostrar la lista
    return render(request, 'paneladmin/gestion_usuario/gestion_usuarios.html', context)


# --- VISTAS PARA GESTIÓN DE PEDIDOS (ADMIN) ---

@login_required
@staff_member_required
def gestion_pedidos(request):

    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    
    context = {
        'pedidos': pedidos
    }

    return render(request, 'paneladmin/gestion_pedido/gestion_pedidos.html', context)

@login_required
@staff_member_required
def pedido_detalle(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    items = pedido.items.all() 
    
    context = {
        'pedido': pedido,
        'items': items
    }

    return render(request, 'paneladmin/gestion_pedido/pedido_detalle.html', context)

# --- VISTAS PARA  DASHBOARD (ADMIN) ---

@staff_member_required
def dashboard_admin(request):
    # 1. Filtramos solo pedidos pagados (Aprobados o Enviados)
    pedidos_validos = Pedido.objects.filter(estado__in=[Pedido.ESTADO_APROBADO, Pedido.ESTADO_ENVIADO])

    # --- KPI 1: Total Vendido Histórico ---
    total_ingresos = pedidos_validos.aggregate(Sum('total'))['total__sum'] or 0

    # --- KPI 2: Cantidad de Pedidos ---
    total_pedidos = pedidos_validos.count()

    # --- KPI 3: Productos Más Vendidos (Top 5) ---
    productos_mas_vendidos = ItemPedido.objects.filter(
        pedido__in=pedidos_validos
    ).values('producto__nombre').annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]

    # --- GRÁFICO 1: Ventas últimos 7 días ---
    fecha_inicio = timezone.now() - timedelta(days=7)
    ventas_por_dia = pedidos_validos.filter(fecha_pedido__gte=fecha_inicio)\
        .annotate(dia=TruncDay('fecha_pedido'))\
        .values('dia')\
        .annotate(total=Sum('total'))\
        .order_by('dia')

    # Preparamos datos para Chart.js (Listas simples)
    fechas_grafico = [v['dia'].strftime('%d/%m') for v in ventas_por_dia]
    montos_grafico = [int(v['total']) for v in ventas_por_dia]

    envios_vs_retiro = pedidos_validos.values('tipo_envio').annotate(count=Count('id'))

    # Datos envios (Listas puras)
    labels_envio = [x['tipo_envio'] for x in envios_vs_retiro]
    data_envio = [x['count'] for x in envios_vs_retiro]

    context = {
        'total_ingresos': total_ingresos,
        'total_pedidos': total_pedidos,
        'productos_top': productos_mas_vendidos,
        
        # PASAMOS LAS LISTAS DIRECTAS (Sin json.dumps)
        'fechas_grafico': fechas_grafico,
        'montos_grafico': montos_grafico,
        'labels_envio': labels_envio,
        'data_envio': data_envio,
    }

    return render(request, 'paneladmin/reportes/dashboard.html', context)




# --- LOGIN Y REGISTRO DE USUARIOS ---

def login_view(request):
    # 1. Usamos 'data=request.POST or None' para limpiar el form en GET
    form = AuthenticationForm(request, data=request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            # 2. Éxito, El form ya validó al usuario.
            user = form.get_user()
            auth_login(request, user)
            
            messages.success(request, f"¡Hola de nuevo, {user.username}!")
            
            return redirect('index')
        else:
            # 3. Si el form NO es válido (credenciales malas), añadimos un mensaje de error.
            messages.error(request, "Usuario o contraseña incorrectos. Por favor, inténtalo de nuevo.")
            
    # 4. Renderizamos la página con el 'form' (que ahora puede tener errores)
    return render(request, 'registration/login.html', {'form': form})

def registrar(request):
    
    form = RegistroUserForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            
            user = form.save()
            usuario = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
            )
            if usuario is not None:
                auth_login(request, usuario)
                
                messages.success(request, f"¡Bienvenido, {user.username}! Tu cuenta ha sido creada exitosamente.")
                
                return redirect('index')
        else:
            # Si el formulario no es válido (username tomado, email duplicado, etc.)
            messages.error(request, "Error al crear la cuenta. Por favor, revisa los campos marcados en rojo.")

    # Devolvemos el 'form' que ahora contiene los errores específicos
    return render(request, 'registration/register.html', {'form': form})

# --- VISTAS DE PERFIL DE USUARIO ---
# --- Mis Pedidos ---

@login_required
def mis_pedidos(request):
   
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    
    context = {
        'pedidos': pedidos
    }
 
    return render(request, 'pages/mis_pedidos.html', context)

def mi_pedido_detalle(request, pedido_id):
    
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    
    items = pedido.items.all()
    
    context = {
        'pedido': pedido,
        'items': items
    }
    return render(request, 'pages/mi_pedido_detalle.html', context)

# --- Mis Mascotas ---

@login_required
def mis_mascotas(request):

    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        if form.is_valid():
            mascota = form.save(commit=False)
            mascota.usuario = request.user
            mascota.save()
            form.save_m2m()
            messages.success(request, f"¡Has añadido a {mascota.nombre} a tu perfil!")
            return redirect('mis_mascotas')
        else:
            messages.error(request, "Hubo un error en el formulario. Por favor, revisa los campos.")
    else:
        form = MascotaForm()

    mascotas_del_usuario = Mascota.objects.filter(usuario=request.user).order_by('nombre')

    context = {
        'form': form,
        'mascotas': mascotas_del_usuario
    }
    return render(request, 'pages/mis_mascotas.html', context)



@login_required
def mascota_detalle(request, slug):
    """
    Paso 3: Muestra la página de perfil de una mascota
    y la lista de productos recomendados para ella.
    """
    # 1. Obtenemos la mascota 
    mascota = get_object_or_404(Mascota, slug=slug, usuario=request.user)

    # --- 2. EL FILTRO MÁGICO ---
    # Obtenemos las propiedades de la mascota
    especie = mascota.especi
    etapa_obj = mascota.etapa_vida_obj
    condiciones = mascota.condiciones.all()
    raza = mascota.raz

    # Empezamos con el filtro base: DEBE coincidir la especie
    filtros = Q(especie=especie)

    # Filtro de Etapa:
    # Productos que coincidan con la etapa (Cachorro) O que sean para todas las etapas (sin etiqueta)
    if etapa_obj:
        filtros &= (Q(edades=etapa_obj) | Q(edades__isnull=True))

    # Filtro de Condiciones:
    if condiciones.exists():
        # Si la mascota tiene condiciones, DEBE coincidir con el producto
        filtros &= Q(condiciones__in=condiciones)
    else:
        # Si la mascota está sana, mostrar productos para sanos (sin etiqueta de condición)
        filtros &= Q(condiciones__isnull=True)
        
    # Filtro de Raza (Opcional):
    if raza:
        # Productos que coincidan con la raza (Bulldog) O que sean para todas las razas (sin etiqueta)
        filtros &= (Q(razas=raza) | Q(razas__isnull=True))

    # 3. Ejecutamos la consulta a la base de datos
    productos_recomendados = Producto.objects.filter(filtros).distinct()[:10] # (Mostramos los primeros 10)

    context = {
        'mascota': mascota,
        'productos': productos_recomendados
    }
    return render(request, 'pages/mascota_detalle.html', context)

@csrf_exempt
def cargar_razas_ajax(request):
    """
    Esta vista auxiliar es para el formulario 'Mis Mascotas'.
    Devuelve las razas (en JSON) según la especie seleccionada.
    """
    especie_id = request.GET.get('especie_id')
    razas = Raza.objects.filter(especie_id=especie_id).order_by('nombre')
    return JsonResponse(list(razas.values('id', 'nombre')), safe=False)


@login_required
def mascota_modificar(request, slug):
    """
    Vista para modificar una mascota existente.
    """
    # Buscamos la mascota por slug y aseguramos que sea del usuario actual
    mascota = get_object_or_404(Mascota, slug=slug, usuario=request.user)

    if request.method == 'POST':
        # Pasamos 'request.POST' y 'request.FILES' (por si sube foto)
        form = MascotaForm(request.POST, request.FILES, instance=mascota)
        
        if form.is_valid():
            form.save()
            messages.success(request, f"¡Perfil de {mascota.nombre} actualizado correctamente!")
            return redirect('mis_mascotas')
        else:
            messages.error(request, "Hubo un error al actualizar. Por favor revisa los campos.")
    
    else:
        # Al cargar la página (GET), cargamos el formulario con los datos de la mascota
        form = MascotaForm(instance=mascota)

    context = {
        'form': form,
        'mascota': mascota
    }
    return render(request, 'pages/mascota_modificar.html', context)


@login_required
def mascota_eliminar(request, slug):
    """
    Vista para eliminar una mascota.
    ✅ MODIFICADO: Ahora funciona al hacer clic en el enlace (GET).
    (Confiamos en la confirmación de JavaScript del frontend).
    """
    mascota = get_object_or_404(Mascota, slug=slug, usuario=request.user)
    
    nombre_mascota = mascota.nombre
    
    # Eliminamos directamente
    mascota.delete()
    
    messages.success(request, f"Has eliminado a {nombre_mascota} de tus registros.")
    return redirect('mis_mascotas')



# --- mi perfil ---

@login_required
def mi_perfil_ver(request):

    context = {
        'usuario': request.user
    }
    return render(request, 'pages/mi_perfil_ver.html', context)

@login_required
def mi_perfil_editar(request):
    if request.method == 'POST':
        # Si se envía el formulario, procesa los datos
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado con éxito!')
    
            return redirect('mi_perfil_ver') 
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        # Si se carga la página (GET), muestra el formulario con los datos actuales
        form = UserUpdateForm(instance=request.user)

    context = {
        'form': form
    }
    # Usaremos una plantilla separada para el formulario
    return render(request, 'pages/mi_perfil_editar.html', context)

# --- vista cambiar Contraseña ---

@login_required
def cambiar_contrasena(request):
    """
    Permite al usuario autenticado cambiar su contraseña actual.
    Requiere ingresar la contraseña actual y confirmar la nueva.
    """
    if request.method == 'POST':
        contrasena_actual = request.POST.get('contrasena_actual')
        nueva_contrasena = request.POST.get('nueva_contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')

        user = request.user

        # Validar la contraseña actual
        if not user.check_password(contrasena_actual):
            messages.error(request, '❌ La contraseña actual es incorrecta.')
            return redirect('cambiar_contrasena')

        # Validar coincidencia entre nueva y confirmación
        if nueva_contrasena != confirmar_contrasena:
            messages.error(request, '⚠️ Las nuevas contraseñas no coinciden.')
            return redirect('cambiar_contrasena')

        # Guardar nueva contraseña
        user.set_password(nueva_contrasena)
        user.save()
        update_session_auth_hash(request, user)  # evita cierre de sesión

        messages.success(request, '✅ Contraseña cambiada correctamente.')
        return redirect('mi_perfil_ver')

    return render(request, 'pages/cambiar_contrasena.html')

# --- vistas olvidar contraseña ---


password_reset_tokens = {}  

def api_password_reset_request(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'No existe una cuenta asociada a ese correo.'
            })

        # Generar token temporal (válido por 1 hora)
        token = get_random_string(length=48)
        expiration = timezone.now() + timedelta(hours=1)
        password_reset_tokens[token] = {'user_id': user.id, 'expires': expiration}

        # Crear URL del enlace de restablecimiento
        reset_link = f"http://127.0.0.1:8000/reset-password/{token}/"

        # Enviar correo al usuario
        send_mail(
            subject='Restablece tu contraseña - SmartPet 🐾',
            message=(
                f'Hola {user.username},\n\n'
                f'Haz clic en el siguiente enlace para restablecer tu contraseña:\n\n'
                f'{reset_link}\n\n'
                'Este enlace expira en 1 hora.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return JsonResponse({
            'success': True,
            'message': 'Se ha enviado un enlace a tu correo electrónico.'
        })

    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def reset_password_view(request, token):
    token_info = password_reset_tokens.get(token)

    # Verificar si el token es inválido o expiró
    if not token_info or timezone.now() > token_info['expires']:
        return render(request, 'restore_password/restablecercontraexpirada.html')

    # Si el usuario envía el formulario con su nueva contraseña
    if request.method == 'POST':
        new_password = request.POST.get('password')
        user = get_object_or_404(User, id=token_info['user_id'])
        user.password = make_password(new_password)
        user.save()

        # Eliminar el token para que no se pueda reutilizar
        del password_reset_tokens[token]

        return render(request, 'restore_password/contraexitosa.html')

    # Mostrar formulario para escribir la nueva contraseña
    return render(request, 'restore_password/restablecercontra.html', {'token': token})


# --- Carrito Vistas y API---
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

@login_required
@transaction.atomic
def crear_pedido(request):
    
    if request.method == 'POST':
        carrito = get_object_or_404(Carrito, usuario=request.user)
        items_carrito = carrito.items.all()

        if not items_carrito:
            messages.error(request, 'Tu carrito está vacío.')
            return redirect('carrito')

        for item_c in items_carrito:
            if item_c.producto.stock < item_c.cantidad:
                messages.error(request, f"No hay stock para '{item_c.producto.nombre}'.")
                return redirect('carrito')

        #  1. Creamos el pedido 
        pedido = Pedido.objects.create(
            usuario=request.user, 
            completado=False,
            # ... (campos de cliente y dirección) ...
        )
        
        total_pedido = 0
        for item_c in items_carrito:
            #  2. Congelamos el precio
            precio_congelado = item_c.producto.precio
            
            ItemPedido.objects.create(
                pedido=pedido,
                producto=item_c.producto,
                cantidad=item_c.cantidad,
                peso=item_c.peso,
                precio_unitario_congelado=precio_congelado 
            )
            #  3. Sumamos usando el precio congelado
            total_pedido += precio_congelado * item_c.cantidad
        
        pedido.total = total_pedido
        pedido.save()
        
        return redirect('iniciar_pago', pedido_id=pedido.id) 
        
    return redirect('index')


# --- Checkout ---
@login_required
def checkout(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    total = sum(item.producto.precio * item.cantidad for item in items)
    
    #  1. Obtenemos las regiones para el dropdown
    regiones = Region.objects.all().order_by('nombre')
    
    context = {
        'items': items, 
        'total': total,
        'regiones': regiones #  2. Las pasamos a la plantilla
    }
    return render(request, 'pages/checkout.html', context)

@login_required
def cotizar_checkout_api(request):
    """
    API para el checkout. (VERSIÓN "PLAN TESIS" - Simple y Robusta)
    - Solo usa la API Cotizador (que SÍ funciona en el sandbox).
    - IGNORA la validación de calle (limitación del sandbox).
    - Captura todos los errores y los devuelve como JSON (corrige el "Calculando...").
    """
    try: 
        # 1. Obtenemos los datos del JavaScript
        comuna_id = request.GET.get('comuna_id')
        calle = request.GET.get('calle')
        numero = request.GET.get('numero')

        if not all([comuna_id, calle, numero]):
            raise Exception("Faltan datos de dirección (comuna, calle, número).")

        # 2. Buscamos la comuna en la BD
        comuna = Comuna.objects.get(id=comuna_id)
        if not comuna.id_chilexpress:
            # ¡Este error SÍ lo verá el usuario! (Ej: Quilicura)
            raise Exception(f"La comuna '{comuna.nombre}' no tiene un código de Chilexpress asignado.")
        
        # Usamos el código de la comuna del dropdown, ignorando la calle.
        # Esta es la limitación que explicarás en tu tesis.
        id_comuna_chilexpress = comuna.id_chilexpress

        # 3. Calcular el peso y dimensiones TOTALES del carrito
        carrito = Carrito.objects.get(usuario=request.user)
        items = carrito.items.all()
        if not items: raise Exception("Tu carrito está vacío")

        peso_total_kg = 0
        alto_max_cm = 0
        ancho_max_cm = 0
        largo_max_cm = 0
        valor_declarado_total = 0

        for item in items:
            producto = item.producto
            peso_total_kg += float(producto.peso_kg) * item.cantidad
            valor_declarado_total += float(producto.precio) * item.cantidad
            if int(producto.alto_cm) > alto_max_cm: alto_max_cm = int(producto.alto_cm)
            if int(producto.ancho_cm) > ancho_max_cm: ancho_max_cm = int(producto.ancho_cm)
            if int(producto.largo_cm) > largo_max_cm: largo_max_cm = int(producto.largo_cm)
            
        # 4. Preparamos LLAMADA 2: COTIZAR (API COTIZADOR)
        url_cotizador = f"{settings.CHILEXPRESS_API_URL}/rating/api/v1.0/rates/courier" 
        headers_cotizador = {
            "Ocp-Apim-Subscription-Key": settings.CHILEXPRESS_COTIZADOR_KEY,
            "Content-Type": "application/json", "Accept": "application/json"
        }
        
        payload_cotizador = {
            "originCountyCode": "MIPU", # Tu bodega
            "destinationCountyCode": id_comuna_chilexpress,
            "package": {
                "weight": str(peso_total_kg),
                "height": str(alto_max_cm),
                "width": str(ancho_max_cm),
                "length": str(largo_max_cm)
            },
            "productType": 3, "contentType": 1, 
            "declaredWorth": str(int(valor_declarado_total)),
            "deliveryTime": 0
        }
        
        # 5. Llamamos a Chilexpress (Cotizador)
        response_cotizador = requests.post(url_cotizador, json=payload_cotizador, headers=headers_cotizador)
        response_cotizador.raise_for_status() 
        data_cotizador = response_cotizador.json()

        # 6. Interpretamos la respuesta (Cotizador)
        if data_cotizador.get("statusCode") != 0:
            raise Exception(data_cotizador.get("statusDescription", "Error desconocido de Chilexpress"))

        servicios = data_cotizador.get("data", {}).get("courierServiceOptions")
        if not servicios:
            
            raise Exception("No hay servicios de despacho disponibles para esta dirección/paquete.")
            
        primer_servicio = servicios[0]
        precio_final = float(primer_servicio.get("serviceValue")) 
        nombre_servicio = primer_servicio.get("serviceDescription")

        # --- ¡ÉXITO TOTAL! ---
        request.session['costo_despacho'] = precio_final
        request.session['servicio_despacho'] = nombre_servicio
        
        return JsonResponse({
            "precio": precio_final, 
            "servicio": nombre_servicio
        }) # (status=200 es el default)

    # --- BLOQUE DE CAPTURA DE ERRORES ---
    
    except (Comuna.DoesNotExist, Carrito.DoesNotExist, Producto.DoesNotExist):
        request.session['costo_despacho'] = 0
        return JsonResponse({"error": "Error de validación: No se encontró la comuna o el carrito."}) 
    
    except requests.exceptions.HTTPError as e:
        error_detalle = f"Error Chilexpress ({e.response.status_code}). "
        try:
            error_api = e.response.json().get('statusDescription', 'Error en la petición')
            error_detalle = f"Error Chilexpress: {error_api}"
        except: pass
            
        request.session['costo_despacho'] = 0
        return JsonResponse({"error": error_detalle})
    
    except Exception as e:
        
        request.session['costo_despacho'] = 0
        return JsonResponse({"error": str(e)})
    
# --------------------------------------------------------------
# --- API PARA COMUNAS DINÁMICAS ---
# --------------------------------------------------------------

def get_comunas(request):
    region_id = request.GET.get('region_id')
    
    # Si no nos envían un ID, devolvemos una lista vacía
    if not region_id:
        return JsonResponse([], safe=False)
        
    # Filtramos las comunas por el ID de la región
    try:
        comunas = Comuna.objects.filter(region_id=region_id).values('id', 'nombre')
        return JsonResponse(list(comunas), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
# --- API PARA REGIONES ---
    
def get_regiones_api(request):
    """
    Una vista API simple para devolver todas las regiones 
    para el modal de simulación de despacho.
    """
    try:
        # .values() es más rápido y crea la lista de diccionarios
        regiones_data = Region.objects.all().order_by('id').values('id', 'nombre')
        
        # Devolvemos la lista directamente (igual que get_comunas)
        return JsonResponse(list(regiones_data), safe=False) 
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# --- SIMULACIÓN DE DESPACHO ---
    
def simular_despacho_api(request):
    """
    API para cotizar el envío de UN producto a una comuna.
    ¡VERSIÓN FINAL, CORREGIDA CON LA DOCUMENTACIÓN REAL!
    """
    try:
        # 1. Obtenemos los datos del JavaScript
        producto_id = request.GET.get('producto_id')
        comuna_id = request.GET.get('comuna_id') # Tu ID interno

        if not producto_id or not comuna_id:
            return JsonResponse({"error": "Faltan parámetros"}, status=400)

        # 2. Buscamos en nuestra Base de Datos
        producto = Producto.objects.get(id=producto_id)
        comuna = Comuna.objects.get(id=comuna_id)
        
        # 3. Traducimos el ID de la comuna
        id_comuna_chilexpress = comuna.id_chilexpress # (Ej: "PALT", "MIPU", "AERO")
        
        if not id_comuna_chilexpress:
            raise Exception(f"La comuna '{comuna.nombre}' no tiene un código de Chilexpress asignado.")

        # 4. Preparamos la llamada a la API
        
        # URL de prueba que encontraste (image_bcbf03.png)
        url_api = f"{settings.CHILEXPRESS_API_URL}/rating/api/v1.0/rates/courier" 
        
        # Headers con tu clave de Cotizador
        headers = {
            "Ocp-Apim-Subscription-Key": settings.CHILEXPRESS_COTIZADOR_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        # --- INICIO DEL PAYLOAD ---
        
        # La API espera 'string' para peso y dimensiones
        peso_str = str(float(producto.peso_kg))
        alto_str = str(int(producto.alto_cm))
        ancho_str = str(int(producto.ancho_cm))
        largo_str = str(int(producto.largo_cm))
        
        # El precio del producto (valor declarado) como string
        valor_declarado_str = str(int(producto.precio))

        payload = {
            "originCountyCode": "MIPU", 
            "destinationCountyCode": id_comuna_chilexpress, 
            "package": {
                "weight": peso_str,
                "height": alto_str,
                "width": ancho_str,
                "length": largo_str
            },
            # 3 = Encomienda (según image_bdaf83.png)
            "productType": 3, 
            # 1 = Tipo de contenido (ejemplo de image_bdafdc.png)
            "contentType": 1, 
            "declaredWorth": valor_declarado_str,
             # 0 = Todos los servicios (según image_bdaf83.png)
            "deliveryTime": 0
        }
        # --- FIN DEL PAYLOAD ---


        # 5. ¡Llamamos a Chilexpress!
        response = requests.post(url_api, json=payload, headers=headers)
        response.raise_for_status() # Lanza error si la API falla (4xx, 5xx)
        data = response.json()

        # 6. Interpretamos la respuesta (Según image_bdb286.png)
        
        if data.get("statusCode") != 0:
            error_msg = data.get("statusDescription", "Error desconocido de Chilexpress")
            raise Exception(error_msg)

        servicios = data.get("data", {}).get("courierServiceOptions")
        
        if not servicios or len(servicios) == 0:
            raise Exception("No hay servicios de despacho disponibles para esta comuna.")
            
        # Tomamos el primer servicio disponible (ej: "PRIORITARIO")
        primer_servicio = servicios[0]
        
        # 'serviceValue' es el precio (viene como string o número)
        precio_final = float(primer_servicio.get("serviceValue")) 
        nombre_servicio = primer_servicio.get("serviceDescription")

        # 7. Enviamos la respuesta limpia a nuestro JavaScript
        return JsonResponse({
            "precio": precio_final, 
            "servicio": nombre_servicio
        })

    except Producto.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)
    except Comuna.DoesNotExist:
        return JsonResponse({"error": "Comuna no encontrada"}, status=404)
    except requests.exceptions.HTTPError as e:
        # Si la API devuelve un 400, 403, 500, etc.
        error_detalle = f"Error de Chilexpress: {e.response.status_code}. Revisa tus claves y el payload."
        try:
            # Intentar leer el error específico que devuelve la API
            error_api = e.response.json().get('statusDescription', 'Error en la petición')
            error_detalle = f"Error de Chilexpress: {error_api}"
        except:
            pass
        return JsonResponse({"error": error_detalle}, status=500)
    except Exception as e:
        # (Cualquier otro error, como la comuna sin ID)
        return JsonResponse({"error": str(e)}, status=500)

#----------------------------------------
# --- INICIO DEL FLUJO MERCADO PAGO ---
#----------------------------------------

@login_required
@transaction.atomic
def pago_mercadopago(request):
    if request.method != 'POST':
        messages.error(request, "Acceso no válido.")
        return redirect("checkout")
    
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    items_carrito = carrito.items.all()

    if not items_carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("carrito")

    for item_c in items_carrito:
        if item_c.producto.stock < item_c.cantidad:
            messages.error(request, f"No hay stock para '{item_c.producto.nombre}'.")
            return redirect('carrito')

    # --- Lectura de datos ---
    nombre_cli = request.POST.get('nombre', '')
    apellido_cli = request.POST.get('apellido', '')
    rut_cli = request.POST.get('rut', '')
    tel_cli = request.POST.get('telefono', '')
    email_cli = request.POST.get('email', request.user.email)

    region_id = request.POST.get('region')
    comuna_id = request.POST.get('comuna')
    calle_data = request.POST.get('calle', '')
    numero_data = request.POST.get('numero', '')
    depto_data = request.POST.get('depto_oficina', '')
    
    # --- Lógica Envío/Retiro ---
    tipo_envio_form = request.POST.get('tipo_envio', 'retiro')
    # Mapeamos al modelo: 'despacho' -> 'ENVIO', 'retiro' -> 'RETIRO'
    tipo_envio_db = 'ENVIO' if tipo_envio_form == 'despacho' else 'RETIRO'

    costo_despacho = 0
    servicio_despacho = "Retiro en Tienda"
    region_obj = None
    comuna_obj = None

    if tipo_envio_db == 'ENVIO':
        costo_despacho = request.session.get('costo_despacho', 0)
        servicio_despacho = request.session.get('servicio_despacho', 'Despacho')

        if costo_despacho == 0:
            messages.error(request, "Error: Debes calcular el costo de envío.")
            return redirect("checkout")
        
        try:
            if region_id: region_obj = Region.objects.get(id=region_id)
            if comuna_id: comuna_obj = Comuna.objects.get(id=comuna_id)
        except:
            messages.error(request, "Dirección inválida.")
            return redirect("checkout")

    # --- Crear Pedido ---
    pedido = Pedido.objects.create(
        usuario=request.user,
        estado=Pedido.ESTADO_PENDIENTE, 
        tipo_envio=tipo_envio_db,       
        
        nombre_cliente=nombre_cli,
        apellido_cliente=apellido_cli,
        rut_cliente=rut_cli,
        telefono_cliente=tel_cli,
        email_cliente=email_cli,
        
        region=region_obj,
        comuna=comuna_obj,
        calle=calle_data,
        numero=numero_data,
        depto_oficina=depto_data
    )
    
    total_pedido = 0 
    items_para_mp = [] 

    for item_c in items_carrito:
        precio_congelado = item_c.producto.precio
        ItemPedido.objects.create(
            pedido=pedido,
            producto=item_c.producto,
            cantidad=item_c.cantidad,
            peso=item_c.peso,
            precio_unitario_congelado=precio_congelado
        )
        total_pedido += precio_congelado * item_c.cantidad
        items_para_mp.append({
            "title": item_c.producto.nombre,
            "quantity": int(item_c.cantidad),
            "unit_price": float(precio_congelado),
            "currency_id": "CLP",
        })
    
    if costo_despacho > 0:
        items_para_mp.append({
            "title": f"Envío: {servicio_despacho}",
            "quantity": 1,
            "unit_price": float(costo_despacho),
            "currency_id": "CLP",
        })
    
    pedido.total = total_pedido + Decimal(str(costo_despacho))
    pedido.save()

    # Limpiar sesión
    if 'costo_despacho' in request.session: del request.session['costo_despacho']
    if 'servicio_despacho' in request.session: del request.session['servicio_despacho']

    # MercadoPago
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    base_url = "https://rectangular-luanna-overliterarily.ngrok-free.dev" # ⚠️ REVISA TU URL

    preference_data = {
        "items": items_para_mp,
        "back_urls": {
            "success": f"{base_url}/mercadopago/success/",
            "failure": f"{base_url}/mercadopago/failure/",
            "pending": f"{base_url}/mercadopago/pending/",
        },
        "auto_return": "approved",
        "binary_mode": True,
        "external_reference": str(pedido.id),
        "notification_url": f"{base_url}/mercadopago/webhook/"
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response.get("response", {})

    if "init_point" in preference:
        return redirect(preference["init_point"])
    else:
        messages.error(request, "Error al generar pago con MercadoPago.")
        return redirect("checkout")
    
#----------------------------------------
# --- RUTAS DE RETORNO MERCADOPAGO ---
#----------------------------------------

@login_required
@transaction.atomic
def mp_success(request):
    pedido_id = request.GET.get('external_reference')
    
    if not pedido_id:
        messages.error(request, "Error: Referencia no encontrada.")
        return redirect("index")

    try:
        pedido = Pedido.objects.get(id=pedido_id, usuario=request.user)
    except Pedido.DoesNotExist:
        messages.error(request, "Pedido no encontrado.")
        return redirect("index")

    # Limpiar Carrito
    #-- IMPORTANTE: Hacemos esto primero para evitar duplicados si el usuario vuelve aquí.
    try:
        Carrito.objects.filter(usuario=request.user).delete()
    except Exception as e:
        print(f"Error borrando carrito: {e}")

    # --- Verificación de Estado ---
    if pedido.estado != Pedido.ESTADO_PENDIENTE:
        # Si el Webhook ya lo aprobó, mostramos éxito y terminamos.
        messages.success(request, f"¡Pago exitoso! Pedido #{pedido.id} (Confirmado por Webhook)")
        return render(request, "mercadopago/mercadopago_success.html", {"pedido": pedido})

    
    # Descontar Stock (Respaldo)
    items_pedido = pedido.items.all()
    for item in items_pedido:
        if item.producto and item.producto.stock >= item.cantidad:
            item.producto.stock -= item.cantidad
            item.producto.save()
    
    # Actualizar estado manualmente (Respaldo)
    pedido.estado = Pedido.ESTADO_APROBADO
    pedido.save()

    messages.success(request, f"¡Pago exitoso! Pedido #{pedido.id}")
    return render(request, "mercadopago/mercadopago_success.html", {"pedido": pedido})


@login_required
def mp_failure(request):
    pedido_id = request.GET.get('external_reference')
    messages.error(request, f"❌ El pago fue rechazado o falló (Pedido #{pedido_id}).")
    return render(request, "mercadopago/mercadopago_failure.html")


@login_required
def mp_pending(request):
    pedido_id = request.GET.get('external_reference')
    messages.info(request, f"⏳ El pago está pendiente de aprobación (Pedido #{pedido_id}).")
    return render(request, "mercadopago/mercadopago_pending.html")


# --- WEBHOOK (Recomendación: Implementar lógica) ---
@csrf_exempt
def mp_webhook(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error"}, status=405)

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    
    try:
        data = json.loads(request.body)
        
        if data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            if not payment_id: return JsonResponse({"status": "error"}, status=400)

            payment_info = sdk.payment().get(payment_id)
            if payment_info["status"] != 200:
                return JsonResponse({"status": "error"}, status=404)

            payment = payment_info["response"]
            payment_status = payment.get("status")
            external_reference = payment.get("external_reference")

            try:
                pedido = Pedido.objects.get(id=int(external_reference))
            except:
                return JsonResponse({"status": "error"}, status=404)

            # --- FLUJO PRINCIPAL ---
            if payment_status == 'approved' and pedido.estado == Pedido.ESTADO_PENDIENTE:
                print(f"WEBHOOK: Pago Aprobado Pedido #{pedido.id} ({pedido.tipo_envio})")
                
                try:
                    with transaction.atomic():
                        # 1. Marcar Aprobado
                        pedido.estado = Pedido.ESTADO_APROBADO
                        pedido.save()

                        # 2. Email Confirmación (Para ambos casos)
                        enviar_email_confirmacion(pedido)

                        # 3. Lógica Diferenciada
                        if pedido.tipo_envio == 'ENVIO':
                            # -> Llamar a Chilexpress
                            tracking, etiqueta = generar_envio_chilexpress(pedido)
                            pedido.tracking_number = tracking
                            pedido.etiqueta_pdf_url = etiqueta
                            pedido.estado = Pedido.ESTADO_ENVIADO
                            pedido.save()
                            enviar_email_enviado(pedido)
                        else:
                            # -> Es RETIRO (No hacer nada con Chilexpress)
                            print("WEBHOOK: Retiro en tienda. No se genera envío.")
                
                except Exception as e:
                    print(f"WEBHOOK ERROR CRÍTICO: {str(e)}")
                    pedido.estado = Pedido.ESTADO_ERROR
                    pedido.save()

        return JsonResponse({"status": "received"}, status=200)

    except Exception as e:
        print(f"WEBHOOK EXCEPTION: {str(e)}")
        return JsonResponse({"status": "error"}, status=500)
    
# ==============================================================
# TERMINA EL FLUJO DE MERCADO PAGO
# ==============================================================


# ==============================================================
# ---  FUNCIONES DE EMAIL ---
# ==============================================================

def enviar_email_confirmacion(pedido):
    """
    Envía el email de "Pago Aprobado".
    Adapta el mensaje según si es Retiro o Envío.
    """
    try:
        asunto = f"¡Recibimos tu pedido #{pedido.id}, SmartPet!"
        
        # Lógica del mensaje según el tipo
        if pedido.tipo_envio == 'RETIRO':
            texto_entrega = """
Método de Entrega: RETIRO EN TIENDA
Dirección de Retiro: Av. El Conquistador 741, Maipú.
Horario: Lunes a Sábado 10:00 - 19:00 hrs.

¡Te enviaremos otro correo cuando tu pedido esté listo para ser retirado!
"""
        else:
            texto_entrega = f"""
Método de Entrega: DESPACHO A DOMICILIO
Dirección de Envío: {pedido.calle} {pedido.numero}, {pedido.comuna.nombre if pedido.comuna else ''}

En cuanto preparemos tu paquete y lo entreguemos a Chilexpress, 
te enviaremos un nuevo correo con el número de seguimiento.
"""

        mensaje = f"""
Hola {pedido.nombre_cliente},

¡Gracias por tu compra en SmartPet!
Hemos recibido tu pago y tu pedido #{pedido.id} ha sido aprobado.

Resumen del Pedido:
--------------------
Total Pagado: ${pedido.total}
{texto_entrega}

Gracias por preferirnos,
El equipo de SmartPet
"""
        
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [pedido.email_cliente],
            fail_silently=False,
        )
        print(f"EMAIL: Confirmación enviada para Pedido #{pedido.id}")

    except Exception as e:
        print(f"ERROR EMAIL (Confirmación) Pedido #{pedido.id}: {str(e)}")


def enviar_email_enviado(pedido):

    if not pedido.tracking_number:
        return

    try:
        asunto = f"¡Tu pedido #{pedido.id} de SmartPet ya está en camino!"
        mensaje = f"""
Hola {pedido.nombre_cliente},

¡Buenas noticias! Tu pedido #{pedido.id} ha sido enviado.

Puedes seguir tu paquete usando este número de seguimiento de Chilexpress:
TRACKING: {pedido.tracking_number}

Link de seguimiento:
https://www.chilexpress.cl/seguimiento-en-linea (luego ingresa el número)

Gracias,
El equipo de SmartPet
"""
        send_mail(
            asunto, mensaje, settings.DEFAULT_FROM_EMAIL,
            [pedido.email_cliente], fail_silently=False,
        )
        print(f"EMAIL: Notificación de envío enviada para Pedido #{pedido.id}")
    except Exception as e:
        print(f"ERROR EMAIL (Enviado) Pedido #{pedido.id}: {str(e)}")


def generar_envio_chilexpress(pedido):
    """
    Genera la etiqueta en Chilexpress.
    TIENE UN ESCUDO DE SEGURIDAD PARA RETIROS.
    """
    print(f"ENVIO: Iniciando generación de envío para Pedido #{pedido.id}")
    
    # --- Retiro en Tienda ---
    if pedido.tipo_envio == 'RETIRO':
        print(f"ENVIO: Cancelado. El Pedido #{pedido.id} es para RETIRO EN TIENDA.")
        return (None, None) 

    try:
        # 1. Calcular Peso y Dimensiones
        items_pedido = pedido.items.all()
        if not items_pedido: raise Exception("El pedido no tiene items.")

        peso_total_kg = 0
        alto_max_cm = 0
        ancho_max_cm = 0
        largo_max_cm = 0
        valor_declarado_total = float(pedido.total)

        for item in items_pedido:
            producto = item.producto
            if not producto: continue
            peso_total_kg += float(producto.peso_kg) * item.cantidad
            if int(producto.alto_cm) > alto_max_cm: alto_max_cm = int(producto.alto_cm)
            if int(producto.ancho_cm) > ancho_max_cm: ancho_max_cm = int(producto.ancho_cm)
            if int(producto.largo_cm) > largo_max_cm: largo_max_cm = int(producto.largo_cm)

        # 2. Validar Dirección de Envío
        if not pedido.comuna or not pedido.comuna.id_chilexpress:
            raise Exception("El pedido es 'DESPACHO' pero no tiene una comuna Chilexpress válida.")
        
        id_comuna_chilexpress_destino = pedido.comuna.id_chilexpress

        # 3. Construir Payload
        url_envio = f"{settings.CHILEXPRESS_API_URL}/transport-orders/api/v1.0/shipping-orders"
        headers_envio = {
            "Ocp-Apim-Subscription-Key": settings.CHILEXPRESS_ENVIOS_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "data": {
                "shipments": [{
                    "reference": f"Pedido #{pedido.id}",
                    "shipmentTypeCode": 3,
                    "serviceTypeCode": 3,
                    "originAddress": {
                        "streetName": "Av. El Conquistador",
                        "streetNumber": "741",
                        "complement": "Bodega SmartPet",
                        "countyCode": "MIPU"
                    },
                    "destinationAddress": {
                        "streetName": pedido.calle,
                        "streetNumber": pedido.numero,
                        "complement": pedido.depto_oficina or "",
                        "countyCode": id_comuna_chilexpress_destino
                    },
                    "contact": {
                        "name": pedido.nombre_cliente,
                        "lastName": pedido.apellido_cliente,
                        "email": pedido.email_cliente,
                        "phone": pedido.telefono_cliente,
                        "rut": pedido.rut_cliente
                    },
                    "package": {
                        "weight": str(peso_total_kg),
                        "height": str(alto_max_cm),
                        "width": str(ancho_max_cm),
                        "length": str(largo_max_cm)
                    },
                    "declaredValue": str(int(valor_declarado_total))
                }],
                "certificate": {
                    "typeCode": "PD",
                    "formatCode": 1,
                    "labelSize": 1
                }
            }
        }
        
        # 4. Llamar API
        print(f"ENVIO: Llamando a Chilexpress para Pedido #{pedido.id}...")
        response = requests.post(url_envio, json=payload, headers=headers_envio)
        response.raise_for_status() 
        data = response.json()

        if data.get("statusCode") != 0:
            raise Exception(data.get("statusDescription", "Error desconocido de Chilexpress"))
        
        shipment_data = data.get("data", {}).get("shipments", [])[0]
        certificate_data = data.get("data", {}).get("certificate", {})

        tracking_number = shipment_data.get("trackingNumber")
        etiqueta_url = certificate_data.get("url")

        if not tracking_number or not etiqueta_url:
            raise Exception("API Chilexpress OK, pero no devolvió tracking o etiqueta.")

        print(f"ENVIO: ¡Éxito! Tracking: {tracking_number}")
        return (tracking_number, etiqueta_url)

    except requests.exceptions.HTTPError as e:
        try: error_msg = e.response.json().get("statusDescription", str(e))
        except: error_msg = str(e)
        print(f"ERROR HTTP Chilexpress: {error_msg}")
        raise Exception(f"Error Chilexpress: {error_msg}")

    except Exception as e:
        print(f"ERROR generar_envio: {str(e)}")
        raise e
