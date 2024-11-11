import random
import mysql.connector
import time
import socket
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

CONFIG_DB = {
    'host': 'localhost',
    'user': 'root',
    'password': 'VLsysadmin2024',
    'database': 'loteria',
    'port': 3306
}

CASPARCG_HOST = "localhost"
CASPARCG_PORT = 5250

def conectar_base_datos():
    try:
        conexion = mysql.connector.connect(**CONFIG_DB)
        return conexion
    except mysql.connector.Error as error:
        print(f"Error de conexión: {error}")
        return None

def obtener_numeros_aleatorios():
    conexion = conectar_base_datos()
    if conexion is None:
        return [0, 0, 0]
    
    cursor = conexion.cursor()
    cursor.execute("SELECT numero FROM numeros ORDER BY RAND() LIMIT 3")
    numeros = [fila[0] for fila in cursor.fetchall()]
    cursor.close()
    conexion.close()
    return numeros

def enviar_a_casparcg(numero, capa, funcion_set_data, index):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CASPARCG_HOST, CASPARCG_PORT))
            
            if index == 1:
                sock.sendall(f'CG 1-{capa} ADD {capa} "lottery_template" 1 "<templateData></templateData>"\r\n'.encode('utf-8'))
                time.sleep(0.5)
            
            comando = f'CG 1-{capa} UPDATE {capa} "<templateData><componentData id=\\"{funcion_set_data}{index}\\"><data value=\\"{numero}\\"/></componentData></templateData>"\r\n'
            sock.sendall(comando.encode('utf-8'))
            print(f"Actualizado en CasparCG para capa {capa}: Número {index} -> {numero}")

    except socket.error as error:
        print(f"Fallo al enviar a CasparCG: {error}")

def enviar_resultados_loteria(numeros, capa, funcion_set_data):
    with ThreadPoolExecutor(max_workers=3) as executor:
        for indice, numero in enumerate(numeros, start=1):
            executor.submit(enviar_a_casparcg, numero, capa, funcion_set_data, indice)
            time.sleep(1)

def generar_y_guardar_resultados(nombre_loteria, capa, funcion_set_data, intervalo, retraso_inicial):
    time.sleep(retraso_inicial)
    while True:  # Ciclo continuo para mantener la ejecución
        numeros = obtener_numeros_aleatorios()
        
        conexion = conectar_base_datos()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO resultados (nombre_loteria, numero1, numero2, numero3, fecha) VALUES (%s, %s, %s, %s, %s)",
                (nombre_loteria, numeros[0], numeros[1], numeros[2], datetime.now())
            )
            conexion.commit()
            cursor.close()
            conexion.close()
            print(f"Resultados guardados para {nombre_loteria}: {numeros}")
        
        enviar_resultados_loteria(numeros, capa, funcion_set_data)
        time.sleep(intervalo)

if __name__ == "__main__":
    loterias_config = [
        ("Loteria_A", 10, "setDataA", 32, 0),
        ("Loteria_B", 11, "setDataB", 32, 0),
        ("Loteria_C", 12, "setDataC", 32, 0)
    ]
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(lambda loteria: generar_y_guardar_resultados(*loteria), loterias_config)
