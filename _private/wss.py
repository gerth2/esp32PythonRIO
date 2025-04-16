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
        if e.errno in [errno.ECONNRESET, errno.EPIPE, errno.ETIMEDOUT]:
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


def start_ws_server(port=8266, onDataCallback=None, onDisconnectCallback=None):
    global curWsClient
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', port))
    s.listen(1)
    print("[WSS] WebSocket server listening on port", port)

    while True:
        try:
            client, addr = s.accept()
            #client.setblocking(False)
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            print("[WSS] Client connected:", addr)
            websocket_handshake(client)

            while True:
                curWsClient = client
                obj = recv_ws_json(client)
                if obj is not None:
                    if onDataCallback:
                        onDataCallback(obj)
                time.sleep_ms(2)

        except Exception as e:
            print("[WSS] Client error or disconnect:", e)

        try:
            curWsClient = None
            client.close()
        except:
            pass
        print("[WSS] Client disconnected")
        if onDisconnectCallback:
            onDisconnectCallback()
