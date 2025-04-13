# MPU6050ZGyro.py
# from machine import I2C
# from time import ticks_ms, ticks_diff
import math
import time

class MPU6050ZGyro:
    MPU6050_ADDR = 0x68
    PWR_MGMT_1 = 0x6B
    GYRO_ZOUT_H = 0x47
    GYRO_SENS = 131.0  # LSB/(°/s) for ±250°/s sensitivity

    def __init__(self, i2c):
        self.i2c = i2c
        self.offset = 0.0  # degrees/sec
        self.angle = 0.0   # accumulated angle in degrees
        self.last_time = time.ticks_us()/1000.0

        # Wake up the MPU6050
        try:
            self.i2c.writeto_mem(self.MPU6050_ADDR, self.PWR_MGMT_1, b'\x00')
        except Exception as e:
            print("MPU6050 init error:", e)


    def read_raw_gyro_z(self) -> int:
        """Returns the raw 16-bit signed gyroscope Z value"""
        data = self.i2c.readfrom_mem(self.MPU6050_ADDR, self.GYRO_ZOUT_H, 2)
        raw = (data[0] << 8) | data[1]
        if raw >= 0x8000:
            raw -= 0x10000
        return raw

    def read_gyro_z(self) -> float:
        """Returns Z-axis angular velocity in radians per second (offset not applied)"""
        try:
            raw = self.read_raw_gyro_z()
            deg_per_sec = raw / self.GYRO_SENS
            rad_per_sec = deg_per_sec * (math.pi / 180)
            return rad_per_sec
        except Exception as e:
            print("MPU6050 read error:", e)
            return 0.0

    def calibrate(self, num_samples: int = 100, delay_ms: int = 10):
        """Measures and sets the zero offset for Z-axis angular velocity."""
        total = 0
        time.sleep_ms(250)
        for _ in range(num_samples):
            raw = self.read_raw_gyro_z()
            total += raw
            time.sleep_ms(delay_ms)

        avg_raw = total / num_samples
        self.offset = avg_raw / self.GYRO_SENS  # in degrees/sec
        print("Calibration complete. Offset: {:.3f} deg/s".format(self.offset))

    def update(self):
        #s = time.ticks_us()
        """Integrates angular velocity over time to update accumulated angle in degrees."""
        current_time = time.ticks_us()/1000.0
        dt_ms = time.ticks_diff(current_time, self.last_time)
        dt = dt_ms / 1000  # seconds

        try:
            raw = self.read_raw_gyro_z()
            deg_per_sec = raw / self.GYRO_SENS
            deg_per_sec -= self.offset  # apply calibration offset

            self.angle += deg_per_sec * dt
            self.last_time = current_time
        except Exception as e:
            print("MPU6050 update error:", e)
        #print(f"Gyro Update: {(time.ticks_us() - s)/1000.0}ms")

    def get_angle(self) -> float:
        """Returns the current accumulated angle in degrees."""
        return self.angle

    def reset(self):
        """Resets the integrated angle to zero."""
        self.angle = 0.0
        self.last_time = time.ticks_us()/1000.0
