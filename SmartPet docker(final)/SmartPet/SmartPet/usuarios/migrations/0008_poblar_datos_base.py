from django.db import migrations
from django.utils.text import slugify # <-- Importamos slugify

# ¡Aquí definimos las listas de datos que queremos crear!
EDADES = [
    'Cachorro', 
    'Adulto', 
    'Senior'
]

CONDICIONES = [
    'Renal', 
    'Urinario', 
    'Obesidad', 
    'Gastrointestinal', 
    'Piel Sensible / Alergia', 
    'Articular / Movilidad', 
    'Cardíaco', 
    'Diabetes'
]

RAZAS_PERRO = [
    'Mestizo', 'Poodle (Caniche)', 'Pastor Alemán', 'Bulldog Francés', 
    'Labrador Retriever', 'Golden Retriever', 'Yorkshire Terrier', 
    'Dachshund (Teckel)', 'Chihuahua', 'Pug', 'Boxer', 'Fox Terrier', 'Beagle'
]

RAZAS_GATO = [
    'Doméstico Pelo Corto', 'Doméstico Pelo Largo', 'Siamés', 
    'Persa', 'Ragdoll', 'Bengala', 'Maine Coon'
]


def poblar_datos(apps, schema_editor):
    """
    Este script creará todos los objetos base para las tablas de filtros.
    """
    # Obtenemos los modelos de la app 'usuarios'
    Especie = apps.get_model('usuarios', 'Especie')
    Raza = apps.get_model('usuarios', 'Raza')
    Condicion = apps.get_model('usuarios', 'Condicion')
    Edad = apps.get_model('usuarios', 'Edad')

    # --- 1. Poblar Especies (Base) ---
    # Usamos get_or_create() para no crear duplicados si ya existen
    perro, _ = Especie.objects.get_or_create(nombre='Perro')
    gato, _ = Especie.objects.get_or_create(nombre='Gato')

    # --- 2. Poblar Edades ---
    for nombre in EDADES:
        # Usamos update_or_create para asegurar que el slug se cree/actualice
        Edad.objects.update_or_create(
            nombre=nombre, 
            defaults={'slug': slugify(nombre)}
        )

    # --- 3. Poblar Condiciones ---
    for nombre in CONDICIONES:
        Condicion.objects.update_or_create(
            nombre=nombre,
            defaults={'slug': slugify(nombre)}
        )
        
    # --- 4. Poblar Razas (Perro) ---
    for nombre in RAZAS_PERRO:
        Raza.objects.update_or_create(
            nombre=nombre, 
            especie=perro,
            defaults={'slug': slugify(f"perro {nombre}")}
        )
        
    # --- 5. Poblar Razas (Gato) ---
    for nombre in RAZAS_GATO:
        Raza.objects.update_or_create(
            nombre=nombre, 
            especie=gato,
            defaults={'slug': slugify(f"gato {nombre}")}
        )

# (Esta función es para poder revertir la migración si es necesario)
def borrar_datos(apps, schema_editor):
    Especie = apps.get_model('usuarios', 'Especie')
    Raza = apps.get_model('usuarios', 'Raza')
    Condicion = apps.get_model('usuarios', 'Condicion')
    Edad = apps.get_model('usuarios', 'Edad')
    
    Edad.objects.filter(nombre__in=EDADES).delete()
    Condicion.objects.filter(nombre__in=CONDICIONES).delete()
    Raza.objects.filter(nombre__in=RAZAS_PERRO, especie__nombre='Perro').delete()
    Raza.objects.filter(nombre__in=RAZAS_GATO, especie__nombre='Gato').delete()
    # (No borramos Especies por si acaso)


class Migration(migrations.Migration):

    # Depende de la última migración que creamos (la 0007)
    dependencies = [
        ('usuarios', '0007_mascota_slug_producto_condiciones_producto_edades_and_more'),
    ]

    operations = [
        # ¡Aquí le decimos a Django que ejecute nuestra función!
        migrations.RunPython(poblar_datos, borrar_datos),
    ]