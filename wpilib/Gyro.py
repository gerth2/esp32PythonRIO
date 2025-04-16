from _private.HAL import HAL

class Gyro():
    """
    Use a rate gyro to return the robots heading relative to a starting position.
    The Gyro class tracks the robots heading based on the starting position. As
    the robot rotates the new heading is computed by integrating the rate of
    rotation returned by the sensor. When the class is instantiated, it does a
    short calibration routine where it samples the gyro while at rest to
    determine the default offset. This is subtracted from each sample to
    determine the heading.
    
    This class is for the gyro sensor onboard the robot
    """

    def __init__(self):
        """
        %Gyro constructor

        No arguments, there is only one.
        """
        pass
    
    def calibrate(self) :
        """
        Calibrate the gyro by running for a number of samples and computing the
        center value. Then use the center value as the Accumulator center value for
        subsequent measurements.
        
        It's important to make sure that the robot is not moving while the
        centering calculations are in progress, this is typically done when the
        robot is first turned on while it's sitting at rest before the competition
        starts.
        """
        HAL.gyro.calibrate()

    def getAngle(self) :
        """
        Return the actual angle in degrees that the robot is currently facing.
        
        The angle is based on the current accumulator value corrected by the
        oversampling rate, the gyro type and the A/D calibration values. The angle
        is continuous, that is it will continue from 360->361 degrees. This allows
        algorithms that wouldn't want to see a discontinuity in the gyro output as
        it sweeps from 360 to 0 on the second time around.
        
        :returns: The current heading of the robot in degrees. This heading is based
                  on integration of the returned rate from the gyro.
        """
        return HAL.gyro.get_angle()

    def getRate(self) :
        """
        Return the rate of rotation of the gyro
        
        The rate is based on the most recent reading of the gyro analog value
        
        :returns: the current rate in degrees per second
        """
        return HAL.gyro.read_gyro_z()

    def reset(self) :
        """
        Reset the gyro.
        
        Resets the gyro to a heading of zero. This can be used if there is
        significant drift in the gyro and it needs to be recalibrated after it has
        been running.
        """
        HAL.gyro.reset() 
