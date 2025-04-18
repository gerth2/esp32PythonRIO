import time

class Timer():

    @staticmethod
    def getFPGATimestamp():
        """
        Returns the current time in seconds since the Code started running.
        This is a floating-point number that represents the time in seconds.
        """
        return time.ticks_us()/ 1000000.0