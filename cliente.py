import socket
import json
import uuid

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000

def run_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"[CONECTADO] Conectado exitosamente al servidor {SERVER_HOST}:{SERVER_PORT}")
        
        # Tareas para enviar
        tasks = [
            {
                "id": str(uuid.uuid4())[:8],
                "action": "suma",
                "payload": {"numeros": [10, 20, 30, 40]}
            },
            {
                "id": str(uuid.uuid4())[:8],
                "action": "reverse",
                "payload": {"text": "Arquitectura Distribuida"}
            },
            {
                "id": str(uuid.uuid4())[:8],
                "action": "suma",
                "payload": {"numeros": [100, 250, 75]}
            }
        ]

        buffer = ""
        for task in tasks:

            message = json.dumps(task) + "\n"
            print(f"\n[ENVIANDO] Tarea ID: {task['id']} (Accion: {task['action']})")
            client_socket.sendall(message.encode("utf-8"))
            
            # Recibir la respuesta
            while "\n" not in buffer:
                chunk = client_socket.recv(1024).decode("utf-8")
                if not chunk:
                    raise ConnectionError("El servidor cerró la conexión inesperadamente.")
                buffer += chunk
            
            response_line, buffer = buffer.split("\n", 1)
            response = json.loads(response_line)
            print(f"[RESPUESTA RECIBIDA]:\n{json.dumps(response, indent=2)}")

    except ConnectionRefusedError:
        print(f"[ERROR] No fue posible conectar con el servidor en {SERVER_HOST}:{SERVER_PORT}. ¿Está encendido?")
    finally:
        client_socket.close()
        print("\n[FINALIZADO] Conexión de socket cerrada.")

if __name__ == "__main__":
    run_client()