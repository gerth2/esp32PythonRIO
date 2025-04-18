# Why

* "Mom Can we have XRP?"
* "No, we have XRP at home."
* at home...

Economical robot platform that emulates the "look and feel" of frc programming as best as possible.

And cuz Chris just wanted to try it.

# TODO

* Test wheel rotation sensors
* design PCB
* write docs
* read in joystick data
* Integrate plots to main page as flyout

# Docs

* https://www.silabs.com/developer-tools/usb-to-uart-bridge-vcp-drivers?tab=downloads - usb driver needed for boards
* https://docs.espressif.com/projects/esptool/en/latest/esp32/ - esptool for uploading basic firmware
* https://micropython.org/download/ESP32_GENERIC/ - micropython install
  * Used v1.24.1 (2024-11-29) .bin / [.app-bin] / [.elf] / [.map] / [Release notes] (latest) normal release
* https://docs.micropython.org/en/latest/reference/mpremote.html
* https://docs.micropython.org/en/latest/esp32/quickref.html

# Setup

```
pip install esptool
pip install mpremote
pip install pyserial
```

## Flash Base Firmware

Micropython needs to be installed on the ESP32

Connect to the device with USB

Double-click `base_image/flash.bat`

## Set robot name

Robots need a unique name to differentiate them from others.

Double-click `setRobotName.bat`

# Deploy Robot Application

Double-click `deploy.bat`

# Start Editing Code

Connect to the wifi network named `MINIBOT-<NAME>`

Visit `http://10.17.36.2` in a browser
