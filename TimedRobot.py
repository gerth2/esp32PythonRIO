
# Robot modes as simple constants
TR_MODE_DISABLED = 0
TR_MODE_TELEOP = 1
TR_MODE_AUTONOMOUS = 2
TR_MODE_TEST = 3

# Mapping without Enum
MODE_METHOD_PREFIXES = {
    TR_MODE_DISABLED: "disabled",
    TR_MODE_TELEOP: "teleop",
    TR_MODE_AUTONOMOUS: "autonomous",
    TR_MODE_TEST: "test",
}

class TimedRobot:
    """
    Base class users subclass to implement init/update/exit methods
    for each mode: disabled, teleop, autonomous, test.
    """
    def disabledInit(self): pass
    def disabledPeriodic(self): pass
    def disabledExit(self): pass

    def teleopInit(self): pass
    def teleopPeriodic(self): pass
    def teleopExit(self): pass

    def autonomousInit(self): pass
    def autonomousPeriodic(self): pass
    def autonomousExit(self): pass

    def testInit(self): pass
    def testPeriodic(self): pass
    def testExit(self): pass

    def robotPeriodic(self): pass


class MainStateMachine:
    def __init__(self, handler: TimedRobot):
        self.handler = handler
        self._current_mode = TR_MODE_DISABLED
        self._desired_mode = TR_MODE_DISABLED
        self._entered = False

        self._callInit(self._current_mode)

    def set_mode(self, mode):
        """Request a transition to a new mode."""
        if mode != self._desired_mode:
            self._desired_mode = mode

    def get_mode(self):
        """Get the current active mode."""
        return self._current_mode

    def update(self):
        """Step the state machine forward. Call periodically."""
        if self._current_mode != self._desired_mode:
            self._callExit(self._current_mode)
            self._current_mode = self._desired_mode
            self._callInit(self._current_mode)

        self._callPeriodic(self._current_mode)

    def _get_method(self, mode, suffix: str):
        prefix = MODE_METHOD_PREFIXES[mode]
        return getattr(self.handler, prefix + suffix[0].upper() + suffix[1:])

    def _callInit(self, mode):
        self._get_method(mode, "init")()
        self._entered = True

    def _callPeriodic(self, mode):
        self._get_method(mode, "periodic")()
        self.handler.robotPeriodic()

    def _callExit(self, mode):
        if self._entered:
            self._get_method(mode, "exit")()
            self._entered = False
