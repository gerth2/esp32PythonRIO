# AS5600.py
from machine import Pin, I2C
from time import ticks_ms, ticks_diff
import math

class AS5600Encoder:
    AS5600_ADDR = 0x36
    RAW_ANGLE_REGISTER = 0x0C
    STATUS_REGISTER = 0x1B
    MAGNET_FAULT_MASK = 0x01

    def __init__(self, i2c_bus):
        self.i2c = i2c_bus
        self.last_time = self._now()
        self.last_angle = 0.0
        self.last_angle = self.read_abs_position()
        self.accum_angle = 0.0

        # Force zero hysterisis
        self.i2c.writeto_mem(self.AS5600_ADDR, 0x1E, b'\x00')
        # Turn off filtering as much as possible
        self.i2c.writeto_mem(self.AS5600_ADDR, 0x1F, b'\x00')

    def _now(self):
        return ticks_ms()

    def _ticks_diff(self, new, old):
        return ticks_diff(new, old)
    
    def reset(self):
        self.accum_angle = 0.0
    
    def magnet_faulted(self):
        """Checks if the magnet is faulted."""
        try:
            data = self.i2c.readfrom_mem(self.AS5600_ADDR, self.STATUS_REGISTER, 1)
            return (data[0] & self.MAGNET_FAULT_MASK) != 0
        except Exception as e:
            print("[AS5600] read error:", e)
            return False

    def read_abs_position(self) :
        """Reads the raw angle from the AS5600 and returns it in radians."""
        try:
            data = self.i2c.readfrom_mem(self.AS5600_ADDR, self.RAW_ANGLE_REGISTER, 2)
            raw_angle = (data[0] << 8) | data[1]
            angle_rad = (raw_angle / 4096) * 2 * math.pi
            return angle_rad
        except Exception as e:
            print("[AS5600] read error:", e)
            return self.last_angle  # fallback to last known angle
        
    def update(self):
        """
        This encoder is an absolute encoder, and we want to keep track of total rotations
        We'll assume it doesn't rotate too fast and accumulate angle deltas
        """
        now = self._now()
        current_angle = self.read_abs_position()
        dt_ms = self._ticks_diff(now, self.last_time)
        dt = dt_ms / 1000.0
        delta = current_angle - self.last_angle

        # Wraparound handling
        if delta > math.pi:
            delta -= 2 * math.pi
        elif delta < -math.pi:
            delta += 2 * math.pi

        # Velocity
        self.velocity = delta / dt if dt > 0 else 0.0

        # Accumuated total rotations
        self.accum_angle += delta

        # Remember things for next time
        self.last_angle = current_angle
        self.last_time = now

    def get_velocity(self) :
        return self.velocity
    
    def get_position(self) :
        return self.accum_angle
