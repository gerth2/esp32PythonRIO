import network, socket

MODE_AUTO = 2
MODE_TELEOP = 0
MODE_TEST = 1

class fromDsPacket():
    def __init__(self, bytes):
        self.seqNum = [bytes[0], bytes[1]]
        self.commVer = bytes[2]
        self.estopCmd = bytes[3] & 0x80
        self.enabledCmd = bytes[3] & 0x04
        self.modeCmd = bytes[3] & 0x03

    def __str__(self):
        s = ("Seq" + str(self.seqNum) + " ") + \
            ("ESTOP " if self.estopCmd else "") + \
            ("ENABLE " if self.enabledCmd else "DISABLED ") + \
            ("TELEOP" if self.modeCmd == MODE_TELEOP else "AUTO" if self.modeCmd == MODE_AUTO else "TEST" if self.modeCmd == MODE_TEST else "UNKNOWN")
        return s

class DsInterface():
    def __init__(self):
        self._init_WiFi()
        self._setupTxSocket()
        self._setupRxSocket()
        self.seqNum = 0

    def periodic(self):
        self._readPacket()

    def _readPacket(self):
        """
        https://frcture.readthedocs.io/en/latest/driverstation/ds_to_rio.html
        """
        data = self.rxSocket.recv(512)
        if data:
            # Process the received packet as needed
            packet = fromDsPacket(data)
            print(str(packet))

            # Respond with latest data
            self._sendPeriodicPacket(packet.seqNum)

    def _sendPeriodicPacket(self, seqNum):
        """
        https://frcture.readthedocs.io/en/latest/driverstation/rio_to_ds.html
        """
        packet = bytes([seqNum[0],  # sequence number 0
                        seqNum[1],
                        0x01, # Comm Type
                        0x00, # Status
                        0x31,# Trace
                        0x0C, # Battery Volts (whole number)
                        0x0F, # Battery Volts (fractional number)
                        0x00, # Date request command
                        ]) # No tags yet
        #print("Responding with:", packet)
        self.txSocket.write(packet)
    
    def _init_WiFi(self):
        self.ap = network.WLAN(network.WLAN.IF_AP) # create access-point interface
        self.ap.config(ssid='ESP-1736-ROBOT')      # set the SSID of the access point
        self.ap.config(max_clients=2)              # set how many clients can connect to the network
        self.ap.ipconfig(addr4=("10.17.36.2", "255.255.255.0"))
        self.ap.ipconfig(gw4="10.17.36.1")
        self.ap.active(True)                       # activate the interface

    def _setupTxSocket(self):
        self.txSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.txSocket.connect(("10.17.36.3", 1150))
        self.txSocket.setblocking(True)

    def _setupRxSocket(self):
        self.rxSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rxSocket.bind(("0.0.0.0", 1110))
