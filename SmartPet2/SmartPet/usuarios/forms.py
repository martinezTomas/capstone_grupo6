from django import forms
from .models import Producto
from django.contrib.auth.forms import UserCreationForm  # [web:1]
from django.contrib.auth.models import User  # [web:1]
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


from django import forms
from .models import Producto

from django import forms
from .models import Producto

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
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'subcategoria': forms.Select(attrs={'class': 'form-select'}),
            'especie': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Fit Formula, Bravery...'
            }),
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



