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
        print("Hello from ESP32!")

    def robotPeriodic(self):
        pass