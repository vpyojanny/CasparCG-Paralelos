import json
import time
import random
import threading
from websocket import create_connection

# Cargar configuración
with open("./config.json") as f:
    config = json.load(f)

# Conexión WebSocket con CasparCG
def connect_to_caspar():
    try:
        ws = create_connection("ws://localhost:5250")
        print("Conectado con éxito")
        return ws
    except Exception as e:
        print(f"Error al conectar con CasparCG: {e}")
        return None  # Retornar None si no se puede conectar

def generate_lottery_results(lottery, ws):
    while True:
        numbers = [random.randint(1, 50) for _ in range(3)]
        # Usamos .get() para evitar KeyError si 'effects' no está en el diccionario
        effects = lottery.get('effects', None)  # Valor predeterminado None si no existe
        display_results(lottery['name'], numbers, effects, ws)
        time.sleep(lottery['update_interval'])

def display_results(name, numbers, effects, ws):
    # Verificar si la conexión WebSocket existe antes de intentar enviar el comando
    if ws is None:
        print(f"Error: No se pudo enviar resultados a {name}, WebSocket no está conectado.")
        return
    
    # Crear la cadena de comando para CasparCG
    result_text = f"{name}: {' '.join(map(str, numbers))}"
    command = f'CG 1-1 ADD 1 "template_name" 1 "{result_text}"'
    
    # Enviar el comando al WebSocket de CasparCG
    try:
        ws.send(command)
        print(f"Updated {name} with numbers: {numbers}")
    except Exception as e:
        print(f"Error updating {name}: {e}")

if __name__ == "__main__":
    # Conectar a CasparCG mediante WebSocket
    ws = connect_to_caspar()

    # Si no se pudo conectar, no continuar con la ejecución
    if ws is None:
        print("No se pudo establecer conexión con CasparCG. Terminando el programa.")
    else:
        # Crear un hilo para cada lotería para ejecutar en paralelo
        threads = []
        for lottery in config['lotteries']:
            t = threading.Thread(target=generate_lottery_results, args=(lottery, ws))
            threads.append(t)
            t.start()

        # Esperar a que todos los hilos terminen
        for t in threads:
            t.join()

        # Cerrar la conexión WebSocket al final
        if ws is not None:
            ws.close()
