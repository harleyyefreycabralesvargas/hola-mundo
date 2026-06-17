"""
dolar.py — Extractor de Dólar (TRM Oficial Colombia) via API
Diseñado para el Orquestador RPA Cajasan
"""

import sys
import requests

def extraer_precio_dolar_api():
    # Usamos una API abierta y confiable para la TRM de Colombia
    url = "https://api.vloop.co/trm/current" 
    # Alternativa pública de respaldo por si la anterior falla
    url_backup = "https://trm-colombia.vercel.app/api/trm"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    print(f"[INFO] Consultando API de TRM oficial...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print("[WARN] API principal con detalles, intentando API de respaldo...")
            response = requests.get(url_backup, headers=headers, timeout=15)
            
        response.raise_for_status()
        datos = response.json()
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a los servicios de TRM: {e}", file=sys.stderr)
        sys.exit(1)

    print("[INFO] Parseando respuesta JSON...")
    
    # Extraemos el valor dependiendo de cuál API respondió
    precio = datos.get("valor") or datos.get("value")
    
    if precio:
        # Dar formato de dinero (ej: 4,150.25)
        precio_formateado = f"{float(precio):,.2f}"
        
        print("=" * 50)
        print(f"🤖 [RPA OK] ¡VALOR DEL DÓLAR OBTENIDO EN VIVO!")
        print(f"[RESULTADO] TRM hoy: ${precio_formateado} COP")
        print("=" * 50)
    else:
        print("[ERROR] El JSON recibido no contiene las claves esperadas.", file=sys.stderr)
        print(f"[DEBUG] JSON: {datos}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    print("[INICIO] Iniciando robot de extracción de divisas...")
    extraer_precio_dolar_api()
    print("[FIN] Procesamiento completado de forma exitosa.")
