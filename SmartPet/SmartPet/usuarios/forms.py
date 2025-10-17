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


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        
        # Usamos los nombres de campo que están en nuestro modelo actualizado
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'imagen']
        
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'precio': 'Precio',
            'stock': 'Stock Disponible',
            'imagen': 'Imagen del Producto'
        }
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bravery Salmon'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 66990'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 50'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'})
        }



