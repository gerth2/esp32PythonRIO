import socket
import struct
import network

def inet_aton(ip: str) -> bytes:
    return bytes(int(part) for part in ip.split('.'))


class RobotMDNS:
    MDNS_ADDR = "224.0.0.251"
    MDNS_PORT = 5353
    HOSTNAME = "robot.local"

    def __init__(self):
        self.ip = self._get_ip()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.MDNS_ADDR, self.MDNS_PORT))

        # Join mDNS multicast group
        mreq = inet_aton(self.MDNS_ADDR) + b'\x00\x00\x00\x00'
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


    def _get_ip(self) -> str:
        sta_if = network.WLAN(network.STA_IF)
        return sta_if.ifconfig()[0]

    def update(self):
        try:
            data, addr = self.sock.recvfrom(512)
            if self.HOSTNAME.encode() in data:
                self._send_response(addr)
        except OSError:
            # Nothing to do
            pass

    def _send_response(self, addr):
        # Build a very basic mDNS response (just enough for robot.local)
        name = b'\x05robot\x05local\x00'  # robot.local in DNS format
        reply = (
            b'\x00\x00\x84\x00'     # response flags
            b'\x00\x00\x00\x01'     # no questions, 1 answer
            b'\x00\x00\x00\x00'     # no authority, no additional
            + name +
            b'\x00\x01'             # type A
            b'\x00\x01'             # class IN
            b'\x00\x00\x00\x3C'     # TTL = 60
            b'\x00\x04'             # RDLENGTH = 4
            + socket.inet_aton(self.ip)
        )

        self.sock.sendto(reply, (self.MDNS_ADDR, self.MDNS_PORT))
