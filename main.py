import machine, sys, time
from robot import MyRobot
from driverStationInterface import DsInterface


try:
    ds = DsInterface()
    print("Robot Code Starting...")
    robot = MyRobot()
    print("Robot Code Startup complete!")
    robot.autonomousInit()
    while True:
        startTimeUs = time.ticks_us()
        ds.periodic()
        robot.autonomousPeriodic()
        robot.robotPeriodic()
        procTimeUs = time.ticks_us() - startTimeUs
        time.sleep_us(20*1000 - procTimeUs)  # 20ms loop time
except Exception as e:
    print("Robot code has reset:")
    sys.print_exception(e)
    time.sleep_ms(2000)

# Following a normal Exception or main() exiting, reset the board.
# Following a non-Exception error such as KeyboardInterrupt (Ctrl-C),
# this code will drop to a REPL. Place machine.reset() in a finally
# block to always reset, instead.
machine.reset()