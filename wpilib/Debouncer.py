import time

RISING = 1
FALLING = 2
BOTH = 3

class Debouncer:
    """
    A simple debounce filter for boolean streams. Requires that the boolean change value from
    baseline for a specified period of time before the filtered value changes.
    """

    def __init__(self, debounce_time: float, debounce_type= RISING):
        """
        Creates a new Debouncer.

        :param debounce_time: The number of seconds the value must change from baseline for the
                               filtered value to change.
        :param debounce_type: Which type of state change the debouncing will be performed on.
        """
        self._debounce_time = debounce_time
        self._debounce_type = debounce_type
        self._prev_time = self._get_time()

        if debounce_type in (BOTH, RISING):
            self._baseline = False
        else:  # DebounceType.FALLING
            self._baseline = True

    def _get_time(self) -> float:
        return time.monotonic()

    def _reset_timer(self):
        self._prev_time = self._get_time()

    def _has_elapsed(self) -> bool:
        return self._get_time() - self._prev_time >= self._debounce_time

    def calculate(self, input_val: bool) -> bool:
        """
        Applies the debouncer to the input stream.

        :param input_val: The current value of the input stream.
        :return: The debounced value of the input stream.
        """
        if input_val == self._baseline:
            self._reset_timer()

        if self._has_elapsed():
            if self._debounce_type == BOTH:
                self._baseline = input_val
                self._reset_timer()
            return input_val
        else:
            return self._baseline

    def set_debounce_time(self, time_seconds: float):
        """
        Sets the time to debounce.

        :param time_seconds: The debounce time in seconds.
        """
        self._debounce_time = time_seconds

    def get_debounce_time(self) -> float:
        """
        Gets the time to debounce.

        :return: The debounce time in seconds.
        """
        return self._debounce_time

    def set_debounce_type(self, debounce_type):
        """
        Sets the debounce type.

        :param debounce_type: The debounce type.
        """
        self._debounce_type = debounce_type

    def get_debounce_type(self):
        """
        Gets the debounce type.

        :return: The debounce type.
        """
        return self._debounce_type
