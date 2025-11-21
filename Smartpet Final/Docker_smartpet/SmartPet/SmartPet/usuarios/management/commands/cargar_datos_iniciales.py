# usuarios/management/commands/cargar_datos_iniciales.py

import json
from django.core.management.base import BaseCommand
from django.db import transaction

# 
# ✅ ESTA ES LA LÍNEA CORREGIDA
# Importa los modelos desde 'usuarios.models' en lugar de 'tu_app.models'
#
from usuarios.models import Region, Comuna, Marca, Categoria, Subcategoria, Especie

# --- DATOS A CARGAR ---

REGIONES_Y_COMUNAS = {
    "Arica y Parinacota": ["Arica", "Camarones", "Putre", "General Lagos"],
    "Tarapacá": ["Iquique", "Alto Hospicio", "Pozo Almonte", "Camiña", "Colchane", "Huara", "Pica"],
    "Antofagasta": ["Antofagasta", "Mejillones", "Sierra Gorda", "Taltal", "Calama", "Ollagüe", "San Pedro de Atacama"],
    "Atacama": ["Copiapó", "Caldera", "Tierra Amarilla", "Chañaral", "Diego de Almagro", "Vallenar", "Freirina", "Huasco", "Alto del Carmen"],
    "Coquimbo": ["La Serena", "Coquimbo", "Andacollo", "La Higuera", "Paiguano", "Vicuña", "Illapel", "Canela", "Los Vilos", "Salamanca", "Ovalle", "Combarbalá", "Monte Patria", "Punitaqui", "Río Hurtado"],
    "Valparaíso": ["Valparaíso", "Casablanca", "Concón", "Juan Fernández", "Puchuncaví", "Quintero", "Viña del Mar", "Isla de Pascua", "Los Andes", "Calle Larga", "Rinconada", "San Esteban", "La Ligua", "Cabildo", "Papudo", "Petorca", "Zapallar", "Quillota", "Calera", "Hijuelas", "La Cruz", "Nogales", "San Antonio", "Algarrobo", "Cartagena", "El Quisco", "El Tabo", "Santo Domingo", "San Felipe", "Catemu", "Llaillay", "Panquehue", "Putaendo", "Santa María", "Quilpué", "Limache", "Olmué", "Villa Alemana"],
    "Metropolitana de Santiago": ["Santiago", "Cerrillos", "Cerro Navia", "Conchalí", "El Bosque", "Estación Central", "Huechuraba", "Independencia", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú", "Ñuñoa", "Pedro Aguirre Cerda", "Peñalolén", "Providencia", "Pudahuel", "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Joaquín", "San Miguel", "San Ramón", "Vitacura", "Puente Alto", "Pirque", "San José de Maipo", "Colina", "Lampa", "Tiltil", "San Bernardo", "Buin", "Calera de Tango", "Paine", "Melipilla", "Alhué", "Curacaví", "María Pinto", "San Pedro", "Talagante", "El Monte", "Isla de Maipo", "Padre Hurtado", "Peñaflor"],
    "Libertador General Bernardo O'Higgins": ["Rancagua", "Codegua", "Coinco", "Coltauco", "Doñihue", "Graneros", "Las Cabras", "Machalí", "Malloa", "Mostazal", "Olivar", "Peumo", "Pichidegua", "Quinta de Tilcoco", "Rengo", "Requínoa", "San Vicente", "Pichilemu", "La Estrella", "Litueche", "Marchihue", "Navidad", "Paredones", "San Fernando", "Chépica", "Chimbarongo", "Lolol", "Nancagua", "Palmilla", "Peralillo", "Placilla", "Pumanque", "Santa Cruz"],
    "Maule": ["Talca", "Constitución", "Curepto", "Empedrado", "Maule", "Pelarco", "Pencahue", "Río Claro", "San Clemente", "San Rafael", "Cauquenes", "Chanco", "Pelluhue", "Curicó", "Hualañé", "Licantén", "Molina", "Rauco", "Romeral", "Sagrada Familia", "Teno", "Vichuquén", "Linares", "Colbún", "Longaví", "Parral", "Retiro", "San Javier", "Villa Alegre", "Yerbas Buenas"],
    "Ñuble": ["Chillán", "Bulnes", "Chillán Viejo", "El Carmen", "Pemuco", "Pinto", "Quillón", "San Ignacio", "Yungay", "Quirihue", "Cobquecura", "Coelemu", "Ninhue", "Portezuelo", "Ránquil", "Treguaco", "San Carlos", "Coihueco", "Ñiquén", "San Fabián", "San Nicolás"],
    "Biobío": ["Concepción", "Coronel", "Chiguayante", "Florida", "Hualqui", "Lota", "Penco", "San Pedro de la Paz", "Santa Juana", "Talcahuano", "Tomé", "Hualpén", "Lebu", "Arauco", "Cañete", "Contulmo", "Curanilahue", "Los Álamos", "Tirúa", "Los Ángeles", "Antuco", "Cabrero", "Laja", "Mulchén", "Nacimiento", "Negrete", "Quilaco", "Quilleco", "San Rosendo", "Santa Bárbara", "Tucapel", "Yumbel", "Alto Biobío"],
    "La Araucanía": ["Temuco", "Carahue", "Cunco", "Curarrehue", "Freire", "Galvarino", "Gorbea", "Lautaro", "Loncoche", "Melipeuco", "Nueva Imperial", "Padre Las Casas", "Perquenco", "Pitrufquén", "Pucón", "Saavedra", "Teodoro Schmidt", "Toltén", "Vilcún", "Villarrica", "Cholchol", "Angol", "Collipulli", "Curacautín", "Ercilla", "Lonquimay", "Los Sauces", "Lumaco", "Purén", "Renaico", "Traiguén", "Victoria"],
    "Los Ríos": ["Valdivia", "Corral", "Lanco", "Los Lagos", "Máfil", "Mariquina", "Paillaco", "Panguipulli", "La Unión", "Futrono", "Lago Ranco", "Río Bueno"],
    "Los Lagos": ["Puerto Montt", "Calbuco", "Cochamó", "Fresia", "Frutillar", "Los Muermos", "Llanquihue", "Maullín", "Puerto Varas", "Castro", "Ancud", "Chonchi", "Curaco de Vélez", "Dalcahue", "Puqueldón", "Queilén", "Quellón", "Quemchi", "Quinchao", "Osorno", "Puerto Octay", "Purranque", "Puyehue", "Río Negro", "San Juan de la Costa", "San Pablo", "Chaitén", "Futaleufú", "Hualaihué", "Palena"],
    "Aysén del General Carlos Ibáñez del Campo": ["Coyhaique", "Lago Verde", "Aysén", "Cisnes", "Guaitecas", "Cochrane", "O'Higgins", "Tortel", "Chile Chico", "Río Ibáñez"],
    "Magallanes y de la Antártica Chilena": ["Punta Arenas", "Laguna Blanca", "Río Verde", "San Gregorio", "Cabo de Hornos (Ex-Navarino)", "Antártica", "Porvenir", "Primavera", "Timaukel", "Natales", "Torres del Paine"]
}

CATEGORIAS_INICIALES = [
    ('Alimento', ['Alimentos Secos', 'Alimentos Húmedos', 'Snacks y Premios']),
    ('Accesorio', ['Collares y Arnés', 'Placas Identificadoras', 'Fuentes para Beber', 'Camas y Escondites', 'Rascadores']),
    ('Higiene', ['Arenas', 'Limpieza y Repelentes', 'Shampoo y Acondicionadores']),
    ('Salud', ['Antiparasitarios', 'Suplementos', 'Productos Calmantes']),
    ('Juguete', ['Juguetes Interactivos', 'Pelotas', 'Varitas']),
    ('Ropa', ['Abrigos', 'Disfraces']),
]

MARCAS_INICIALES = ['Purina', 'Royal Canin', 'Master Cat', 'Dog Chow', 'Pedigree', 'Whiskas', 'Catit', 'Zeecat']

ESPECIES_INICIALES = ['Perro', 'Gato', 'Pez', 'Ave', 'Roedor', 'Reptil', 'Otros']


class Command(BaseCommand):
    help = 'Carga los datos iniciales de regiones, comunas, categorías, etc.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Iniciando carga de datos iniciales...")

        # --- 1. Cargar Regiones y Comunas ---
        self.stdout.write("Cargando Regiones y Comunas...")
        for nombre_region, comunas_list in REGIONES_Y_COMUNAS.items():
            region_obj, created = Region.objects.get_or_create(nombre=nombre_region)
            if created:
                self.stdout.write(f"  > Región creada: {nombre_region}")
            
            for nombre_comuna in comunas_list:
                comuna_obj, created = Comuna.objects.get_or_create(
                    nombre=nombre_comuna, 
                    region=region_obj
                )
                if created:
                    self.stdout.write(f"    - Comuna creada: {nombre_comuna}")

        # --- 2. Cargar Categorías y Subcategorías ---
        self.stdout.write("Cargando Categorías y Subcategorías...")
        for nombre_cat, subcategorias_list in CATEGORIAS_INICIALES:
            cat_obj, created = Categoria.objects.get_or_create(nombre=nombre_cat)
            if created:
                self.stdout.write(f"  > Categoría creada: {nombre_cat}")
            
            for nombre_subcat in subcategorias_list:
                subcat_obj, created = Subcategoria.objects.get_or_create(
                    nombre=nombre_subcat,
                    categoria=cat_obj
                )
                if created:
                    self.stdout.write(f"    - Subcategoría creada: {nombre_subcat}")

        # --- 3. Cargar Marcas ---
        self.stdout.write("Cargando Marcas...")
        for nombre_marca in MARCAS_INICIALES:
            marca_obj, created = Marca.objects.get_or_create(nombre=nombre_marca)
            if created:
                self.stdout.write(f"  > Marca creada: {nombre_marca}")

        # --- 4. Cargar Especies ---
        self.stdout.write("Cargando Especies...")
        for nombre_especIE in ESPECIES_INICIALES:
            especie_obj, created = Especie.objects.get_or_create(nombre=nombre_especIE)
            if created:
                self.stdout.write(f"  > Especie creada: {nombre_especIE}")


        self.stdout.write(self.style.SUCCESS("¡Carga de datos iniciales completada con éxito!"))