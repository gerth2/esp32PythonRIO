import socket, hashlib, binascii, json
import time

class MinimalNT4Server:
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MinimalNT4Server, cls).__new__(cls)
        return cls._instance

    def __init__(self, port=5810):
        if hasattr(self, "_initialized") and self._initialized:
            return  # Avoid reinitialization
        self._initialized = True

        self.port = port
        self.clients = []
        self.last_send_ms = 0
        self.next_topic_id = 1
        self.topics = {}

        self._start_server()

    def _start_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.port))
        self.sock.listen(1)
        self.sock.setblocking(False)

    def _accept_client(self):
        try:
            conn, addr = self.sock.accept()
            print("🔌 New NT4 connection from", addr)
            if self._handshake(conn):
                for name, meta in self.topics.items():
                    self._send_announce(conn, name, meta['id'], meta['type'])
                self.clients.append(conn)
        except OSError:
            pass

    def _handshake(self, conn):
        try:
            request = conn.recv(1024).decode()
            key_line = next(line for line in request.split("\r\n") if "Sec-WebSocket-Key" in line)
            key = key_line.split(": ")[1]
            magic = key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
            sha1 = hashlib.sha1(magic.encode()).digest()
            accept = binascii.b2a_base64(sha1).decode().strip()

            response = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
            )
            conn.send(response.encode())
            conn.setblocking(False)
            return True
        except Exception as e:
            print("⚠️ NT4 Handshake failed:", e)
            return False

    def _send_announce(self, conn, name, topic_id, type_str):
        msg = {
            "type": "announce",
            "name": name,
            "id": topic_id,
            "pubuid": 1,
            "flags": 0,
            "type_str": type_str
        }
        self._send_json(conn, msg)

    def _send_json(self, conn, obj):
        try:
            if conn.fileno() == -1:  # Check if socket is closed
                print(f"⚠️ NT4 Socket {conn} is closed.")
                self.clients.remove(conn)
                conn.close()
                return

            payload = json.dumps(obj).encode()
            frame = b'\x81' + bytes([len(payload)]) + payload
            conn.send(frame)
        except OSError as e:
            print("⚠️ NT4 Send failed:", e)
            if conn in self.clients:
                self.clients.remove(conn)
                conn.close()

    def _check_clients(self):
        for conn in self.clients[:]:
            try:
                data = conn.recv(1024)
                if data and data[0] & 0x0F == 0x8:
                    self.clients.remove(conn)
                    conn.close()
            except OSError:
                pass

    def publish(self, name: str, value):
        type_str = self._infer_type(value)
        if type_str is None:
            print(f"❌ NT4 Unsupported type for topic '{name}': {type(value)}")
            return

        if name not in self.topics:
            topic_id = self.next_topic_id
            self.next_topic_id += 1
            self.topics[name] = {
                "id": topic_id,
                "type": type_str,
                "last_value": None
            }
            for conn in self.clients:
                self._send_announce(conn, name, topic_id, type_str)

        self.topics[name]["last_value"] = value

    def _infer_type(self, value):
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "double"
        return None

    def update(self):
        now = time.ticks_ms()
        self._accept_client()
        self._check_clients()

        if time.ticks_diff(now, self.last_send_ms) >= 100:
            for name, meta in self.topics.items():
                value = meta["last_value"]
                if value is not None:
                    msg = {
                        "type": "value",
                        "id": meta["id"],
                        "value": value
                    }
                    for conn in self.clients[:]:
                        self._send_json(conn, msg)
            self.last_send_ms = now


# 🔁 Global accessor
_nt4_instance = None

def get_nt4_server():
    global _nt4_instance
    if _nt4_instance is None:
        _nt4_instance = MinimalNT4Server()
    return _nt4_instance
