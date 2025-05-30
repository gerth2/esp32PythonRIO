import machine  # Uncomment this in your MicroPython environment

class VoltageMonitor:
    def __init__(
        self,
        pin: int = 34,
        r1_ohms: float = 10000.0,     # Top resistor (connected to VIN)
        r2_ohms: float = 1000.0,      # Bottom resistor (connected to GND)
        vref: float = 3.3             # ADC reference voltage (ESP32 default)
    ):
        self.r1 = r1_ohms
        self.r2 = r2_ohms
        self.vref = vref

        adc_pin = machine.Pin(pin)
        self.adc = machine.ADC(adc_pin)
        self.adc.atten(machine.ADC.ATTN_11DB)    # Full 0–3.3V input range
        self.adc.width(machine.ADC.WIDTH_12BIT)  # 12-bit resolution (0–4095)

    def read_voltage(self) :
        raw = self.adc.read_uv()
        adc_voltage = (raw / 1000000.0)  # Convert microvolts to volts

        # Reverse the voltage divider:
        vin = adc_voltage * ((self.r1 + self.r2) / self.r2)
        return vin

    def read_voltage_rounded(self, decimals: int = 2) :
        return round(self.read_voltage(), decimals)