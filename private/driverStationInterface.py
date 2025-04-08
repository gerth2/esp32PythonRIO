import network, socket, time
import struct, io
from private.TCPServerManager import TCPServerManager
from private.ESP32Stats import ESP32SystemStats


DS_MODE_AUTO = 2
DS_MODE_TELEOP = 0
DS_MODE_TEST = 1

class FromDsUDPPacket:
    def __init__(self, data: bytes):
        if len(data) < 6:
            raise ValueError("Packet too short")
        
        #print("INBytes:", str(data))

        self.seqNum = (data[0] << 8) | data[1]
        self.commVer = data[2]

        control = data[3]
        self.estop = bool(control & 0x80)
        self.fms_connected = bool(control & 0x08)
        self.enabled = bool(control & 0x04)
        self.mode = control & 0x03

        request = data[4]
        self.reboot = bool(request & 0x08)
        self.restart_code = bool(request & 0x04)

        alliance = data[5]
        self.alliance_color = 'Red' if alliance < 3 else 'Blue'
        self.alliance_position = (alliance % 3) + 1

        # Parse tags
        self.tags = {}
        i = 6
        while i < len(data):
            size = data[i]
            tag_id = data[i + 1]
            tag_data = data[i + 2:i + 1 + size]
            self.tags[tag_id] = self.parse_tag(tag_id, tag_data)
            i += 1 + size

    def parse_tag(self, tag_id: int, data: bytes):
        if tag_id == 0x07:  # Countdown
            return struct.unpack(">f", data[:4])[0]

        elif tag_id == 0x0C:  # Joystick
            ptr = 0
            axis_count = data[ptr]
            ptr += 1
            axes = list(struct.unpack(f"{axis_count}b", data[ptr:ptr + axis_count]))
            ptr += axis_count

            button_count = data[ptr]
            ptr += 1
            button_byte_count = (button_count + 7) // 8
            button_bytes = data[ptr:ptr + button_byte_count]
            buttons = []
            for bit_index in range(button_count):
                byte = button_bytes[bit_index // 8]
                bit = (byte >> (bit_index % 8)) & 1
                buttons.append(bool(bit))
            ptr += button_byte_count

            pov_count = data[ptr]
            ptr += 1
            povs = []
            for _ in range(pov_count):
                pov = struct.unpack(">h", data[ptr:ptr + 2])[0]
                povs.append(pov)
                ptr += 2

            return {
                'axes': axes,
                'buttons': buttons,
                'povs': povs
            }

        elif tag_id == 0x0F:  # Date
            if len(data) < 11:
                return None
            micros = struct.unpack(">I", data[0:4])[0]
            sec, minute, hour, day, month, year = struct.unpack("6B", data[4:10])
            return {
                'utc': f"{1900 + year}-{month + 1:02}-{day:02} {hour:02}:{minute:02}:{sec:02}",
                'microseconds': micros
            }

        elif tag_id == 0x10:  # Timezone
            return data.decode('utf-8', errors='ignore')

        else:
            return data  # Unknown tag, just return raw

    def __str__(self):
        mode_str = {
            DS_MODE_TELEOP: "TELEOP",
            DS_MODE_TEST: "TEST",
            DS_MODE_AUTO: "AUTO"
        }.get(self.mode, "UNKNOWN")

        s = f"Seq:{self.seqNum} CommVer:{self.commVer} "
        s += f"{'ESTOP ' if self.estop else ''}"
        s += f"{'ENABLED ' if self.enabled else 'DISABLED '}"
        s += f"Mode:{mode_str} "
        s += f"{'FMS ' if self.fms_connected else ''}"
        s += f"{'REBOOT ' if self.reboot else ''}"
        s += f"{'RESTART_CODE ' if self.restart_code else ''}"
        s += f"{self.alliance_color}{self.alliance_position} "

        # Add tag info
        if self.tags:
            s += "Tags: ["
            for tag_id, val in self.tags.items():
                s += f"{hex(tag_id)}: {val}, "
            s = s.rstrip(", ") + "]"

        return s


class ToDsUDPPacket:
    def __init__(self, sequence_number: int = 0, comm_version: int = 0x01, status: int = 0, trace: int = 0,
                 battery_voltage: float = 12.0, request_date: bool = False):
        self.sequence_number = sequence_number
        self.comm_version = comm_version
        self.status = status
        self.trace = trace
        self.battery_voltage = battery_voltage
        self.request_date = request_date
        self.tags = []

    def add_tag(self, tag_id: int, tag_data: bytes):
        tag_length = len(tag_data) + 1  # +1 for ID
        self.tags.append(struct.pack("BB", tag_length, tag_id) + tag_data)

    def add_joystick_output(self, outputs: int, left_rumble: int, right_rumble: int):
        tag_id = 0x01
        data = struct.pack("<IHH", outputs, left_rumble, right_rumble)
        self.add_tag(tag_id, data)

    def add_disk_info(self, free_space_bytes: int):
        tag_id = 0x04
        data = struct.pack("<I", free_space_bytes)
        self.add_tag(tag_id, data)

    def add_cpu_info(self, load_pct: float):
        tag_id = 0x05
        num_cpus = 1.0
        critical = load_pct
        above_normal = 0.0
        normal = 0.0
        low = 100.0 - load_pct
        data = struct.pack("<fffff", num_cpus, critical, above_normal, normal, low)
        self.add_tag(tag_id, data)

    def add_ram_info(self, block_size: int, free_space: int):
        tag_id = 0x06
        data = struct.pack("<II", block_size, free_space)
        self.add_tag(tag_id, data)

    def add_can_metrics(self, utilization: float, bus_off: int, tx_full: int, rx_errors: int, tx_errors: int):
        tag_id = 0x0e
        data = struct.pack("<fIIBB", utilization, bus_off, tx_full, rx_errors, tx_errors)
        self.add_tag(tag_id, data)

    def set_status(self, e_stop: bool, brownout: bool, code_start: bool, enabled: bool, mode: int):
        self.status = (
            (0x80 if e_stop else 0) |
            (0x10 if brownout else 0) |
            (0x08 if code_start else 0) |
            (0x04 if enabled else 0) |
            (mode & 0x03)
        )

    def set_trace(self, robot_code: bool, is_roborio: bool, test_mode: bool,
                  autonomous_mode: bool, teleop_mode: bool, disabled: bool):
        self.trace = (
            (0x20 if robot_code else 0) |
            (0x10 if is_roborio else 0) |
            (0x08 if test_mode else 0) |
            (0x04 if autonomous_mode else 0) |
            (0x02 if teleop_mode else 0) |
            (0x01 if disabled else 0)
        )

    def __str__(self):
        # Convert status and trace to their respective components
        e_stop = 'ESTOP ' if self.status & 0x80 else ''
        brownout = 'BROWNOUT ' if self.status & 0x10 else ''
        code_start = 'CODE_START ' if self.status & 0x08 else ''
        enabled = 'ENABLED ' if self.status & 0x04 else 'DISABLED '
        mode_str = {0: 'TELEOP', 1: 'TEST', 2: 'AUTONOMOUS'}.get(self.status & 0x03, 'UNKNOWN')

        robot_code = 'ROBOT_CODE ' if self.trace & 0x20 else ''
        is_roborio = 'IS_ROBORIO ' if self.trace & 0x10 else ''
        test_mode = 'TEST_MODE ' if self.trace & 0x08 else ''
        autonomous_mode = 'AUTONOMOUS_MODE ' if self.trace & 0x04 else ''
        teleop_mode = 'TELEOP_MODE ' if self.trace & 0x02 else ''
        disabled_trace = 'DISABLED_TRACE ' if self.trace & 0x01 else ''

        # Building the string
        s = f"Seq:{self.sequence_number} CommVer:{self.comm_version} "
        s += f"{e_stop}{brownout}{code_start}{enabled}Mode:{mode_str} "
        s += f"{robot_code}{is_roborio}{test_mode}{autonomous_mode}{teleop_mode}{disabled_trace} "
        s += f"BatteryVoltage:{self.battery_voltage} RequestDate:{'Yes' if self.request_date else 'No'} "
        s += f"Tags:{len(self.tags)}"

        return s
    
    def to_bytes(self) -> bytes:
        # Battery as two bytes: XXYY, Voltage = XX + YY / 256
        voltage_whole = int(self.battery_voltage)
        voltage_fraction = int((self.battery_voltage - voltage_whole) * 256)
        battery_bytes = struct.pack("BB", voltage_whole, voltage_fraction)

        packet = struct.pack(">HBBB", self.sequence_number, self.comm_version, self.status, self.trace)
        packet += battery_bytes
        packet += struct.pack("B", 0x01 if self.request_date else 0x00)

        for tag in self.tags:
            packet += tag

        #print("OUTBytes:", str(packet))

        return packet

class ToDSTCPPacket:
    def __init__(self):
        self.size = 0  # Will be calculated later
        self.id = 0  # Placeholder for ID (to be set based on the tag)
        self.tags = []

    def add_disable_faults(self, comms, v12):
        # Disable Faults tag: comms (2 bytes), v12 (2 bytes)
        self.tags.append({
            'id': 0x04,  # Disable Faults tag ID
            'data': struct.pack('!HH', comms, v12)
        })

    def add_rail_faults(self, v6, v5, v3_3):
        # Rail Faults tag: v6, v5, v3.3 (all 2 bytes each)
        self.tags.append({
            'id': 0x05,  # Rail Faults tag ID
            'data': struct.pack('!HHH', v6, v5, v3_3)
        })

    def add_version_info(self, device_type, can_id, name, version):
        # Version Info tag
        self.tags.append({
            'id': 0x0A,  # Version Info tag ID
            'data': struct.pack('!B', device_type) + bytes([0x00,0x00]) + struct.pack('!B', can_id) +
                   b'x0f' + name.encode('utf-8') +
                   b'x0f' + version.encode('utf-8') + b'x000000000000'
        })

    def add_standard_output(self, timestamp, seq_num, message):
        # Standard Output tag: timestamp (4 bytes), seq_num (2 bytes), message (variable length)
        self.tags.append({
            'id': 0x0C,  # Standard Output tag ID
            'data': struct.pack('!f', timestamp) + struct.pack('!H', seq_num) + message.encode('utf-8')
        })

    def to_bytes(self):
        """Convert the packet to bytes, including Size and ID fields."""
        packet_data = io.BytesIO()

        for tag in self.tags:
            tag_id = tag['id']
            tag_data = tag['data']
            tag_size = len(tag_data)

            # Add Size (2 bytes, including ID)
            size = 3 + tag_size  # 1 byte for ID + size of data
            packet_data.write(struct.pack('!H', size))
            packet_data.write(struct.pack('!B', tag_id))
            packet_data.write(tag_data)

        return packet_data.getvalue()





class DsInterface():
    def __init__(self):
        self.seqNum = 0
        self._modeCmd = DS_MODE_TELEOP
        self._enabledCmd = False
        self._codeRunning = False
        self._dsAddr = None
        self._txUDPSocket = None
        self._rxUDPSocket = None
        self._tcpMgr = None
        self._stats = ESP32SystemStats()
        self._stdoutSeqNum = 0

        self._init_WiFi()
        self._setupUDPRxSocket()

    def periodic(self):
        self._readPacket()

    def setCodeRunning(self, codeRunning):
        self._codeRunning = codeRunning

    def getModeCmd(self):
        return self._modeCmd

    def getEnabledCmd(self):
        return self._enabledCmd

    def _readPacket(self):
        """
        https://frcture.readthedocs.io/en/latest/driverstation/ds_to_rio.html
        """

        # UDP Data First
        data, addr = self._rxUDPSocket.recvfrom(512)

        if addr != self._dsAddr:
            self._dsAddr = addr
            print("New DS Connected:", addr)
            self._setupUDPTxSocket()
            self._setupTCPSocket()

        if data:
            # Process the received packet as needed
            packet = FromDsUDPPacket(data)
            #print(str(packet))

            # Pull out relevant packet data
            self._enabledCmd = packet.enabled
            self._modeCmd = packet.mode

            # TODO - joystick?

            # Respond with latest data
            self._sendPeriodicPacket(packet.seqNum)

        # Now TCP Data
        if(self._tcpMgr is not None):
            self._tcpMgr.update()

            if self._tcpMgr.is_connected():
                data = self._tcpMgr.recv()
                if data:
                    dataPkt = ToDSTCPPacket()
                    dataPkt.add_version_info(0, 0, "robot", "1.0")
                    self._tcpMgr.send(dataPkt.to_bytes())

    def _sendPeriodicPacket(self, seqNum):
        """
        https://frcture.readthedocs.io/en/latest/driverstation/rio_to_ds.html
        """
        packet = ToDsUDPPacket(seqNum, 0x01, 0x00, 0x00, 12.0, False)

        packet.add_cpu_info(100.0)
        packet.add_ram_info(1024, self._stats.get_free_heap())
        packet.add_disk_info(self._stats.get_free_program_space())
        
        packet.set_status(False, False, not self._codeRunning, self._enabledCmd, self._modeCmd)
        packet.set_trace(self._codeRunning, True, self._modeCmd==DS_MODE_TEST, self._modeCmd==DS_MODE_AUTO, self._modeCmd==DS_MODE_TELEOP, not self._enabledCmd)
        #print(str(packet))
        self._txUDPSocket.write(packet.to_bytes())
        #print("===========")
    
    def _init_WiFi(self):
        self.ap = network.WLAN(network.WLAN.IF_AP) # create access-point interface
        self.ap.config(ssid='ESP-1736-ROBOT')      # set the SSID of the access point
        self.ap.config(max_clients=2)              # set how many clients can connect to the network
        self.ap.ipconfig(addr4=("10.17.36.2", "255.255.255.0"))
        self.ap.ipconfig(gw4="10.17.36.1")
        self.ap.active(True)                       # activate the interface

    def _setupUDPTxSocket(self):
        self._txUDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._txUDPSocket.connect((self._dsAddr[0], 1150)) # TODO - hardcoded ds address? blech
        self._txUDPSocket.setblocking(False)

    def _setupUDPRxSocket(self):
        self._rxUDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._rxUDPSocket.bind(("0.0.0.0", 1110))

    def _setupTCPSocket(self):
        self._tcpMgr = TCPServerManager(1740)