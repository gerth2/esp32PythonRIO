# DualMotorDriver.py
from machine import Pin, PWM

class DualMotorDriver:
    def __init__(self, left_pin1, left_pin2, right_pin1, right_pin2, freq=200):
        """Initialize motor driver with 2 pins per motor."""
        self.freq = freq

        # Left motor pins
        self.left_pwm1 = PWM(Pin(left_pin1), freq=freq)
        self.left_pwm2 = PWM(Pin(left_pin2), freq=freq)

        # Right motor pins
        self.right_pwm1 = PWM(Pin(right_pin1), freq=freq)
        self.right_pwm2 = PWM(Pin(right_pin2), freq=freq)

        self.set_left_speed(0)
        self.set_right_speed(0)

    def _set_motor(self, pwm1, pwm2, speed):
        """
        Sets speed for a motor using two PWM pins.
        - speed: float from -1.0 to 1.0
        """
        speed = max(min(speed, 1.0), -1.0)
        duty = int(abs(speed) * 1023)  # 10-bit resolution

        if speed > 0:
            pwm1.duty(duty)
            pwm2.duty(0)
        elif speed < 0:
            pwm1.duty(0)
            pwm2.duty(duty)
        else:
            pwm1.duty(0)
            pwm2.duty(0)

    def set_left_speed(self, speed: float):
        """Set speed for left motor (-1.0 to 1.0)."""
        self._set_motor(self.left_pwm1, self.left_pwm2, speed)

    def set_right_speed(self, speed: float):
        """Set speed for right motor (-1.0 to 1.0)."""
        self._set_motor(self.right_pwm1, self.right_pwm2, speed)

    def stop(self):
        """Stops both motors."""
        self.set_left_speed(0)
        self.set_right_speed(0)
