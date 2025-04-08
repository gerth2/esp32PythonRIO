# web_editor.py
import usocket as socket
import uos

class WebEditorServer:
    def __init__(self, port=8080):
        self.port = port
        self.locked = False
        self.state = "stopped"  # "running" or "stopped"
        self._start_server()

    def _start_server(self):
        addr = socket.getaddrinfo('0.0.0.0', self.port)[0][-1]
        self.sock = socket.socket()
        self.sock.bind(addr)
        self.sock.listen(1)
        print(f"[WebEditor] Listening on port {self.port}")

    def _read_robot_file(self):
        try:
            with open("robot.py", "r") as f:
                return f.read()
        except:
            return ""

    def _write_robot_file(self, data):
        if self.locked:
            return False
        with open("robot.py", "w") as f:
            f.write(data)
        return True

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def get_state(self):
        return self.state

    def _guess_content_type(self, path):
        if path.endswith(".html"):
            return "text/html"
        if path.endswith(".css"):
            return "text/css"
        if path.endswith(".js"):
            return "application/javascript"
        return "text/plain"

    def _handle_client(self, conn):
        try:
            request = conn.recv(1024).decode()
            method, path, *_ = request.split(" ", 2)
            print(f"[WebEditor] Request: {method} {path}")

            if path == "/":
                self._serve_file(conn, "/index.html")

            elif path.startswith("/save") and method == "POST":
                body = self._get_body(request, conn)
                if self._write_robot_file(body):
                    self._send_response(conn, "OK", "text/plain")
                else:
                    self._send_response(conn, "LOCKED", "text/plain")

            elif path.startswith("/run") and method == "POST":
                body = self._get_body(request, conn)
                if self._write_robot_file(body):
                    self.state = "running"
                    self._send_response(conn, "RUNNING", "text/plain")
                else:
                    self._send_response(conn, "LOCKED", "text/plain")

            elif path.startswith("/stop") and method == "POST":
                self.state = "stopped"
                self._send_response(conn, "STOPPED", "text/plain")

            elif path.startswith("/robot.py"):
                self._send_response(conn, self._read_robot_file(), "text/plain")

            else:
                self._serve_file(conn, path)

        except Exception as e:
            print(f"[WebEditor] Error: {e}")
        finally:
            conn.close()

    def _serve_file(self, conn, path):
        try:
            if ".." in path:
                raise Exception("Invalid path")
            filepath = "www" + path
            with open(filepath, "r") as f:
                content = f.read()
            content_type = self._guess_content_type(filepath)
            self._send_response(conn, content, content_type)
        except:
            self._send_response(conn, "Not found", "text/plain", status="404 Not Found")

    def _get_body(self, request, conn):
        length = 0
        for line in request.split("\r\n"):
            if line.lower().startswith("content-length:"):
                length = int(line.split(":")[1].strip())
        body = request.split("\r\n\r\n", 1)[-1]
        while len(body) < length:
            body += conn.recv(1024).decode()
        return body

    def _send_response(self, conn, content, content_type="text/plain", status="200 OK"):
        conn.send(f"HTTP/1.1 {status}\r\n")
        conn.send(f"Content-Type: {content_type}\r\n")
        conn.send("Connection: close\r\n\r\n")
        if isinstance(content, str):
            conn.send(content)

    def update(self):
        try:
            conn, _ = self.sock.accept()
            self._handle_client(conn)
        except:
            pass
