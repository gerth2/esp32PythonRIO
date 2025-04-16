

class _JoystickCtrl:
    def __init__(self):
        pass # TODO implement real joysticks

JOYCTRL = _JoystickCtrl()

class _KeyboardCtrl:
    """
    Keep this in line witht he web javascript:
    // Mapping from key to its bit index (max 16 keys = 2 bytes)
    const keyToBit = {
        'w': 0, //1
        'a': 1, //2
        's': 2, //4
        'd': 3, //8
        'q': 4,
        'e': 5,
        'z': 6,
        'x': 7,
        'c': 8,
        'Enter': 9,
        'ShiftLeft': 10,
        ' ': 11  // Spacebar
    };
    """
    def __init__(self):
        self.curKeycode = 0x0
    def w(self):
        return self.curKeycode & 0x1 != 0
    def a(self):
        return self.curKeycode & 0x2 != 0
    def s(self):
        return self.curKeycode & 0x4 != 0
    def d(self):
        return self.curKeycode & 0x8 != 0
    def q(self):
        return self.curKeycode & 0x10 != 0
    def e(self):
        return self.curKeycode & 0x20 != 0
    def z(self):
        return self.curKeycode & 0x40 != 0
    def x(self):
        return self.curKeycode & 0x80 != 0
    def c(self):
        return self.curKeycode & 0x100 != 0
    def enter(self):
        return self.curKeycode & 0x200 != 0
    def shift(self):
        return self.curKeycode & 0x400 != 0
    def space(self):
        return self.curKeycode & 0x800 != 0
    def setKeycode(self, keycode):
        self.curKeycode = keycode
    
        
KB = _KeyboardCtrl()