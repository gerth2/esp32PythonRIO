import usocket as socket
import uos
import builtins
import sys, json
from robotName import ROBOT_NAME

class WebEditorServer:
    def __init__(self, port=8080):
        self.port = port
        self.locked = False
        self.state = "disabled"
        self.console_log = ""
        self.max_log_size = 5000
        self.fileChanged = False
        self._batVoltage = 9.12

        self._orig_print = builtins.print
        builtins.print = self._tee_print  # Override print

        self._start_server()

    def set_batVoltage(self, voltage):
        self._batVoltage = voltage

    def _tee_print(self, *args, **kwargs):
        text = " ".join(str(arg) for arg in args) + "\n"
        self.console_log += text
        if len(self.console_log) > self.max_log_size:
            self.console_log = self.console_log[-self.max_log_size:]
        self._orig_print(*args, **kwargs)

    def _start_server(self):
        addr = socket.getaddrinfo('0.0.0.0', self.port)[0][-1]
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(addr)
        self.sock.listen(1)
        self.sock.setblocking(False)  # <- non-blocking mode

        print(f"[WebEditor] Listening on port {self.port}")

    def _read_robot_file(self):
        try:
            with open("robot.py", "r") as f:
                return f.read()
        except:
            return ""
        
    def getFileChanged(self):
        retVal = self.fileChanged 
        self.fileChanged = False
        return retVal

    def _write_robot_file(self, data):
        if self.locked:
            return False
        with open("robot.py", "w") as f:
            f.write(data)
            self.fileChanged = True
        return True

    def _guess_content_type(self, path):
        if path.endswith(".html"): return "text/html"
        if path.endswith(".css"): return "text/css"
        if path.endswith(".js"): return "application/javascript"
        return "text/plain"

    def _handle_client(self, conn):
        try:
            request = conn.recv(1024).decode()
            method, path, request_data = request.split(" ", 2)

            #print(f"[WebEditor] Request method: {method}")
            #print(f"[WebEditor] Request path: {path}")
            #print(f"[WebEditor] Request data: {request_data}")


            if path == "/":
                print(f"[WebEditor] Request: Serve Main UI")
                self._serve_file(conn, "/index.html")

            elif path.startswith("/deploy") and method == "POST":
                body = self._get_body(request, conn)
                print(f"[WebEditor] Request: Deploy File")
                self._write_robot_file(body)
                self._send_response(conn, "OK")

            elif path.startswith("/robot.py"):
                print(f"[WebEditor] Request: Load File")
                self._send_response(conn, self._read_robot_file())

            elif path.startswith("/stateCmd"):
                try:
                    # Split headers from body
                    _, _, body = request_data.partition('\r\n\r\n')

                    # Parse JSON body
                    data = json.loads(body)
                    print(f"[WebEditor] Received state data: {data}")
                    self.state = data['state']
                    print(f"[WebEditor] Robot State is now {self.state}")
                    
                    self._send_response(conn, "OK")

                except:
                    print("[WebEditor] Failed to decode JSON in /state")
                    self._send_response(conn, "Error: Invalid JSON", status="400 BAD")

            elif path.startswith("/console"):
                self._send_response(conn, self.console_log[-1000:], "text/plain")

            elif path.startswith("/curState"):
                retDict = {
                    "robotName": ROBOT_NAME,
                    "statusMsg": self.state,
                    "batVoltage": self._batVoltage,
                    "codeRunning": True
                }
                self._send_response(conn,  json.dumps(retDict), "application/json")

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
            self._send_response(conn, "Not found", status="404 Not Found")

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
        except OSError:
            pass  # No connection ready, that's fine
