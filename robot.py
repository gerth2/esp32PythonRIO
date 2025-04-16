from TimedRobot import TimedRobot
from wpilib import Gyro, Motor, Keyboard

class MyRobot(TimedRobot):
    def __init__(self):
        self.gyro = Gyro() 
        self.gyro.calibrate()
        self.leftMotor = Motor(0)
        self.rightMotor = Motor(1)
        self.rightMotor.setInverted(True)
        self.kb = Keyboard()
        
        self.fwdRevCmd = 0.0
        self.rotCmd = 0.0

    def autonomousInit(self):
        print("myAuto")
        self.gyro.reset()

    def autonomousPeriodic(self):
        print(self.gyro.getAngle())

    def teleopInit(self):
        print("myTeleop")

    def teleopPeriodic(self):      
        self.fwdRevCmd = 0.0
        self.rotCmd = 0.0
        
        if(self.kb.w_pressed()):
            self.fwdRevCmd = 1.0
        elif(self.kb.s_pressed()):
            self.fwdRevCmd = -1.0
            
        if(self.kb.a_pressed()):
            self.rotCmd = 1.0
        elif(self.kb.d_pressed()):
            self.rotCmd = -1.0

    def robotPeriodic(self):
        self.leftMotor.set(self.fwdRevCmd - self.rotCmd)
        self.rightMotor.set(self.fwdRevCmd + self.rotCmd)
        