import socket
import struct
import time

class MinimalNT3Server:
    def __init__(self, host="0.0.0.0", port=5800):
        self.host = host
        self.port = port
        self.socket = None
        self.client_socket = None
        self.client_address = None
        self.start_server()

    def start_server(self):
        """Start the NT3 server, listen for connections, and handle incoming clients."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        print(f"NT3 Server started on {self.host}:{self.port}")
        
    def update(self):
            if(self.socket is not None):
                self.client_socket, self.client_address = self.socket.accept()
                print(f"New connection from {self.client_address}")
                # Handshake with the client (optional)
                self._send_handshake()


    def _send_handshake(self):
        """Send a simple handshake message to the client."""
        handshake_msg = struct.pack("!B", 0x01)  # Simple handshake (just a byte)        
        if(self.client_socket is not None):
            self.client_socket.send(handshake_msg)

    def send_data(self, name, value):
        """Send a simple data message (float, int, or boolean) to the client."""
        if isinstance(value, float):
            message = struct.pack("!B", 0x02)  # Data type indicator
            message += struct.pack("!I", len(name))  # Length of the name
            message += name.encode("utf-8")  # Name
            message += struct.pack("!d", value)  # Double value
        elif isinstance(value, int):
            message = struct.pack("!B", 0x03)  # Data type indicator
            message += struct.pack("!I", len(name))  # Length of the name
            message += name.encode("utf-8")  # Name
            message += struct.pack("!I", value)  # Integer value
        elif isinstance(value, bool):
            message = struct.pack("!B", 0x04)  # Data type indicator
            message += struct.pack("!I", len(name))  # Length of the name
            message += name.encode("utf-8")  # Name
            message += struct.pack("!B", value)  # Boolean value

        if(self.client_socket is not None):
            self.client_socket.send(message)

