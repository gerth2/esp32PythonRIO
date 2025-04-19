from TimedRobot import TimedRobot
from wpilib import Gyro, Motor, Keyboard, Servo, Encoder, SmartDashboard

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

        self.lenc = Encoder(0)
        self.renc = Encoder(1)
        self.lenc.setReverseDirection(True)

        self.servo = Servo(0)

    def autonomousInit(self):
        print("myAuto")

    def autonomousPeriodic(self):
        pass
        
    def teleopInit(self):
        print("myTeleop")
        self.lenc.reset()
        self.renc.reset()
        self.gyro.reset()


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


        if(self.kb.q_pressed()):
            self.servo.setAngle(-90)
        elif(self.kb.e_pressed()):
            self.servo.setAngle(90)
            
        gyroAngle = self.gyro.getAngle()
        self.rotCmd += (0.0 - gyroAngle)* 0.02

        SmartDashboard.putNumber("GyroAngle", gyroAngle)



    def robotPeriodic(self):
        leftMotorCmd = self.fwdRevCmd - self.rotCmd
        self.leftMotor.set(leftMotorCmd)
        rightMotorCmd = self.fwdRevCmd + self.rotCmd
        self.rightMotor.set(rightMotorCmd)

        SmartDashboard.putNumber("Left Encoder", self.lenc.getRate())
        SmartDashboard.putNumber("Right Encoder", self.renc.getRate())
        SmartDashboard.putNumber("Left Motor Cmd", leftMotorCmd)
        SmartDashboard.putNumber("Right Motor Cmd", rightMotorCmd)
        