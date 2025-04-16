import errno
import hashlib
import usocket as socket
import ustruct
import ubinascii
import ujson as json
import time

curWsClient = None

def websocket_handshake(client):
    req = client.recv(1024)
    headers = req.decode().split('\r\n')
    key = ''
    for h in headers:
        if 'Sec-WebSocket-Key' in h:
            key = h.split(': ')[1]
            break

    accept = ubinascii.b2a_base64(
        hashlib.sha1(key.encode() + b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest()
    ).strip().decode()
    
    response = (
        'HTTP/1.1 101 Switching Protocols\r\n'
        'Upgrade: websocket\r\n'
        'Connection: Upgrade\r\n'
        'Sec-WebSocket-Accept: {}\r\n'
        '\r\n'
    ).format(accept)

    client.send(response.encode())

def recv_ws_json(client):
    try:
        hdr = client.recv(2)
        if not hdr or len(hdr) < 2:
            return None

        length = hdr[1] & 0x7F
        if length == 126:
            length = ustruct.unpack('>H', client.recv(2))[0]
        elif length == 127:
            length = ustruct.unpack('>Q', client.recv(8))[0]

        mask = client.recv(4)
        raw = bytearray(client.recv(length))
        for i in range(len(raw)):
            raw[i] ^= mask[i % 4]

        try:
            return json.loads(raw.decode())
        except ValueError as e:
            print("[WSS] JSON decode failed:", str(raw))
            return None
    except OSError as e:
        if e.errno in [errno.ECONNRESET, errno.ETIMEDOUT]:
            print("[WSS] Client disconnected")
            raise  # Re-raise the exception to handle it in the main loop
        return None
    
def send_ws_json(obj):
    if(curWsClient is None):
        return # no client, nothin to send
    
    # We have a client, send actual data
    try:
        data = json.dumps(obj)
        payload = data.encode('utf-8')
        length = len(payload)

        # Build header
        if length <= 125:
            header = bytes([0x81, length])
        elif length <= 65535:
            header = bytes([0x81, 126]) + ustruct.pack('>H', length)
        else:
            header = bytes([0x81, 127]) + ustruct.pack('>Q', length)

        curWsClient.send(header + payload)
    except Exception as e:
        print("[WSS] Failed to send JSON:", e)


def ws_server_update(onDataCallback=None, onDisconnectCallback=None):
    """Handles one iteration of the WebSocket server logic."""
    global curWsClient, server_socket

    try:
        # Accept a new client if no client is connected
        if curWsClient is None:
            server_socket.settimeout(0)  # Non-blocking accept
            try:
                client, addr = server_socket.accept()
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                print("[WSS] Client connected:", addr)
                websocket_handshake(client)
                curWsClient = client
            except OSError:
                pass  # No client connection available, continue

        # Handle data from the connected client
        if curWsClient is not None:
            try:
                obj = recv_ws_json(curWsClient)
                if obj is not None and onDataCallback:
                    onDataCallback(obj)
            except OSError as e:
                print("[WSS] Client error or disconnect:", e)
                if onDisconnectCallback:
                    onDisconnectCallback()
                curWsClient.close()
                curWsClient = None

    except Exception as e:
        print("[WSS] Server error:", e)

def start_ws_server(port=8266, onDataCallback=None, onDisconnectCallback=None):
    """Initializes the WebSocket server."""
    global curWsClient, server_socket
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(1)
    print("[WSS] WebSocket server listening on port", port)
