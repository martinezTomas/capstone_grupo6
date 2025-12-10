# usuarios/management/commands/poblar_codigos_rm.py
# --- VERSIÓN 3 (¡La definitiva!) ---

import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from usuarios.models import Comuna

class Command(BaseCommand):
    help = 'Puebla los códigos de Chilexpress para la RM desde rm_chilexpress.json'

    def handle(self, *args, **options):
        # 1. Definimos la ruta al archivo JSON
        json_file_path = os.path.join(settings.BASE_DIR, 'rm_chilexpress.json')
        
        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR('ERROR: Archivo rm_chilexpress.json no encontrado.'))
            return

        # 2. Abrimos y leemos el JSON
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # --- ✅ ¡AQUÍ ESTÁ LA CORRECCIÓN! ---
        # Le decimos que tome la lista 'coverageAreas', y de ahí, el PRIMER (y único)
        # elemento [0], que es la lista real de comunas.
        try:
            lista_de_comunas = data.get("coverageAreas")[0]
        except (TypeError, IndexError, KeyError):
            self.stdout.write(self.style.ERROR('ERROR: El JSON no tiene el formato esperado "coverageAreas": [[...]]'))
            return

        self.stdout.write(f"Procesando {len(lista_de_comunas)} áreas de cobertura desde el JSON...")
        
        actualizados = 0
        errores = 0
        
        # 3. Recorremos la lista de comunas
        for comuna_data in lista_de_comunas:
            
            # Solo procesamos las comunas principales (queryMode: 1)
            if comuna_data.get('queryMode') == 1:
                
                nombre_chx = comuna_data.get('countyName')
                codigo_chx = comuna_data.get('countyCode')

                if not nombre_chx or not codigo_chx:
                    continue
                
                # 4. Buscamos la comuna en nuestra base de datos
                try:
                    comuna = Comuna.objects.get(nombre__iexact=nombre_chx)
                    
                    comuna.id_chilexpress = codigo_chx
                    comuna.save()
                    
                    self.stdout.write(self.style.SUCCESS(f"Actualizado: {comuna.nombre} -> {codigo_chx}"))
                    actualizados += 1
                    
                except Comuna.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"  Advertencia: No se encontró '{nombre_chx}' en tu base de datos."))
                    errores += 1
                except Comuna.MultipleObjectsReturned:
                    self.stdout.write(self.style.ERROR(f"  Error: Múltiples comunas coinciden con '{nombre_chx}'."))
                    errores += 1
        
        self.stdout.write(self.style.SUCCESS(f"\n¡Proceso completado!"))
        self.stdout.write(f"Comunas principales actualizadas: {actualizados}")
        self.stdout.write(f"Comunas no encontradas (o sub-zonas ignoradas): {errores}")