from collections import deque
import bisect

class MedianFilter:
    """
    A class that implements a moving-window median filter. Useful for reducing measurement noise,
    especially with processes that generate occasional, extreme outliers (such as values from vision
    processing, LIDAR, or ultrasonic sensors).
    """

    def __init__(self, size: int):
        """
        Creates a new MedianFilter.

        :param size: The number of samples in the moving window.
        """
        self._size = size
        self._value_buffer = deque(maxlen=size)  # Circular buffer of values (ordered by time)
        self._ordered_values = []  # Sorted list of values in the window (ordered by value)

    def calculate(self, next_val: float) -> float:
        """
        Calculates the moving-window median for the next value of the input stream.

        :param next_val: The next input value.
        :return: The median of the moving window, updated to include the next value.
        """
        # Insert the new value in sorted order
        bisect.insort(self._ordered_values, next_val)

        # If buffer is at max size, remove the oldest and also remove it from the sorted list
        if len(self._value_buffer) == self._size:
            oldest = self._value_buffer.pop()
            index = bisect.bisect_left(self._ordered_values, oldest)
            if index < len(self._ordered_values):
                del self._ordered_values[index]

        # Add new value to the front of the circular buffer
        self._value_buffer.appendleft(next_val)

        cur_size = len(self._ordered_values)
        if cur_size % 2 != 0:
            return self._ordered_values[cur_size // 2]
        else:
            mid = cur_size // 2
            return (self._ordered_values[mid - 1] + self._ordered_values[mid]) / 2.0

    def last_value(self) -> float:
        """
        Returns the last value calculated by the MedianFilter.

        :return: The last value.
        """
        return self._value_buffer[0] if self._value_buffer else 0.0

    def reset(self):
        """
        Resets the filter, clearing the window of all elements.
        """
        self._value_buffer.clear()
        self._ordered_values.clear()

