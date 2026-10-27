import json
import socket
import struct
import sys
from queue import Queue

from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


HOST = "127.0.0.1"
PORT = 50505


class NetCom:
    def __init__(self, sock):
        self.sock = sock

    @staticmethod
    def _recv_exact(sock, size):
        chunks = []
        received = 0
        while received < size:
            chunk = sock.recv(size - received)
            if not chunk:
                return None
            chunks.append(chunk)
            received += len(chunk)
        return b"".join(chunks)

    def recv(self):
        header = self._recv_exact(self.sock, 4)
        if header is None:
            return None

        payload_size = struct.unpack("!I", header)[0]
        payload = self._recv_exact(self.sock, payload_size)
        if payload is None:
            return None

        return json.loads(payload.decode("utf-8"))

    def send(self, message):
        payload = json.dumps(message, ensure_ascii=False).encode("utf-8")
        header = struct.pack("!I", len(payload))
        self.sock.sendall(header + payload)


class ReceiveThread(QThread):
    message_received = pyqtSignal(dict)

    disconnected = pyqtSignal(str)

    def __init__(self, net):
        super().__init__()
        self.net = net

    def run(self):
        try:
            while True:
                message = self.net.recv()
                if message is None:
                    self.disconnected.emit("Сервер закрыл соединение")
                    break
                self.message_received.emit(message)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError, struct.error) as exc:
            self.disconnected.emit(f"Ошибка при получении данных: {exc}")


class SendThread(QThread):
    send_error = pyqtSignal(str)

    def __init__(self, net):
        super().__init__()
        self.net = net
        self.queue = Queue()

    def send(self, message):
        self.queue.put(message)

    def stop(self):
        self.queue.put(None)

    def run(self):
        while True:
            message = self.queue.get()
            if message is None:
                break

            try:
                self.net.send(message)
            except OSError as exc:
                self.send_error.emit(f"Ошибка при отправке данных: {exc}")
                break


class MainWindow(QMainWindow):
    def __init__(self, net):
        super().__init__()
        self.net = net

        self._connected = True
        self._closing = False

        self.setWindowTitle("PyQt6 network chat")
        self.resize(560, 420)

        self.history = QTextEdit()
        self.history.setReadOnly(True)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите имя")

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message…")

        self.send_button = QPushButton("Send")
        self.status_label = QLabel("Connected to 127.0.0.1:50505")

        username_row = QHBoxLayout()
        username_row.addWidget(QLabel("Имя:"))
        username_row.addWidget(self.username_input)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input)
        input_row.addWidget(self.send_button)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addLayout(username_row)
        layout.addWidget(self.history)
        layout.addLayout(input_row)

        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)

        self.send_button.clicked.connect(self.on_send_clicked)
        self.input.returnPressed.connect(self.on_send_clicked)

        self.receive_thread = ReceiveThread(self.net)
        self.receive_thread.message_received.connect(self.handle_message)
        self.receive_thread.disconnected.connect(self.handle_disconnect)
        self.receive_thread.start()

        self.send_thread = SendThread(self.net)
        self.send_thread.send_error.connect(self.handle_disconnect)
        self.send_thread.start()

    def on_send_clicked(self):
        if not self._connected:
            return

        text = self.input.text().strip()
        if not text:
            return

        username = self.username_input.text().strip() or "Гость"
        self.send_thread.send({
            "type": "chat",
            "username": username,
            "text": text,
        })
        self.input.clear()

    def handle_message(self, message):
        message_type = message.get("type")

        if message_type == "chat":
            username = message.get("username", "Гость")
            text = message.get("text", "")
            self.history.append(f"{username}: {text}")
        elif message_type == "system":
            text = message.get("text", "")
            self.history.append(f"[Система] {text}")

    def handle_disconnect(self, reason):
        if self._closing or not self._connected:
            return

        self._connected = False
        self.status_label.setText("Соединение потеряно")
        self.history.append(f"[Система] Соединение потеряно: {reason}")
        self.send_button.setEnabled(False)
        self.input.setEnabled(False)

        self.send_thread.stop()
        self._shutdown_socket()

    def _shutdown_socket(self):
        try:
            self.net.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    def closeEvent(self, event):
        self._closing = True
        self._connected = False

        self.send_thread.stop()
        self._shutdown_socket()

        self.send_thread.wait()
        self.receive_thread.wait()

        self.net.sock.close()
        event.accept()


def main():
    app = QApplication(sys.argv)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except OSError as exc:
        print(f"Could not connect to server at {HOST}:{PORT}: {exc}")
        print("Run server.py first, then start main.py.")
        sock.close()
        return

    net = NetCom(sock)
    window = MainWindow(net)
    window.show()

    exit_code = app.exec()
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()