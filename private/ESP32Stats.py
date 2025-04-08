import esp32
import gc
import os
import time

import gc
import os

def free():
  return gc.mem_free()


class ESP32SystemStats:
    def __init__(self):
        pass

    def get_free_heap(self):
        """Returns the available RAM (in bytes)."""
        return free()

    def get_free_program_space(self):
        """Returns the available program storage space (in bytes)."""
        return 1234 # TODO
