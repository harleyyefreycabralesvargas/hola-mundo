"""
main.py — Robot de Extracción Gastronómica Masiva (TheMealDB)
Diseñado para la API del Orquestador v3 de Cajasan
"""

import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")
def consultar_recetas_abecedario():
    # 1. Cargar archivo local SOLO si existe (para tus pruebas en el escritorio)
    # En el Worker real, como este archivo no se sube a Git, se saltará esto automáticamente.
    if os.path.exists("bot.env"):
        load_dotenv(dotenv_path="bot.env")
    else:
        load_dotenv()  # Intenta cargar un .env estándar por si acaso

    # 2. Leer la ruta desde la memoria (inyectada por el Worker o cargada del archivo)
    ruta_consolidado = os.getenv("RUTA_CONSOLIDADO_EXCEL")
    
    if not ruta_consolidado:
        print("[ERROR] La variable de entorno 'RUTA_CONSOLIDADO_EXCEL' no está definida.", file=sys.stderr)
        print("[AYUDA] Asegúrate de agregar esta variable en el formulario de la tarea/proyecto en el Master.", file=sys.stderr)
        sys.exit(1)
        
    # Limpiar comillas adicionales que a veces quedan al procesar strings
    ruta_consolidado = ruta_consolidado.strip('"').strip("'")
        
    # 3. Asegurar que la carpeta donde se guardará el Excel exista en la máquina Windows
    directorio_destino = os.path.dirname(ruta_consolidado)
    if directorio_destino and not os.path.exists(directorio_destino):
        try:
            os.makedirs(directorio_destino, exist_ok=True)
        except Exception as e:
            print(f"[ERROR] No se pudo crear el directorio de destino ({directorio_destino}): {e}", file=sys.stderr)
            sys.exit(1)

    base_url = "https://www.themealdb.com/api/json/v1/1/search.php"
    headers = {"User-Agent": "RPA-Cajasan-Extractor/3.0"}
    
    todas_las_comidas = []
    # Genera la lista de letras de la 'a' a la 'z'
    abecedario = [chr(i) for i in range(ord('a'), ord('z') + 1)]
    
    print("=" * 70)
    print("[RPA START] INICIANDO EXTRACCIÓN MASIVA DE THEMEALDB")
    print(f"[CONFIG] Ruta de Destino: {ruta_consolidado}")
    print("=" * 70)
    
    for letra in abecedario:
        print(f"\n[LETRA '{letra.upper()}'] Consultando recetas en la API...")
        
        params = {"f": letra}
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"  [WARN] Falló la consulta de la letra {letra}: {e}. Continuando...", file=sys.stderr)
            continue
            
        meals = data.get("meals")
        if not meals:
            print(f"  [INFO] No se encontraron recetas que empiecen por '{letra.upper()}'.")
            continue
            
        print(f"  [OK] ¡Se encontraron {len(meals)} recetas!")
        
        for meal in meals:
            nombre = meal.get("strMeal") or "Sin Nombre"
            categoria = meal.get("strCategory") or "Sin Categoría"
            area = meal.get("strArea") or "Internacional"
            youtube = meal.get("strYoutube") or "No disponible"
            fuente = meal.get("strSource") or "No disponible"
            id_meal = meal.get("idMeal")
            
            # Log estético alineado que verás impecable en la pantalla de Streamlit
            print(f"    [Plato] {nombre.ljust(30)} | Categoría: {categoria.ljust(12)} | Origen: {area}")
            
            todas_las_comidas.append({
                "ID Registro": id_meal,
                "Nombre del Plato": nombre,
                "Categoría": categoria,
                "Región / Área": area,
                "Enlace Video (YouTube)": youtube,
                "Fuente / Receta original": fuente,
                "Fecha Extracción": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
        # Breve pausa para no saturar el servidor de la API
        time.sleep(0.3)

    print("\n" + "=" * 70)
    print(" [PROCESO DE CONSOLIDACIÓN] Generando archivo de Excel con Pandas...")
    print("=" * 70)
    
    if todas_las_comidas:
        try:
            df = pd.DataFrame(todas_las_comidas)
            # Ordenar lógicamente por Categoría y Nombre del plato
            df = df.sort_values(by=["Categoría", "Nombre del Plato"])
            
            # Escribir el Excel con dos hojas (Data completa + Métricas resumidas)
            with pd.ExcelWriter(ruta_consolidado, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Consolidado General", index=False)
                
                resumen_categorias = df["Categoría"].value_counts().reset_index()
                resumen_categorias.columns = ["Categoría", "Total Recetas Encontradas"]
                resumen_categorias.to_excel(writer, sheet_name="Métricas por Categoría", index=False)
            
            print(f" [RPA SUCCESS] ¡Proceso completado con éxito!")
            print(f" Total de platos extraídos y organizados: {len(df)}")
            print(f" Archivo Excel guardado en: {ruta_consolidado}")
            print("=" * 70)
            
        except Exception as e:
            print(f"[ERROR] No se pudo escribir el archivo Excel final: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("[WARN] No se obtuvo ningún dato de las recetas. Excel no generado.", file=sys.stderr)

if __name__ == "__main__":
    consultar_recetas_abecedario()
