from _private.HAL import HAL

class Servo():
    """
    Standard hobby style servo.
    
    The range parameters default to the appropriate values for the Hitec HS-322HD
    servo provided in the FIRST Kit of Parts in 2008.
    """

    VALID_CHANNELS = [0]


    def __init__(self, channel):
        """
        Constructor.
        
        By default, 2.4 ms is used as the max PWM value and 0.6 ms is used as the
        min PWM value.
        
        :param channel: The PWM channel to which the servo is attached. 
                        TBD THESE ON OUR ROBOT
        """
        if channel not in self.VALID_CHANNELS:
            raise ValueError(f"Invalid channel. Valid channels are {" , ".join(map(str, self.VALID_CHANNELS))}.")
        
        self._ch = channel

    def set(self, value) :
        """
        Set the servo position.
        
        Servo values range from -1.0 to 1.0 corresponding to the range of full left
        to full right.
        
        :param value: Position from -1.0 to 1.0.
        """
        if(self._ch == 0) :
            HAL.servo0.set(value)

    def setAngle(self, angle) :
        """
        Set the servo angle.
        
        The angles are based on the HS-322HD Servo, and have a range of 0 to 180
        degrees.
        
        Servo angles that are out of the supported range of the servo simply
        "saturate" in that direction. In other words, if the servo has a range of
        (X degrees to Y degrees) than angles of less than X result in an angle of
        X being set and angles of more than Y degrees result in an angle of Y being
        set.
        
        :param angle: The angle in degrees to set the servo.
        """
        self.set((angle - 90) / 90)  # Convert angle to -1.0 to 1.0 range

    def setOffline(self) :
        """
        Set the servo to offline.
        
        Set the servo raw value to 0 (undriven)
        """
        # TODO
        pass