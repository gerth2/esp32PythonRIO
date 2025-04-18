import time
from _private.HAL import HAL
from _private.mdns import RobotMDNS
from _private.wss import send_ws_json, start_ws_server, ws_server_update
import usocket as socket
import uos
import builtins
from robotName import get_robot_name
#from _private.NT4MiniServer import NT4MiniServer

class WebInterfaceServer:
    def __init__(self, port=80):
        self.port = port
        self.locked = False
        self.state = "disabled"
        self.console_log = ""
        self.max_log_size = 5000
        self._fileChanged = False
        self._batVoltage = 9.12
        self._codeRunning = False
        self.keyStates = 0x00

        self._wsSendCounter = 0

        self._sendPlotData = False

        #self.nt4mini = NT4MiniServer(port=5810, freq=1.0)  # Initialize NT4 Mini server

        self._orig_print = builtins.print
        builtins.print = self._tee_print  # Override print

        self._start_server()
        start_ws_server()
        #self._mdns = RobotMDNS()

    def _getStatusMessage(self):
        if self.state == "disabled":
            return "Disabled"
        elif self.state == "teleop":
            return "Teleop Enabled"
        elif self.state == "auto":
            return "Autonomous Enabled"


    def _wsSendPeriodic(self):

        sendJson = {}

        # Handle stdout
        if(self._wsSendCounter % 4 == 0):
            if(len(self.console_log) > 0):
                sendJson["consoleOutput"]  = self.console_log
                self.console_log = "" #reset
        
        # Handle periodic state
        if(self._wsSendCounter % 10 == 0):
            sendJson = {
                "robotState": {
                    "batVoltage": self._batVoltage,
                    "codeRunning": self._codeRunning,
                    "statusMsg": self._getStatusMessage()
                }
            }

        # Handle configuration - very slow update
        if(self._wsSendCounter % 50 == 0):
            sendJson = {
                "robotConfig": {
                    "robotName": get_robot_name(),
                }
            }

        if(self._sendPlotData):
            sendJson["plotData"] = {
                "TIME": time.ticks_ms()/1000.0,
                "batVoltage": self._batVoltage,
                "codeRunning": self._codeRunning,
                "gyroAngle": HAL.gyro.get_angle(),
            }

        if(len(sendJson) > 0):
            #print(f"[WebInf] Sending JSON {sendJson}")
            send_ws_json(sendJson)

        self._wsSendCounter +=1 
        if(self._wsSendCounter >= 100):
            self._wsSendCounter = 0 # wrap every 100 loops


    def onWsDisconnect(self):
        # Safety - go to disabled with no input command on client disconnect
        self.state = "disabled"
        self.keyStates = 0x00
        # Utility - stop sending plot data
        self._sendPlotData = False

    def onWsData(self, data):
        # Switchyard for any incoming websocket data from the server
        if "keyboardData" in data:
            self.keyStates = data["keyboardData"]

        if "stateCmd" in data:
            self.state = data["stateCmd"]

        if "plotConfig" in data:
            self._sendPlotData = data["plotConfig"]["enabled"]
            print("[WebEditor] Plots Enabled: ", self._sendPlotData)


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
    
    def _reset_robot_file(self):
        if self.locked:
            return False
        with open("robot.py", "w") as fout:
            with open("robot.py_default", "r") as fin:
                fout.write(fin.read())
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

            elif path.startswith("/resetFile") and method == "POST":
                print(f"[WebEditor] Request: Reset Robot File")
                self._reset_robot_file()
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

    def update(self):
        self._serverUpdate()
        ws_server_update(self.onWsData, self.onWsDisconnect)
        self._wsSendPeriodic()
        #self._mdns.update()
        #self.nt4mini.update()


    def _serverUpdate(self):
        try:
            conn, _ = self.sock.accept()
        except OSError:
            return # No connection ready, that's fine  

        self._handle_client(conn)
