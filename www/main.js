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

function setEditorDisabled(isDisabled) {
    const editor = document.getElementById("editor");
    const overlay = document.querySelector(".editor-disabled-overlay");

    if (isDisabled) {
        editor.setAttribute("disabled", "true"); // Disable the editor
        overlay.style.display = "flex"; // Show the overlay
    } else {
        editor.removeAttribute("disabled"); // Enable the editor
        overlay.style.display = "none"; // Hide the overlay
    }
}

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

function resetFile(){
    fetch('/resetFile', { method: 'POST'})
    .then(res => {
        if (!res.ok) throw new Error("Failed to reset robot.py");
        else {
            fetchCurrentCode();
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

document.getElementById('reset').onclick = () => {
    resetFile()
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
    if (!editor.disabled) {
        setEditorDisabled(false); // Disable overlay
        editor.focus(); // Focus on the editor
    } else {
        setEditorDisabled(true); // Enable overlay
    }
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
function fetchCurrentCode(){
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
}


function updateDisplayedRobotState(batVoltage, codeRunning, statusMsg){
    if(isConnected){
        statusBatteryEl.innerHTML = batVoltage.toString() + " V";
        statusCommEl.innerHTML = "<span class=\"status-check true\">✔</span></td></tr>"
        statusCodeEl.innerHTML = codeRunning ? "<span class=\"status-check true\">✔</span></td></tr>" : "<span class=\"status-check false\" >✘</span></td></tr>"
        statusJoystickEl.innerHTML = "<span class=\"status-check false\" >✘</span></td></tr>"
        statusMsgEl.innerHTML = statusMsg;
    } else {
        statusBatteryEl.innerHTML = " --- V"
        statusCommEl.innerHTML = "<span class=\"status-check false\" >✘</span></td></tr>"
        statusCodeEl.innerHTML = "<span class=\"status-check false\" >✘</span></td></tr>"
        statusJoystickEl.innerHTML = "<span class=\"status-check false\" >✘</span></td></tr>"
        statusMsgEl.innerHTML = "No Robot <br> Communication";
    }
}

function updateConfig(robotName){
    statRobotNameEl.innerHTML = robotName;
}

// global websocket object
let ws;

function connectWebSocket() {
    ws = new WebSocket(`ws://${location.hostname}:8266`);

    ws.onopen = function () {
        console.log("Connected to ESP32 WebSocket server");
        isConnected = true;
    };

    ws.onmessage = function (event) {
        console.log("Received from ESP32:", event.data);

        let jsonData;
        try {
            jsonData = JSON.parse(event.data);
        } catch (e) {
            console.error("Failed to parse JSON:", e);
            return;
        }

        if (jsonData.hasOwnProperty("consoleOutput")) {
            consoleEl.textContent += jsonData.consoleOutput;
            consoleEl.scrollTop = consoleEl.scrollHeight;
        }

        if (jsonData.hasOwnProperty("robotState")) {
            let data = jsonData.robotState;
            updateDisplayedRobotState(data.batVoltage, data.codeRunning, data.statusMsg);
        }

        if (jsonData.hasOwnProperty("robotConfig")) {
            let data = jsonData.robotConfig;
            updateConfig(data.robotName);
        }

        if (jsonData.hasOwnProperty("plotData")) {
            handleNewPlotData(jsonData.plotData);
        }
    };

    ws.onerror = function (error) {
        console.error("WebSocket error:", error);
        cleanupAndRetry();
    };

    ws.onclose = function () {
        console.log("WebSocket connection closed");
        cleanupAndRetry();
    };
}

function cleanupAndRetry() {
    isConnected = false;
    updateDisplayedRobotState(" --- ", " --- ", false, "No Robot <br> Communication");

    // Wait 0.5 seconds and then reconnect
    setTimeout(connectWebSocket, 500);
}

let flyoutOpen = false;

function toggleFlyout() {
    const panel = document.getElementById('flyout-panel');
    const tab = document.getElementById('flyout-tab');

    if (flyoutOpen) {
        panel.classList.remove('open');
        tab.innerText = '🗠 ▶';
        onFlyoutRetract();
    } else {
        panel.classList.add('open');
        tab.innerText = '🗠 ◀';
        onFlyoutExtend();
    }

    flyoutOpen = !flyoutOpen;
}

function onFlyoutExtend() {
    console.log("Plots Flyout extended");
    ws.send(JSON.stringify({ plotConfig: { enabled: true } }));

}

function onFlyoutRetract() {
    console.log("Plots Flyout retracted");
    ws.send(JSON.stringify({ plotConfig: { enabled: false } }));

}


// make sure editor is up to date
fetchCurrentCode();
// Start connection initially
connectWebSocket();
