from colorama import Fore, Style, init

# Inicializa colorama
init(autoreset=True)

print(Fore.GREEN + "[OK] El entorno virtual del Worker funciona correctamente.")
print(Fore.CYAN + "[INFO] Procesando datos de prueba del orquestador...")
print(Fore.YELLOW + "[WARN] Esto es una alerta de prueba colorida.")
print(Fore.MAGENTA + "=== FIN DEL PROCESO ===")