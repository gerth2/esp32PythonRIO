from _private.HAL import HAL


class Motor():
    """
    Common base class for all PWM Motor Controllers.
    """

    VALID_CHANNELS = [0, 1]

    def __init__(self, channel) :
        """
        Constructor for a PWM Motor %Controller connected via PWM.
        
        :param channel: The PWM channel that the controller is attached to. 
                        0 = Left Drive Motor
                        1 = Right Drive Motor
        """
        if channel not in self.VALID_CHANNELS:
            raise ValueError(f"Invalid channel. Valid channels are {" , ".join(map(str, self.VALID_CHANNELS))}.")
        
        self.ch = channel

        if(self.ch == 0):
            self.setSpdFcn = HAL.motors.set_left_speed
            self.setVoltageFcn = HAL.setLeftMotorVoltage
        else:
            self.setSpdFcn = HAL.motors.set_right_speed
            self.setVoltageFcn = HAL.setRightMotorVoltage

        self.invFactor = 1.0
    
    def disable(self) :
        self.setSpdFcn(0.0)


    def set(self, value) :
        """
        Set the PWM value.
        
        The PWM value is set using a range of -1.0 to 1.0, appropriately scaling
        the value for the PWM output on the ESP32.
        
        :param value: The speed value between -1.0 and 1.0 to set.
        """
        self.setSpdFcn(_limit(value * self.invFactor))

    def setInverted(self, isInverted: bool) :
        self.invFactor = -1.0 if isInverted else 1.0

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
        self.setVoltageFcn(output * self.invFactor)

    def stopMotor(self) :
        self.setSpdFcn(0.0)

def _limit(val):
    return max(min(1.0, val),-1.0)
