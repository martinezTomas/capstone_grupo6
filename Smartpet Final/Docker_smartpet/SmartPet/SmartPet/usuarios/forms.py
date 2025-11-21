from django import forms
from .models import Producto, Categoria, Subcategoria, Especie, Marca, Resena, Mascota, Especie, Raza, Condicion
from django.contrib.auth.forms import UserCreationForm  # [web:1]
from django.contrib.auth.models import User  # [web:1]
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper  # [web:85]
from crispy_forms.layout import Layout, Field, Submit  # [web:85]

class RegistroUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    # Opcional: quitar help_texts molestos
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text="",  # oculta lista por defecto en UI, validadores siguen activos
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="",  # idem
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']  # [web:1]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # [web:230]
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # Si ya envuelves el formulario con <form> en tu plantilla, descomenta:
        self.helper.form_tag = False  # evita <form> duplicado [web:233]
        self.helper.layout = Layout(
            Field('username', css_class='input-form'),
            Field('first_name', css_class='input-form'),
            Field('last_name', css_class='input-form'),
            Field('email', css_class='input-form'),
            Field('password1', css_class='input-form'),
            Field('password2', css_class='input-form'),
        )  # [web:85]
        self.helper.add_input(Submit('submit', 'Crear cuenta', css_class='btn-enviar'))  # [web:85]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Busca si CUALQUIER usuario ya tiene este email
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Ya existe una cuenta registrada con este correo electrónico.")
        
        return email

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombre(s)',
            'last_name': 'Apellido(s)',
            'email': 'Correo Electrónico',
        }

    # --- VALIDACIÓN PARA EDITAR PERFIL ---
    # Esto se ejecuta cuando un usuario logueado edita su perfil.
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # self.instance es el usuario que se está editando
        usuario_actual = self.instance 
        
        # Busca si OTRO usuario (excluyéndome a mí) ya tiene este email
        if User.objects.filter(email__iexact=email).exclude(pk=usuario_actual.pk).exists():
            raise ValidationError("Este correo electrónico ya está en uso por otro usuario.")
            
        return email


class MascotaForm(forms.ModelForm):
    
    class Meta:
        model = Mascota
        fields = [
            'nombre', 
            'especie', 
            'raza', 
            'fecha_nacimiento', 
            'condiciones',
            'foto', # Asegúrate de tener este campo en tu modelo si lo usas
        ]
        widgets = {
            # Esto le dice a Django que espere y envíe el formato YYYY-MM-DD
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'condiciones': forms.CheckboxSelectMultiple(),
            'foto': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Configuración de campos opcionales
        self.fields['raza'].required = False
        self.fields['condiciones'].required = False
        # Si tu modelo no tiene 'foto', borra esta línea de abajo
        if 'foto' in self.fields:
            self.fields['foto'].required = False

        # 2. ✅ FIX FECHA: Si estamos editando, forzamos el formato de texto para el input
        if self.instance and self.instance.pk and self.instance.fecha_nacimiento:
            self.fields['fecha_nacimiento'].initial = self.instance.fecha_nacimiento.strftime('%Y-%m-%d')

        # 3. Lógica de Razas (Select dependiente)
        if 'especie' in self.data:
            # Caso A: Hay datos POST (el usuario eligió especie o falló la validación)
            try:
                especie_id = int(self.data.get('especie'))
                self.fields['raza'].queryset = Raza.objects.filter(especie_id=especie_id).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['raza'].queryset = Raza.objects.none()
        
        elif self.instance and self.instance.pk:
            # Caso B: Editando una mascota existente (Cargamos las razas de su especie actual)
            self.fields['raza'].queryset = Raza.objects.filter(especie=self.instance.especie).order_by('nombre')
        
        else:
            # Caso C: Creando nueva mascota (Lista vacía hasta que seleccionen especie)
            self.fields['raza'].queryset = Raza.objects.none()


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'descripcion',
            'precio',
            'stock',
            'imagen',
            'categoria',
            'subcategoria',
            'especie',
            'marca',
            'alto_cm',
            'ancho_cm',
            'largo_cm',
            'peso_kg',
        ]

        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'precio': 'Precio ($)',
            'stock': 'Stock Disponible',
            'imagen': 'Imagen del Producto',
            'categoria': 'Categoría',
            'subcategoria': 'Subcategoría',
            'especie': 'Especie',
            'marca': 'Marca',
            'alto_cm': 'Altura (cm)',
            'ancho_cm': 'Ancho (cm)',
            'largo_cm': 'Largo (cm)',
            'peso_kg': 'Peso (kg)',
        }

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Bravery Salmon Adulto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción breve del producto...'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 66990'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 50'
            }),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select', 'id': 'id_categoria'}),
            'subcategoria': forms.Select(attrs={'class': 'form-select', 'id': 'id_subcategoria'}),
            'especie': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.Select(attrs={'class': 'form-select'}),
            'alto_cm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 30'
            }),
            'ancho_cm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 20'
            }),
            'largo_cm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 15'
            }),
            'peso_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': 'Ej: 1.2'
            }),
        }

    # --- PERSONALIZACIÓN ---
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ordenamos desplegables
        self.fields['categoria'].queryset = Categoria.objects.all().order_by('nombre')
        self.fields['subcategoria'].queryset = Subcategoria.objects.all().order_by('categoria__nombre', 'nombre')
        self.fields['especie'].queryset = Especie.objects.all().order_by('nombre')
        self.fields['marca'].queryset = Marca.objects.all().order_by('nombre')

        # Etiquetas vacías
        self.fields['categoria'].empty_label = 'Seleccione una categoría'
        self.fields['subcategoria'].empty_label = 'Seleccione una subcategoría (opcional)'
        self.fields['especie'].empty_label = 'Seleccione una especie'
        self.fields['marca'].empty_label = 'Seleccione una marca (opcional)'

        # --- 🔧 Lógica para subcategorías dependientes ---
        if 'categoria' in self.data:
            try:
                categoria_id = int(self.data.get('categoria'))
                self.fields['subcategoria'].queryset = Subcategoria.objects.filter(categoria_id=categoria_id).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['subcategoria'].queryset = Subcategoria.objects.none()
        elif self.instance.pk and self.instance.categoria:
            self.fields['subcategoria'].queryset = Subcategoria.objects.filter(categoria=self.instance.categoria).order_by('nombre')
        else:
            self.fields['subcategoria'].queryset = Subcategoria.objects.none()

class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        # Solo queremos que el usuario ingrese el rating y el comentario.
        # El 'producto' y 'usuario' los pondremos automáticamente en la vista.
        fields = ['rating', 'comentario']
        
        labels = {
            'rating': 'Tu calificación (de 1 a 5 estrellas)',
            'comentario': 'Tu opinión (opcional)',
        }
        
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }