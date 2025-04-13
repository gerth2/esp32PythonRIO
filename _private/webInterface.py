import time
import _thread
from _private.wss import send_ws_json, start_ws_server
import usocket as socket
import uos
import builtins
import json
from robotName import ROBOT_NAME

class WebInterfaceServer:
    def __init__(self, port=8080):
        self.port = port
        self.locked = False
        self.state = "disabled"
        self.console_log = ""
        self.max_log_size = 5000
        self._fileChanged = False
        self._batVoltage = 9.12
        self._codeRunning = False
        self.keyStates = 0x00

        self._orig_print = builtins.print
        builtins.print = self._tee_print  # Override print

        self._start_server()
        _thread.start_new_thread(self._server_loop, ())

        # Start a websockets server too in the background
        _thread.start_new_thread(start_ws_server, (8266, self.onWsData, self.onWsDisconnect))

        # Periodic data send for websockets
        _thread.start_new_thread(self.wsSendLoop, ())

    def _getStatusMessage(self):
        if self.state == "disabled":
            return "Disabled"
        elif self.state == "teleop":
            return "Teleop Enabled"
        elif self.state == "auto":
            return "Autonomous Enabled"

    def wsSendLoop(self):
        while True:
            sendJson = {
                "robotState": {
                    "robotName": ROBOT_NAME,
                    "batVoltage": self._batVoltage,
                    "codeRunning": self._codeRunning,
                    "keyStates": self.keyStates,
                    "statusMsg": self._getStatusMessage()
                }
            }

            if(len(self.console_log) > 0):
                sendJson["consoleOutput"]  = self.console_log
                self.console_log = "" #reset

            send_ws_json(sendJson)

            time.sleep_ms(300)


    def onWsDisconnect(self):
        # Safety - go to disabled with no input command on client disconnect
        self.state = "disabled"
        self.keyStates = 0x00


    def onWsData(self, data):
        # Switchyard for any incoming websocket data from the server
        if "keyboardData" in data:
            self.keyStates = data["keyboardData"]

        if "stateCmd" in data:
            self.state = data["stateCmd"]

    def set_batVoltage(self, voltage):
        self._batVoltage = voltage

    def set_codeRunning(self, running):
        self._codeRunning = running

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
        retVal = self._fileChanged 
        self._fileChanged = False
        return retVal

    def _write_robot_file(self, data):
        if self.locked:
            return False
        with open("robot.py", "w") as f:
            f.write(data)
            self._fileChanged = True
        return True

    def _guess_content_type(self, path):
        if path.endswith(".html"): return "text/html"
        if path.endswith(".css"): return "text/css"
        if path.endswith(".js"): return "application/javascript"
        return "text/plain"

    def _handle_client(self, conn):
        try:
            request = conn.recv(1024).decode()
            method, path, _ = request.split(" ", 2)

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

    def _server_loop(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                continue # No connection ready, that's fine  

            self._handle_client(conn)
