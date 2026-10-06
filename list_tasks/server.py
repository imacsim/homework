import socket
import threading
import protocol

HOST = "0.0.0.0"
PORT = 5000

tasks = []
tasks_lock = threading.Lock()


def format_tasks() -> str:
    if not tasks:
        return "Список задач пуст"
    lines = []
    for idx, task in enumerate(tasks, start=1):
        status = "[x]" if task["done"] else "[ ]"
        lines.append(f"{idx}. {status} {task['text']}")
    return "\n".join(lines)


def handle_client(sock: socket.socket, addr):
    print(f"[SERVER] Подключился клиент: {addr}")
    try:
        while True:
            msg = protocol.recv_message(sock)
            if msg is None:
                break

            command, payload = msg
            text = payload.decode("utf-8", errors="ignore").strip()

            if command == "ADD":
                if not text:
                    protocol.send_message(sock, "ERROR", "Ошибка: текст задачи не может быть пустым"
                                          .encode("utf-8"))
                    continue

                with tasks_lock:
                    tasks.append({"text": text, "done": False})
                    task_id = len(tasks)

                protocol.send_message(sock, "TEXT", f"Задача #{task_id} добавлена.".encode("utf-8"))

            elif command == "LIST":
                with tasks_lock:
                    result = format_tasks()

                protocol.send_message(sock, "TEXT", result.encode("utf-8"))

            elif command == "DONE":
                if not text:
                    protocol.send_message(sock, "ERROR", "Ошибка: укажите номер задачи".encode("utf-8"))
                    continue

                try:
                    num = int(text)
                except ValueError:
                    protocol.send_message(sock, "ERROR", "Ошибка: номер задачи должен быть целым числом"
                                          .encode("utf-8"))
                    continue

                with tasks_lock:
                    if not (1 <= num <= len(tasks)):
                        protocol.send_message(sock, "ERROR", f"Ошибка: задачи с номером {num} не существует"
                                              .encode("utf-8"))
                        continue

                    if tasks[num - 1]["done"]:
                        protocol.send_message(sock, "TEXT", f"Задача #{num} уже была выполнена"
                                              .encode("utf-8"))
                        continue

                    tasks[num - 1]["done"] = True

                protocol.send_message(sock, "TEXT", f"Задача #{num} отмечена как выполненная".encode("utf-8"))

            elif command == "QUIT":
                protocol.send_message(sock, "TEXT", "Пока!".encode("utf-8"))
                break

            else:
                protocol.send_message(sock, "ERROR", f"Неизвестная команда: {command}".encode("utf-8"))

    except (ConnectionResetError, BrokenPipeError, OSError) as e:
        print(f"[SERVER] Ошибка связи с {addr}: {e}")
    finally:
        sock.close()
        print(f"[SERVER] Клиент {addr} отключился")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER] Сервер задач запущен")

    try:
        while True:
            client_sock, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Завершение работы")
    finally:
        server.close()


if __name__ == "__main__":
    main()