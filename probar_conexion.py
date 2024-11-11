import websocket

def on_open(ws):
    print("Conexión WebSocket establecida")
    # Enviar un mensaje simple de prueba
    ws.send('INFO')

def on_message(ws, message):
    print(f"Mensaje recibido: {message}")
    # Imprimir cada mensaje para ver qué está enviando CasparCG

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Conexión cerrada")

ws = websocket.WebSocketApp("ws://localhost:5250",
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.run_forever()
