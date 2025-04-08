esptool erase_flash
esptool --baud 460800 write_flash 0x1000 ESP32_GENERIC-20241129-v1.24.1.bin
pause