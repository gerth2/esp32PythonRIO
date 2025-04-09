from TimedRobot import TimedRobot


class MyRobot(TimedRobot):
    def __init__(self):
        pass

    def autonomousInit(self):
        print("myAuto")

    def autonomousPeriodic(self):
        pass

    def teleopInit(self):
        print("myTeleop")

    def teleopPeriodic(self):
        pass

    def robotPeriodic(self):
        pass