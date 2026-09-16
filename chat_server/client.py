import socket
import threading
import protocol
import sys


HOST = "127.0.0.1"
PORT = 5000


def receive_loop(sock: socket.socket):
    while True:
        msg = protocol.recv_message(sock)
        if msg is None:
            print("\n[Клиент] Соединение с сервером разорвано")
            break

        command, payload = msg
        text = payload.decode("utf-8", errors="ignore")

        if command == "TEXT":
            print(f"\n{text}")
        elif command == "ERROR":
            print(f"\n[Ошибка сервера] {text}")
        else:
            print(f"\n[{command}] {text}")


def main():
    if len(sys.argv) < 2:
        print("Использование: python client.py <имя_пользователя>")
        return

    username = sys.argv[1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Не удалось подключиться к серверу")
        return

    protocol.send_message(sock, "JOIN", username.encode("utf-8"))

    t = threading.Thread(target=receive_loop, args=(sock,), daemon=True)
    t.start()

    print(f"Подключено как {username}. Команды: /list, /quit")

    try:
        while True:
            line = input()
            if not line:
                continue

            if line.strip().lower() == "/quit":
                protocol.send_message(sock, "QUIT")
                break
            elif line.strip().lower() == "/list":
                protocol.send_message(sock, "LIST")
            else:
                protocol.send_message(sock, "TEXT", line.encode("utf-8"))

    except (KeyboardInterrupt, EOFError):
        protocol.send_message(sock, "QUIT")
    finally:
        sock.close()
        print("\nВыход.")


if __name__ == "__main__":
    main()