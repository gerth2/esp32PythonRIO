from TimedRobot import TimedRobot


class MyRobot(TimedRobot):
    def __init__(self):
        pass

    def autonomousInit(self):
        pass

    def autonomousPeriodic(self):
        print("My Auto!")

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        print("My Teleop!")

    def robotPeriodic(self):
        pass