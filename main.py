from TimedRobot import TR_MODE_DISABLED,TR_MODE_AUTONOMOUS, TR_MODE_TELEOP, 
from _private.Controllers import KB
from wpilib import *
import sys, time
from _private.HAL import HAL
from _private.RobotSignalLight import RobotSignalLight
from _private.webInterface import WebInterfaceServer
from TimedRobot import MainStateMachine
from robotName import ROBOT_NAME
import machine
import network

codeRunning = False
rsm = None

MAIN_LOOP_TIME_MS = 50

def startUserCode():
    global rsm, codeRunning
    print("*********** USER ROBOT CODE STARTING ******************")
    if "robot" in sys.modules:
        del sys.modules["robot"]  # Force re-import
    try:
        userMod = __import__("robot")
        rsm = MainStateMachine(userMod.MyRobot())
        codeRunning = True
        print("***********       CODE RUNNING!      ******************")

    except Exception as e:
        print("********** USER ROBOT CODE CRASHED! *****************")
        print("Error in user robot code:")
        print(e)
        codeRunning = False

def updateUserCode():
    global rsm, codeRunning, webInf
    if(rsm is not None):
        if webInf.state == "disabled" or not codeRunning:
            rsm.set_mode(TR_MODE_DISABLED)
        elif webInf.state == "teleop":
            rsm.set_mode(TR_MODE_TELEOP)
        elif webInf.state == "auto":
            rsm.set_mode(TR_MODE_AUTONOMOUS)
        else:
            rsm.set_mode(TR_MODE_DISABLED)

        if(codeRunning):
            try:
                rsm.update()
            except Exception as e:
                print("********** USER ROBOT CODE CRASHED! *****************")
                print("Error in user robot code:")
                print(e)
                codeRunning = False

# Init WiFi
ap = network.WLAN(network.WLAN.IF_AP) # create access-point interface
#ap.config(pm = 0xa11140)  # disables power save mode
ap.config(ssid=f'ESP-1736-{ROBOT_NAME}')      # set the SSID of the access point
ap.config(max_clients=2)              # set how many clients can connect to the network
ap.ipconfig(addr4=("10.17.36.2", "255.255.255.0")) 
ap.ipconfig(gw4="10.17.36.1")
ap.active(True)                       # activate the interface


try:
    rsl = RobotSignalLight()
    webInf = WebInterfaceServer()
    startUserCode()

    while True:
        startTimeUs = time.ticks_us()

        webInf.set_batVoltage(HAL.vMon.read_voltage())
        webInf.set_codeRunning(codeRunning)
        webInf.update()  # update web interface state

        KB.setKeycode(webInf.keyStates)  # update keyboard state
        
        if(webInf.state == "disabled"):
            # Motor Safeties - disable
            HAL.setLeftMotorVoltage(0.0)
            HAL.setRightMotorVoltage(0.0)

        HAL.update()  # update hardware state

        # Reload robot.py if needed
        if webInf.getFileChanged():
            startUserCode()

        updateUserCode()  # update the user's robot code

        rsl.set_enabled(webInf.state != "disabled" and codeRunning)
        rsl.update(time.ticks_ms())

        procTimeUs = float(time.ticks_us() - startTimeUs)
        #print(f"Proc Time: {procTimeUs/1000.0}ms")
        if(procTimeUs < MAIN_LOOP_TIME_MS*1000.0):
            time.sleep_us(int(MAIN_LOOP_TIME_MS*1000.0 - procTimeUs))  # 20ms loop time
        else:
            print(f"Warning! Loop Overrun: ProcTime: {procTimeUs/1000.0}ms")


except Exception as e:
    print(">>>>>>>>>>>>>>> BASE ROBOT CODE CRASHED! <<<<<<<<<<<<<<")
    sys.print_exception(e)
    time.sleep_ms(2000)

# Allow exit to raw repl
