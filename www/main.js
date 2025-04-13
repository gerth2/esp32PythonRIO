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
let currentMode = 'teleop';
let isConnected = false;

function deploy(){
    fetch('/deploy', { method: 'POST', body: editor.value })
    .then(res => {
        if (!res.ok) throw new Error("Failed to deploy robot.py");
        else {
            isChanged = false;
            updateStatus();
        }
        return res.text();
    })
}

// Deploy, Download, Upload logic
document.getElementById('deploy').onclick = () => {
    deploy()
};

//Handle ctrl-s as deploy
editor.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault(); // Prevent the default save action
        deploy();
    }
});

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
            updateHighlight();
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
    ws.send(JSON.stringify({
        stateCmd: state
    }));
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
        updateHighlight();
        isChanged = false;
        updateStatus();
    })
    .catch(err => {
        console.error('Error loading robot.py:', err);
        status.textContent = 'Error loading file';
    });

function updateDisplayedRobotState(robotName, batVoltage, codeRunning, statusMsg){
    if(isConnected){
        statRobotNameEl.innerHTML = data.robotName;
        statusBatteryEl.innerHTML = data.batVoltage.toString() + " V";
        statusCommEl.innerHTML = "<span class=\"status-check true\">✔</span></td></tr>"
        statusCodeEl.innerHTML = data.codeRunning ? "<span class=\"status-check true\">✔</span></td></tr>" : "<span class=\"status-check false\" >✘</span></td></tr>"
        statusJoystickEl.innerHTML = "<span class=\"status-check false\" >✘</span></td></tr>"
        statusMsgEl.innerHTML = data.statusMsg;
    } else {
        statRobotNameEl.innerHTML = " --- ";
        statusBatteryEl.innerHTML = " --- V"
        statusCommEl.innerHTML = "<span class=\"status-check false\" >✘</span></td></tr>"
        statusCodeEl.innerHTML = "<span class=\"status-check false\" >✘</span></td></tr>"
        statusJoystickEl.innerHTML = "<span class=\"status-check false\" >✘</span></td></tr>"
        statusMsgEl.innerHTML = "No Robot <br> Communication";
    }
}

const ws = new WebSocket("ws://10.17.36.2:8266");

ws.onopen = function () {
    console.log("Connected to ESP32 WebSocket server");
    isConnected = true;
};

ws.onmessage = function (event) {
    console.log("Received from ESP32:", event.data);

    jsonData = JSON.parse(event.data); 

    if(jsonData.hasOwnProperty("consoleOutput")){
        consoleEl.textContent += jsonData.consoleOutput;
        consoleEl.scrollTop = consoleEl.scrollHeight; // Scroll to the bottom
    }

    if(jsonData.hasOwnProperty("robotState")){
        data = jsonData.robotState;
        updateDisplayedRobotState(data.robotName, data.batVoltage, data.codeRunning, data.statusMsg);
    }



};

ws.onerror = function (error) {
    console.error("WebSocket error:", error);
    isConnected = false;
    updateDisplayedRobotState(" --- ", " --- ", false, "No Robot <br> Communication");
    //TODO reopen websocket
};

ws.onclose = function () {
    console.log("WebSocket connection closed");
    isConnected = false;
    updateDisplayedRobotState(" --- ", " --- ", false, "No Robot <br> Communication");
};
