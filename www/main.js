const editor = document.getElementById('editor');
const status = document.getElementById('status');
const enableBtn = document.getElementById('enable');
const disableBtn = document.getElementById('disable');
const consoleEl = document.getElementById('console');
const teleopBtn = document.getElementById('teleopBtn');
const autoBtn = document.getElementById('autoBtn');
const statRobotNameEl = document.getElementById('status-robot-name');
const statusBatteryEl = document.getElementById('status-battery');
const statusCommEl = document.getElementById('status-comm');
const statusCodeEl = document.getElementById('status-code');
const statusJoystickEl = document.getElementById('status-joystick');
const statusMsgEl = document.getElementById('status-message');
let isChanged = false;
let isEnabled = false;
let currentMode = 'disabled';

// Deploy, Download, Upload logic
document.getElementById('deploy').onclick = () => {
    fetch('/deploy', { method: 'POST', body: editor.value });
    isChanged = false;
    updateStatus();
};

document.getElementById('download').onclick = () => {
    const blob = new Blob([editor.value], { type: 'text/plain' });
    const link = document.createElement('a');
    link.download = 'robot.py';
    link.href = URL.createObjectURL(blob);
    link.click();
};

document.getElementById('upload').onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
        file.text().then(text => {
            editor.value = text;
            isChanged = true;
            updateStatus();
        });
    }
};

editor.addEventListener('input', () => {
    isChanged = true;
    updateStatus();
});

function updateStatus() {
    status.textContent = isChanged ? 'Modified' : 'Unchanged';
}

// Driver station logic
function updateEditorLock() {
    editor.disabled = isEnabled;
}

function sendState() {
    const state = isEnabled ? currentMode : "disabled";
    fetch('/stateCmd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state })
    });
}

enableBtn.onclick = () => {
    isEnabled = true;
    updateEditorLock();
    sendState();
};
disableBtn.onclick = () => {
    isEnabled = false;
    updateEditorLock();
    sendState();
};

updateEditorLock(); // Initial lock

// Toggle mode buttons
teleopBtn.onclick = () => {
    if (currentMode !== 'teleop') {
        currentMode = 'teleop';
        teleopBtn.classList.add('active');
        autoBtn.classList.remove('active');
        sendState();
    }
};

autoBtn.onclick = () => {
    if (currentMode !== 'auto') {
        currentMode = 'auto';
        autoBtn.classList.add('active');
        teleopBtn.classList.remove('active');
        sendState();
    }
};

// Load robot.py from server on page load
fetch('/robot.py')
    .then(res => {
        if (!res.ok) throw new Error("Failed to load robot.py");
        return res.text();
    })
    .then(text => {
        editor.value = text;
        isChanged = false;
        updateStatus();
    })
    .catch(err => {
        console.error('Error loading robot.py:', err);
        status.textContent = 'Error loading file';
    });

// Polling to fetch console log data every 1 second
function fetchConsoleLog() {
    fetch('/console')
        .then(response => response.text())
        .then(data => {
            consoleEl.textContent = data;
            consoleEl.scrollTop = consoleEl.scrollHeight; // Scroll to the bottom
        })
        .catch(err => {
            console.error('Error fetching console log:', err);
        });
}

setInterval(fetchConsoleLog, 500);


// Polling to fetch robot state log data every 1 second
function fetchRobotState() {
    fetch('/curState')
        .then(response => response.json())
        .then(data => {
            statRobotNameEl.innerHTML = data.robotName;
            statusBatteryEl.innerHTML = data.batVoltage.toString() + " V";
            statusCommEl.innerHTML = "<span class=\"status-check true\">✔</span></td></tr>"
            statusCodeEl.innerHTML = data.codeRunning ? "<span class=\"status-check true\">✔</span></td></tr>" : "<span class=\"status-check false\" >✘</span></td></tr>"
            statusJoystickEl.innerHTML = "<span class=\"status-check false\" >✘</span></td></tr>"
            statusMsgEl.innerHTML = data.statusMsg;
        })
        .catch(err => {
            statRobotNameEl.innerHTML = " --- ";
            statusBatteryEl.innerHTML = " --- V"
            statusCommEl.innerHTML = "<span class=\"status-check false\" >✘</span></td></tr>"
            statusCodeEl.innerHTML = "<span class=\"status-check false\" >✘</span></td></tr>"
            statusJoystickEl.innerHTML = "<span class=\"status-check false\" >✘</span></td></tr>"
            statusMsgEl.innerHTML = "No Robot <br> Communication";
        });
}

setInterval(fetchRobotState, 1000);


// Ensure that "tab" in the text area causes a tab character to be inserted instead of moving focus
document.getElementById('editor').addEventListener('keydown', function (e) {
    if (e.key === 'Tab') {
        e.preventDefault();  // Prevent default tab behavior (moving focus)

        // Get the current position of the cursor
        const textarea = e.target;
        const cursorPos = textarea.selectionStart;

        // Get the text before and after the cursor
        const textBefore = textarea.value.substring(0, cursorPos);
        const textAfter = textarea.value.substring(cursorPos);

        // Insert a tab character
        textarea.value = textBefore + '    ' + textAfter;

        // Move the cursor position after the inserted tab
        textarea.selectionStart = textarea.selectionEnd = cursorPos + 4;
    }
});