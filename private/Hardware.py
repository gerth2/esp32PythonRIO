from machine import Pin, I2C
from private.AS5600Encoder import AS5600Encoder
from private.DualMotorControl import DualMotorDriver
from private.MPU6050ZGyro import MPU6050ZGyro
from private.voltageMonitor import VoltageMonitor

I2C_BUS_A_SCL = 23
I2C_BUS_A_SDA = 22
I2C_BUS_A_FREQ = 400_000

I2C_BUS_B_SCL = 18
I2C_BUS_B_SDA = 19
I2C_BUS_B_FREQ = 400_000

LEFT_MOTOR_PIN_1 = 32
LEFT_MOTOR_PIN_2 = 26

VMON_PIN = 34

RIGHT_MOTOR_PIN_1 = 25
RIGHT_MOTOR_PIN_2 = 33

class Hardware:
    def __init__(self):
        self.i2cBusA = I2C(0, scl=Pin(I2C_BUS_A_SCL), sda=Pin(I2C_BUS_A_SDA), freq=I2C_BUS_A_FREQ)
        self.i2cBusB = I2C(1, scl=Pin(I2C_BUS_B_SCL), sda=Pin(I2C_BUS_B_SDA), freq=I2C_BUS_B_FREQ)

        #self.leftEnc = AS5600Encoder(self.i2cBusA)
        #self.rightEnc = AS5600Encoder(self.i2cBusB)
        self.gyro = MPU6050ZGyro(self.i2cBusA)
        self.motors = DualMotorDriver(LEFT_MOTOR_PIN_1, LEFT_MOTOR_PIN_2, RIGHT_MOTOR_PIN_1, RIGHT_MOTOR_PIN_2)
        self.vMon = VoltageMonitor(pin=VMON_PIN)

        self.heading = 0.0

        self.gyro.calibrate()
        self.gyro.reset()

    def update(self):
        #self.lenc = self.leftEnc.read_position()
        #self.renc = self.rightEnc.read_position()
        self.gyro.update()
        self.headingDeg = self.gyro.get_angle()
        #print(self.headingDeg)
        self.motors.set_left_speed(0.0)
        self.motors.set_right_speed(0.0)
