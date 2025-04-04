import serial

#connect to COM 3
ser = serial.Serial('COM3', 115200, timeout=None)

#open serial port
if ser.is_open:
    # Print all output until ctrl-c is hit on the terminal
    try:
        while True:
            # Read a line from the serial port
            line = ser.readline().decode('utf-8').rstrip()
            # Print the line to the terminal
            print(line)
    except KeyboardInterrupt:
        # Close the serial port when done
        ser.close()
        print("Serial port closed.")