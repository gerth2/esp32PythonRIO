class Servo():
    """
    Standard hobby style servo.
    
    The range parameters default to the appropriate values for the Hitec HS-322HD
    servo provided in the FIRST Kit of Parts in 2008.
    """
    def __init__(self, channel):
        """
        Constructor.
        
        By default, 2.4 ms is used as the max PWM value and 0.6 ms is used as the
        min PWM value.
        
        :param channel: The PWM channel to which the servo is attached. 0-9 are
                        on-board, 10-19 are on the MXP port
        """
        pass


    def set(self, value) :
        """
        Set the servo position.
        
        Servo values range from 0.0 to 1.0 corresponding to the range of full left
        to full right.
        
        :param value: Position from 0.0 to 1.0.
        """
        pass 

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
        pass

    def setOffline(self) :
        """
        Set the servo to offline.
        
        Set the servo raw value to 0 (undriven)
        """
        pass