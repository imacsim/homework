import struct
import socket

MAX_MESSAGE_SIZE = 10 * 1024 * 1024


def recv_exact(sock: socket.socket, size: int) -> bytes:
    if size < 0:
        raise ValueError("size не может быть отрицательным")

    data = bytearray()

    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Соединение закрыто до получения всех данных")
        data.extend(chunk)

    return bytes(data)


def send_message(sock: socket.socket, command: str, payload: bytes) -> None:
    cmd_bytes = command.encode("utf-8")
    header = struct.pack("!I", len(cmd_bytes)) + cmd_bytes + struct.pack("!I", len(payload))
    sock.sendall(header + payload)


def recv_message(sock: socket.socket):
    try:
        length_data = recv_exact(sock, 4)
        cmd_len = struct.unpack("!I", length_data)[0]
        cmd_bytes = recv_exact(sock, cmd_len)
        command = cmd_bytes.decode("utf-8")

        length_data = recv_exact(sock, 4)
        payload_len = struct.unpack("!I", length_data)[0]

        if payload_len > MAX_MESSAGE_SIZE:
            raise ValueError(f"Слишком большое сообщение: {payload_len}")

        payload = recv_exact(sock, payload_len) if payload_len > 0 else b""

        return command, payload

    except (ConnectionError, ConnectionResetError, BrokenPipeError, struct.error):
        return None