from TimedRobot import TR_MODE_DISABLED,TR_MODE_AUTONOMOUS, TR_MODE_TELEOP, MainStateMachine
import sys, time
from private.Hardware import Hardware
from private.RobotSignalLight import RobotSignalLight
from private.webInterface import WebInterfaceServer
from robotName import ROBOT_NAME
import machine
import network

codeRunning = False
rsm = None

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
ap.config(ssid=f'ESP-1736-{ROBOT_NAME}')      # set the SSID of the access point
ap.config(max_clients=2)              # set how many clients can connect to the network
ap.ipconfig(addr4=("10.17.36.2", "255.255.255.0"))
ap.ipconfig(gw4="10.17.36.1")
ap.active(True)                       # activate the interface

try:
    rsl = RobotSignalLight()
    webInf = WebInterfaceServer()
    hw = Hardware()
    startUserCode()

    while True:
        startTimeUs = time.ticks_us()

        webInf.set_batVoltage(hw.vMon.read_voltage())
        webInf.set_codeRunning(codeRunning)
        webInf.update()  # handle web requests

        # TEMP TESTING ONLY
        if(webInf.keyStates == 0x01):
            hw.setLeftMotorVoltage(3.0)
            hw.setRightMotorVoltage(0.0)
        elif(webInf.keyStates == 0x04):
            hw.setLeftMotorVoltage(-3.0)
            hw.setRightMotorVoltage(0.0)
        elif(webInf.keyStates == 0x02):
            hw.setLeftMotorVoltage(0.0)
            hw.setRightMotorVoltage(3.0)
        elif(webInf.keyStates == 0x08):
            hw.setLeftMotorVoltage(0.0)
            hw.setRightMotorVoltage(-3.0)
        else:
            hw.setLeftMotorVoltage(0.0)
            hw.setRightMotorVoltage(0.0)

        hw.update()  # update hardware state


        # Reload robot.py if needed
        if webInf.getFileChanged():
            startUserCode()


        updateUserCode()  # update the user's robot code

        rsl.set_enabled(webInf.state != "disabled" and codeRunning)
        rsl.update(time.ticks_ms())

        procTimeUs = time.ticks_us() - startTimeUs
        time.sleep_us(20*1000 - procTimeUs)  # 20ms loop time

except Exception as e:
    print(">>>>>>>>>>>>>>> BASE ROBOT CODE CRASHED! <<<<<<<<<<<<<<")
    sys.print_exception(e)
    time.sleep_ms(2000)

# Allow exit to raw repl
