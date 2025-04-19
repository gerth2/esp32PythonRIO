# DualMotorDriver.py
from machine import Pin, PWM

class MG90SServo:
    def __init__(self, pin, freq=50, max_pulse=2.4, min_pulse=0.6):
        """Initialize servo with one control pin"""
        self.freq = freq
        self.max_pulse_ms = max_pulse
        self.min_pulse_ms = min_pulse

        self.isStopped = True

        # Left motor pins
        self.pwm = PWM(Pin(pin), freq=freq)

    def set(self, inVal):
        """
        Sets speed for a motor using two PWM pins.
        - speed: float from -1.0 to 1.0
        """
        if(self.isStopped):
            duty = 0
        else:
            inVal = max(min(inVal, 1.0), -1.0)

            pulse_width = self._toPulseWidth(inVal)  # Convert to pulse width in ms
            dutyCyclePct = (pulse_width / 1000) * self.freq

            duty = int(abs(dutyCyclePct) * 1023)  # 10-bit resolution

        self.pwm.duty(duty)

    def setStopped(self, stopped):
        self.isStopped = stopped

    def _toPulseWidth(self, val):
        """
        Convert -1 to 1 range to pulse width in ms.
        """
        pulse_width = self.min_pulse_ms + (self.max_pulse_ms - self.min_pulse_ms) * (val / 2.0 + 0.5)
        return pulse_width
    


