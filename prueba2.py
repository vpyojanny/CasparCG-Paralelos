import websocket

def on_open(ws):
    print("Conexión abierta")

def on_message(ws, message):
    print(f"Mensaje recibido: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Conexión cerrada")

ws_url = "ws://localhost:5250"
ws = websocket.WebSocketApp(ws_url, on_open=on_open, on_message=on_message,
                            on_error=on_error, on_close=on_close)
ws.run_forever()
