# AS5600.py
from machine import Pin, I2C
from time import ticks_ms, ticks_diff
import math

class AS5600Encoder:
    AS5600_ADDR = 0x36
    RAW_ANGLE_REGISTER = 0x0C

    def __init__(self, i2c_bus):
        self.i2c = i2c_bus
        self.last_time = self._now()
        self.last_angle = 0.0
        self.last_angle = self.read_position()

    def _now(self):
        return ticks_ms()

    def _ticks_diff(self, new, old):
        return ticks_diff(new, old)

    def read_position(self) :
        """Reads the raw angle from the AS5600 and returns it in radians."""
        try:
            data = self.i2c.readfrom_mem(self.AS5600_ADDR, self.RAW_ANGLE_REGISTER, 2)
            raw_angle = (data[0] << 8) | data[1]
            angle_rad = (raw_angle / 4096) * 2 * math.pi
            return angle_rad
        except Exception as e:
            print("AS5600 read error:", e)
            return self.last_angle  # fallback to last known angle

    def get_velocity(self) :
        """Returns the angular velocity in radians per second."""
        current_time = self._now()
        current_angle = self.read_position()

        dt_ms = self._ticks_diff(current_time, self.last_time)
        dt = dt_ms / 1000  # convert to seconds

        delta = current_angle - self.last_angle

        # Wraparound handling
        if delta > math.pi:
            delta -= 2 * math.pi
        elif delta < -math.pi:
            delta += 2 * math.pi

        velocity = delta / dt if dt > 0 else 0.0

        self.last_angle = current_angle
        self.last_time = current_time

        return velocity
