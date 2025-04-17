import machine
import ubinascii

ROBOT_NAME_FILE = "robot_name.txt"

def get_fallback_name() -> str:
    uid = ubinascii.hexlify(machine.unique_id()).decode().upper()
    return f"{uid}"

def get_robot_name() -> str:
    try:
        with open(ROBOT_NAME_FILE, "r") as f:
            name = f.read().strip()
            if name:
                return name.upper()
    except Exception:
        pass
    return get_fallback_name()
