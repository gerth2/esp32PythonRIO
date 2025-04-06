import machine, time 

class RobotSignalLight:
    def __init__(self, pin_num: int = 2, blink_period_ms: int = 500):
        self.pin = machine.Pin(pin_num, machine.Pin.OUT)
        self.enabled = False
        self.blink_period = blink_period_ms
        self._last_toggle = 0
        self._led_on = False

        self.pin.off()

    def set_enabled(self, is_enabled: bool):
        """
        Set whether the robot is enabled (True) or disabled (False).
        """
        self.enabled = is_enabled


    def update(self, now_ms: int):
        """
        Call this periodically (~every 20ms). Pass in time.ticks_ms().
        """
        if not self.enabled:
            self.pin.on()
        else:
            # Blink logic
            elapsed = now_ms - self._last_toggle
            if elapsed >= self.blink_period // 2:
                self._led_on = not self._led_on
                self.pin.value(self._led_on)
                self._last_toggle = now_ms
