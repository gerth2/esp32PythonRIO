from _private.HAL import HAL

class Encoder():

    VALID_CHANNELS = [0, 1]
    """
    Class to read onboard encoders.
    """
    def __init__(self, channel:int):
        if channel not in self.VALID_CHANNELS:
            raise ValueError(f"Invalid channel. Valid channels are {" , ".join(map(str, self.VALID_CHANNELS))}.")
        
        self.ch = channel

    def get(self) :
        """
        Gets the current count.
        
        Returns the current count on the Encoder. This method compensates for the
        decoding type.
        
        :returns: Current distance traveled by the encoder
        """
        return self.getDistance()

    def getDirection(self) -> bool:
        """
        The last direction the encoder value changed.
        
        :returns: The last direction the encoder value changed.
        """
        pass

    def getDistance(self) :
        """
        Get the distance the robot has driven since the last reset.
        
        :returns: The distance driven since the last reset in rotations
        """
        #if(self.ch == 0):
        #    return HAL.lenc.get_position()
        pass

    def getRate(self) :
        """
        Get the current rate of the encoder in rotations per second
        
        Units are distance per second as scaled by the value from
        SetDistancePerPulse().
        
        :returns: The current rate of the encoder.
        """
        pass

    def getStopped(self) -> bool:
        """
        Determine if the encoder is stopped.
        
        Using the MaxPeriod value, a boolean is returned that is true if the
        encoder is considered stopped and false if it is still moving. A stopped
        encoder is one where the most recent pulse width exceeds the MaxPeriod.
        
        :returns: True if the encoder is considered stopped.
        """
        pass

    def reset(self) :
        """
        Reset the Encoder distance to zero.
        
        Resets the current count to zero on the encoder.
        """
        pass

    def setReverseDirection(self, reverseDirection: bool) :
        """
        Set the direction sensing for this encoder.
        
        This sets the direction sensing on the encoder so that it could count in
        the correct software direction regardless of the mounting.
        
        :param reverseDirection: true if the encoder direction should be reversed
        """
        pass
   