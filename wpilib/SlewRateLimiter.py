import time

def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value between a minimum and maximum."""
    return max(min_value, min(value, max_value))

class SlewRateLimiter:
    """
    A class that limits the rate of change of an input value. Useful for implementing voltage,
    setpoint, and/or output ramps. A slew-rate limit is most appropriate when the quantity being
    controlled is a velocity or a voltage.
    """

    def __init__(self, positive_rate_limit: float, negative_rate_limit: float = None, initial_value: float = 0.0):
        """
        Creates a new SlewRateLimiter with the given rate limits and initial value.

        :param positive_rate_limit: The rate-of-change limit in the positive direction, in units per second.
                                    This is expected to be positive.
        :param negative_rate_limit: The rate-of-change limit in the negative direction, in units per second.
                                    This is expected to be negative. If None, defaults to -positive_rate_limit.
        :param initial_value: The initial value of the input.
        """
        self._positive_rate_limit = positive_rate_limit
        self._negative_rate_limit = negative_rate_limit if negative_rate_limit is not None else -positive_rate_limit
        self._prev_val = initial_value
        self._prev_time = time.ticks_ms()

    def calculate(self, input_val: float) -> float:
        """
        Filters the input to limit its slew rate.

        :param input_val: The input value whose slew rate is to be limited.
        :return: The filtered value, which will not change faster than the slew rate.
        """
        current_time = time.ticks_ms()
        elapsed_ms = time.ticks_diff(current_time, self._prev_time)
        elapsed_sec = elapsed_ms / 1000.0

        delta = input_val - self._prev_val
        limited_delta = clamp(
            delta,
            self._negative_rate_limit * elapsed_sec,
            self._positive_rate_limit * elapsed_sec
        )
        self._prev_val += limited_delta
        self._prev_time = current_time

        return self._prev_val

    def last_value(self) -> float:
        """
        Returns the value last calculated by the SlewRateLimiter.

        :return: The last value.
        """
        return self._prev_val

    def reset(self, value: float):
        """
        Resets the slew rate limiter to the specified value; ignores the rate limit when doing so.

        :param value: The value to reset to.
        """
        self._prev_val = value
        self._prev_time = time.ticks_ms()
