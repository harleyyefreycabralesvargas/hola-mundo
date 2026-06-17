"""
main.py — Robot Extractor de Dólar (TRM Colombia)
Diseñado para el Orquestador RPA Cajasan
"""

import sys
from bs4 import BeautifulSoup
import requests

def extraer_precio_dolar():
    url = "https://dolar.wilkinsonpc.com.co/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"[INFO] Conectando a la fuente financiera: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] No se pudo acceder a la página web: {e}", file=sys.stderr)
        sys.exit(1)

    print("[INFO] Analizando el contenido de la página...")
    soup = BeautifulSoup(response.text, "html.parser")

    # Buscamos el contenedor principal del valor de la TRM actual
    indicador = soup.find("div", class_="trm-precio")
    
    # Alternativa si cambia el diseño: buscar en la tabla de indicadores rápidos
    if not indicador:
        indicador = soup.find("span", class_="valor")

    if indicador:
        # Extraemos el texto y limpiamos espacios o caracteres extraños
        precio_texto = indicador.text.strip().replace("$", "").replace(" ", "")
        print("=" * 50)
        print(f"[OK] ¡PRECIO DEL DÓLAR DETECTADO!")
        print(f"[RESULTADO] TRM Actual: ${precio_texto} COP")
        print("=" * 50)
    else:
        print("[ERROR] No se encontró el elemento HTML del precio en la página.", file=sys.stderr)
        # Imprimimos un pedazo del HTML para debugging en los logs del Master
        print(f"[DEBUG] HTML parcial: {response.text[:500]}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    print("[INICIO] Iniciando robot de extracción de divisas...")
    extraer_precio_dolar()
    print("[FIN] Procesamiento completado de forma exitosa.")