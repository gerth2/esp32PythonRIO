from TimedRobot import TR_MODE_DISABLED,TR_MODE_AUTONOMOUS, TR_MODE_TELEOP, TR_MODE_TEST, MainStateMachine
import sys, time
from robot import MyRobot
from private.RobotSignalLight import RobotSignalLight
from private.webEditor import WebEditorServer
import machine
import network

# Init WiFi
ap = network.WLAN(network.WLAN.IF_AP) # create access-point interface
ap.config(ssid='ESP-1736-ROBOT')      # set the SSID of the access point
ap.config(max_clients=2)              # set how many clients can connect to the network
ap.ipconfig(addr4=("10.17.36.2", "255.255.255.0"))
ap.ipconfig(gw4="10.17.36.1")
ap.active(True)                       # activate the interface

try:
    print("Robot Code Starting...")
    rsl = RobotSignalLight()
    rsm = MainStateMachine(MyRobot())
    editor = WebEditorServer()

    print("Robot Code Startup complete!")
    while True:
        startTimeUs = time.ticks_us()


        editor.update()  # handle web requests

        if editor.state == "disabled":
            rsm.set_mode(TR_MODE_DISABLED)
        elif editor.state == "teleop":
            rsm.set_mode(TR_MODE_TELEOP)
        elif editor.state == "auto":
            rsm.set_mode(TR_MODE_AUTONOMOUS)
        
        rsm.update()

        rsl.set_enabled(editor.state != "disabled")
        rsl.update(time.ticks_ms())

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