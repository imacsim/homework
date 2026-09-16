import socket
import threading
import protocol

HOST = "0.0.0.0"
PORT = 5000

clients = {}
clients_lock = threading.Lock()


def broadcast(message: str, exclude_sock=None):
    data = message.encode("utf-8")
    with clients_lock:
        dead = []
        for sock, username in clients.items():
            if sock is exclude_sock:
                continue
            try:
                protocol.send_message(sock, "TEXT", data)
            except (BrokenPipeError, ConnectionResetError, OSError):
                dead.append(sock)

        for sock in dead:
            remove_client(sock)


def remove_client(sock: socket.socket):
    username = None
    with clients_lock:
        if sock in clients:
            username = clients.pop(sock)

    if username:
        print(f"[SERVER] {username} отключился")
        broadcast(f"*** {username} покинул чат ***")

    try:
        sock.close()
    except OSError:
        pass


def handle_client(sock: socket.socket, addr):
    print(f"[SERVER] Новое подключение: {addr}")
    username = None

    try:
        while True:
            msg = protocol.recv_message(sock)
            if msg is None:
                break

            command, payload = msg
            text = payload.decode("utf-8", errors="ignore")

            if command == "JOIN":
                username = text.strip()
                if not username:
                    protocol.send_message(sock, "ERROR", "Имя не может быть пустым".encode("utf-8"))
                    continue

                with clients_lock:
                    if username in clients.values():
                        protocol.send_message(sock, "ERROR", "Имя уже занято".encode("utf-8"))
                        continue
                    clients[sock] = username

                print(f"[SERVER] {username} присоединился")
                protocol.send_message(sock, "TEXT", f"Добро пожаловать, {username}!".encode())
                broadcast(f"*** {username} вошёл в чат ***", exclude_sock=sock)

            elif command == "TEXT":
                if not username:
                    protocol.send_message(sock, "ERROR", "Сначала JOIN".encode("utf-8"))
                    continue
                full_msg = f"{username}: {text}"
                print(f"[CHAT] {full_msg}")
                broadcast(full_msg, exclude_sock=sock)

            elif command == "LIST":
                with clients_lock:
                    users = ", ".join(clients.values()) or "никого нет"
                protocol.send_message(sock, "TEXT", f"Онлайн: {users}".encode())

            elif command == "QUIT":
                break

            else:
                protocol.send_message(sock, "ERROR", f"Неизвестная команда: {command}".encode())

    except (ConnectionResetError, BrokenPipeError, OSError) as e:
        print(f"[SERVER] Ошибка с {addr}: {e}")
    finally:
        remove_client(sock)


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER] Слушаю {HOST}:{PORT}")

    try:
        while True:
            client_sock, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Останавливаюсь...")
    finally:
        server.close()


if __name__ == "__main__":
    main()