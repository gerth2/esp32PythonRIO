import socket

class TCPServerManager:
    def __init__(self, port: int = 1740):
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_addr = None
        self.connected = False
        self._start()

    def _start(self) -> None:
        if self.server_socket is not None:
            return  # already started

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(1)
        self.server_socket.setblocking(False)
        print(f"Driver Station TCP server listening on port {self.port}")

    def update(self) -> None:
        if not self.connected:
            try:
                client_sock, client_addr = self.server_socket.accept()
                client_sock.setblocking(False)
                self.client_socket = client_sock
                self.client_addr = client_addr
                self.connected = True
                print(f"✅ Driver Station TCP Client connected from {client_addr}")
            except OSError:
                pass  # No incoming connection

    def send(self, data: bytes) -> bool:
        if self.connected and self.client_socket:
            try:
                self.client_socket.send(data)
                return True
            except OSError as e:
                print("TCP send error:", e)
                self._cleanup()
        return False

    def recv(self, bufsize: int = 1024) -> bytes:
        if self.connected and self.client_socket:
            try:
                return self.client_socket.recv(bufsize)
            except OSError as e:
                if e.args[0] == 11:  # EAGAIN = no data yet (non-blocking)
                    return b""  # No data, not an error
                print("TCP recv error:", e)
                self._cleanup()
        return b""

    def _cleanup(self) -> None:
        print("🔌 Client disconnected")
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        self.client_socket = None
        self.client_addr = None
        self.connected = False

    def stop(self) -> None:
        self._cleanup()
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None

    def is_connected(self) -> bool:
        return self.connected
