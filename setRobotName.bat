@echo off
set /p ROBOT_NAME=Enter robot name: 
echo %ROBOT_NAME%>robot_name.txt

rem Push the file to the ESP32 using mpremote
mpremote fs cp robot_name.txt :
del robot_name.txt

echo Robot name set to "%ROBOT_NAME%"
pause
