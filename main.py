from TimedRobot import TR_MODE_DISABLED,TR_MODE_AUTONOMOUS, TR_MODE_TELEOP, TR_MODE_TEST, MainStateMachine
import sys, time
from robot import MyRobot
from driverStationInterface import DS_MODE_AUTO,DS_MODE_TELEOP,DS_MODE_TEST, DsInterface
import machine

def dsToRSMMode(enabled, mode):
        if(not enabled):
            return TR_MODE_DISABLED
        else:
            if(mode == DS_MODE_AUTO):
                return TR_MODE_AUTONOMOUS
            elif(mode == DS_MODE_TELEOP):
                 return TR_MODE_TELEOP
            else:
                 return TR_MODE_TEST

try:
    ds = DsInterface()
    print("Robot Code Starting...")
    rsm = MainStateMachine(MyRobot())
    ds.setCodeRunning(True)
    print("Robot Code Startup complete!")
    while True:
        startTimeUs = time.ticks_us()
        ds.periodic()
        rsm.set_mode(dsToRSMMode(ds.getEnabledCmd(), ds.getModeCmd()))
        rsm.update()
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