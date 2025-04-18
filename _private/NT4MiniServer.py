# Minimal NT4-like server in MicroPython for ESP32

import math
import time
import socket
import struct

class NT4MiniServer:
    def __init__(self, port=5810, freq=1.0):
        self.freq = freq
        self.start_time = time.ticks_ms()
        self.last_send = 0
        self.client = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', port))
        self.sock.listen(1)
        self.sock.setblocking(False)
        self.topic_id = 1  # Arbitrary ID
        self.topic_name = "/sine_wave"
        self.topic_type = "double"
        self.topic_announced = False

    def _accept_client(self):
        try:
            self.client, _ = self.sock.accept()
            self.client.setblocking(False)
            self.topic_announced = False
        except OSError:
            pass

    def _get_sine_value(self):
        t_ms = time.ticks_ms() - self.start_time
        t = t_ms / 1000.0
        return math.sin(2 * math.pi * self.freq * t)

    def _read_client(self):
        if not self.client:
            return
        try:
            data = self.client.recv(1024)
            if data:
                # Expecting ClientHello (0x00)
                if data[0] == 0x00:
                    self._send_server_hello()
        except OSError:
            pass

    def _send_server_hello(self):
        if not self.client:
            return
        proto_revision = 0x0400  # NT4 version 4.0
        msg = struct.pack("<B", 0x01)  # ServerHello (msg type 0x01)
        msg += struct.pack("<H", proto_revision)
        msg += struct.pack("<H", 0)  # No flags
        self.client.send(msg)

    def _send_topic_announce(self):
        if not self.client or self.topic_announced:
            return

        msg = struct.pack("<B", 0x10)  # TopicAnnounce
        msg += self._pack_string(self.topic_name)
        msg += self._pack_string(self.topic_type)
        msg += struct.pack("<I", self.topic_id)
        msg += struct.pack("<B", 0)  # No properties
        self.client.send(msg)
        self.topic_announced = True

    def _send_value_update(self):
        if not self.client:
            return
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_send) < 50:
            return

        value = self._get_sine_value()
        msg = struct.pack("<B", 0x14)  # EntryUpdate
        msg += struct.pack("<I", self.topic_id)
        msg += struct.pack("<Q", int(time.time() * 1e6))  # Timestamp (microseconds)
        msg += b"\x01"  # Value type: double
        msg += struct.pack("<d", value)
        try:
            self.client.send(msg)
            self.last_send = now
        except OSError:
            self.client.close()
            self.client = None
            self.topic_announced = False

    def _pack_string(self, s):
        b = s.encode()
        return self._pack_varint(len(b)) + b

    def _pack_varint(self, value):
        # Standard varint (LEB128-style)
        b = bytearray()
        while True:
            byte = value & 0x7F
            value >>= 7
            if value:
                b.append(byte | 0x80)
            else:
                b.append(byte)
                break
        return bytes(b)

    def update(self):
        if not self.client:
            self._accept_client()
        else:
            self._read_client()
            self._send_topic_announce()
            self._send_value_update()
