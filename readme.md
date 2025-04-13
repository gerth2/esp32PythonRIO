# Why

* "Mom Can we have XRP?"
* "No, we have XRP at home."
* at home...

Economical robot platform that emulates the "look and feel" of frc programming as best as possible.

And cuz Chris just wanted to try it.

# TODO

* read in joystick data
* Design wpilib class replicas
* Improve UI clarity on which mode you are in
* Test wheel rotation sensors
* debug dataplotter
* Add reset-source-code logic
* verify periodic timing
* design PCB
* write docs


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

# Deploy

Run `deploy.bat`

