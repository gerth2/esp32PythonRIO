@echo off
mpremote mkdir :_private
mpremote mkdir :www
mpremote mkdir :wpilib

:: copy all source files
for %%f in (*.py) do (
    mpremote fs cp %%f :%%f
    if errorlevel 1 (
        echo Failed to copy %%f
        exit /b 1
    )
)

for %%f in (_private/*.py) do (
    mpremote fs cp _private/%%f :_private/%%f
    if errorlevel 1 (
        echo Failed to copy %%f
        exit /b 1
    )
)

for %%f in (wpilib/*.py) do (
    mpremote fs cp wpilib/%%f :wpilib/%%f
    if errorlevel 1 (
        echo Failed to copy %%f
        exit /b 1
    )
)

for %%f in (www/*.*) do (
    mpremote fs cp www/%%f :www/%%f
    if errorlevel 1 (
        echo Failed to copy %%f
        exit /b 1
    )
)

mpremote soft-reset

::Open shell to view program progress
mpremote