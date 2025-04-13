class Motor():
    """
    Common base class for all PWM Motor Controllers.
    """
    def __init__(self, name: str, channel) :
        """
        Constructor for a PWM Motor %Controller connected via PWM.
        
        :param name:    Name to use for SendableRegistry
        :param channel: The PWM channel that the controller is attached to. 
                        TBD These on our robot
        """
        pass
    
    def disable(self) :
        pass


    def set(self, value) :
        """
        Set the PWM value.
        
        The PWM value is set using a range of -1.0 to 1.0, appropriately scaling
        the value for the PWM output on the ESP32.
        
        :param value: The speed value between -1.0 and 1.0 to set.
        """
        pass

    def setInverted(self, isInverted: bool) :
        pass

    def setVoltage(self, output) :
        """
        Sets the voltage output of the PWMMotorController. Compensates for
        the current bus voltage to ensure that the desired voltage is output even
        if the battery voltage is below 12V - highly useful when the voltage
        outputs are "meaningful" (e.g. they come from a feedforward calculation).
        
        NOTE: This function *must* be called regularly in order for voltage
        compensation to work properly - unlike the ordinary set function, it is not
        "set it and forget it."
        
        :param output: The voltage to output.
        """
        pass

    def stopMotor(self) :
        pass
