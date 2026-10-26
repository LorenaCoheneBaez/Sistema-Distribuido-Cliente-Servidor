import socket
import threading
import json
import time
from concurrent.futures import ThreadPoolExecutor

HOST = "0.0.0.0"
PORT = 9000
MAX_WORKER_THREADS = 4

# Simulación de la tarea que ejecutaría el worker
def execute_task(task_data: dict) -> dict:
    task_id = task_data.get("id")
    action = task_data.get("action")
    payload = task_data.get("payload", {})
    
    # Simula trabajo intensivo (ej. procesar datos)
    time.sleep(1.5)
    
    if action == "suma":
        result = sum(payload.get("numeros", []))
    elif action == "reverse":
        result = str(payload.get("text", ""))[::-1]
    else:
        result = "Accion no soportada"

    return {
        "status": "COMPLETED",
        "task_id": task_id,
        "result": result,
        "processed_by_thread": threading.current_thread().name
    }

# Conexión del cliente
def handle_client(conn: socket.socket, addr: tuple, executor: ThreadPoolExecutor):
    print(f"[NUEVA CONEXION] Cliente conectado desde {addr}")
    buffer = ""
    try:
        while True:
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break
            buffer += data
            
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                
                task_data = json.loads(line)
                print(f"[TAREA RECIBIDA] ID: {task_data.get('id')} - Encolando al Pool de Hilos...")
                
                # Despacha la tarea al pool de workers y espera el resultado
                future = executor.submit(execute_task, task_data)
                result = future.result()
                
                # Envia respuesta al cliente
                response = json.dumps(result) + "\n"
                conn.sendall(response.encode("utf-8"))
    except (ConnectionResetError, json.JSONDecodeError) as e:
        print(f"[ERROR] Problema en conexión con {addr}: {e}")
    finally:
        print(f"[DESCONECTADO] Cliente {addr} desconectado.")
        conn.close()

def start_server():
    executor = ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS, thread_name_prefix="WorkerThread")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[SERVIDOR INICIADO] Escuchando en {HOST}:{PORT} con {MAX_WORKER_THREADS} workers.")

    try:
        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr, executor),
                daemon=True
            )
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[APAGANDO] Deteniendo el servidor y el pool de workers...")
    finally:
        executor.shutdown(wait=True)
        server_socket.close()

if __name__ == "__main__":
    start_server()