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

// Keep track of current state
let keyState = 0;
let prevKeyState = 0;

// Set of currently pressed keys (for shift distinction)
const pressedKeys = new Set();

function updateKeyState(key, isDown) {
    if (!(key in keyToBit)) return;

    const bitIndex = keyToBit[key];
    if (isDown) {
        keyState |= (1 << bitIndex);
        pressedKeys.add(key);
    } else {
        keyState &= ~(1 << bitIndex);
        pressedKeys.delete(key);
    }

    if(keyState != prevKeyState){
        // Send JSON with the packed key state
        const payload = {
            keyboardData: keyState
        };

        fetch('/controllerInfo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        prevKeyState = keyState;
    }


}

// Normalize key event codes
function normalizeKey(event) {
    if (event.code === 'ShiftLeft' || event.code === 'ShiftRight') return 'ShiftLeft'; // treat both shifts as same
    if (event.key === ' ') return ' ';
    if (event.key === 'Enter') return 'Enter';
    return event.key.toLowerCase(); // For w/a/s/d etc.
}

document.addEventListener('keydown', (event) => {
    const key = normalizeKey(event);
    updateKeyState(key, true);
});

document.addEventListener('keyup', (event) => {
    const key = normalizeKey(event);
    updateKeyState(key, false);
});
