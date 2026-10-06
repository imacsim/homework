import socket
import protocol

HOST = "127.0.0.1"
PORT = 5000


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Не удалось подключиться к серверу")
        return

    print("Подключено к серверу задач")
    print("Доступные команды: /add <текст>, /list, /done <номер>, /quit")

    try:
        while True:
            try:
                line = input("> ").strip()
            except (KeyboardInterrupt, EOFError):
                print()
                protocol.send_message(sock, "QUIT")
                break

            if not line:
                continue

            parts = line.split(maxsplit=1)
            cmd = parts[0]
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "/add":
                protocol.send_message(sock, "ADD", arg.encode("utf-8"))
            elif cmd == "/list":
                protocol.send_message(sock, "LIST")
            elif cmd == "/done":
                protocol.send_message(sock, "DONE", arg.encode("utf-8"))
            elif cmd == "/quit":
                protocol.send_message(sock, "QUIT")
                msg = protocol.recv_message(sock)
                if msg:
                    _, payload = msg
                    print(payload.decode("utf-8", errors="ignore"))
                break
            else:
                print("неизвестная команда. Доступны: /add, /list, /done, /quit")
                continue

            msg = protocol.recv_message(sock)
            if msg is None:
                print("Соединение с сервером разорвано")
                break

            resp_cmd, payload = msg
            text = payload.decode("utf-8", errors="ignore")

            if resp_cmd == "ERROR":
                print(f"[Ошибка] {text}")
            else:
                print(text)

    finally:
        sock.close()
        print("Сессия завершена")


if __name__ == "__main__":
    main()