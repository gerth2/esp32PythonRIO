
let rawData = [];
let signals = [];
let selectedSignals = new Set();
let lastTimeReceived = 0;

const canvas = document.getElementById("plot");
const ctx = canvas.getContext("2d");

function resizeCanvas() {
  canvas.width = canvas.clientWidth;
  canvas.height = canvas.clientHeight*0.9;
  drawPlot();
}

function drawPlot() {
  if (selectedSignals.size === 0 || rawData.length === 0) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    return;
  }

  const now = rawData[rawData.length - 1].TIME;
  const minTime = now - 15; // Show last 15 seconds
  const visibleData = rawData.filter(d => d.TIME >= minTime);

  const times = visibleData.map(d => d.TIME);
  const selectedData = visibleData.map(d => {
    let entry = { TIME: d.TIME };
    selectedSignals.forEach(s => entry[s] = d[s]);
    return entry;
  });

  const allValues = selectedData.flatMap(d =>
    Object.entries(d)
      .filter(([k, v]) => k !== "TIME" && typeof v === "number")
      .map(([_, v]) => v)
  );

  const minValue = Math.min(...allValues);
  const maxValue = Math.max(...allValues);

  const margin = 50;
  const width = canvas.width - 2 * margin;
  const height = canvas.height - 2 * margin;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = "#000";
  ctx.strokeRect(margin, margin, width, height);

  const xScale = time => margin + ((time - minTime) / 15) * width;
  const yScale = value => margin + height - ((value - minValue) / (maxValue - minValue)) * height;

  // Axis labels
  ctx.fillStyle = "#000";
  ctx.textAlign = "center";
  ctx.fillText("Time (s)", canvas.width / 2, canvas.height - 5);
  ctx.textAlign = "left";
  ctx.fillText(`Y (${minValue.toFixed(2)} - ${maxValue.toFixed(2)})`, 5, margin - 10);

  // Y-axis ticks
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for (let i = 0; i <= 5; i++) {
    const yVal = minValue + (i / 5) * (maxValue - minValue);
    const y = yScale(yVal);
    ctx.fillText(yVal.toFixed(2), margin - 5, y);
    ctx.strokeStyle = "#ccc";
    ctx.beginPath();
    ctx.moveTo(margin, y);
    ctx.lineTo(canvas.width - margin, y);
    ctx.stroke();
  }

  // X-axis ticks
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  for (let i = 0; i <= 5; i++) {
    const t = minTime + (i / 5) * 15;
    const x = xScale(t);
    ctx.fillText(t.toFixed(1), x, canvas.height - margin + 5);
    ctx.strokeStyle = "#ccc";
    ctx.beginPath();
    ctx.moveTo(x, margin);
    ctx.lineTo(x, canvas.height - margin);
    ctx.stroke();
  }

  // Plot signals
  const colors = ["red", "blue", "green", "orange", "purple", "brown", "magenta", "teal"];
  let colorIndex = 0;

  selectedSignals.forEach(signal => {
    ctx.strokeStyle = colors[colorIndex % colors.length];
    ctx.beginPath();
    selectedData.forEach((d, i) => {
      const x = xScale(d.TIME);
      const y = yScale(d[signal]);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    colorIndex++;
  });
}

function createCheckboxes() {
  const container = document.getElementById("signal-list");
  const oldSelections = new Set(selectedSignals);
  container.innerHTML = "";
  signals.forEach(signal => {
    const label = document.createElement("label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = signal;
    checkbox.checked = oldSelections.has(signal);
    checkbox.onchange = () => {
      if (checkbox.checked) selectedSignals.add(signal);
      else selectedSignals.delete(signal);
      drawPlot();
    };
    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(" " + signal));
    container.appendChild(label);
    container.appendChild(document.createElement("br"));
  });
}

function handleNewPlotData(data) {
  if (data.TIME <= lastTimeReceived) return;
  rawData.push(data);
  lastTimeReceived = data.TIME;

  // Clean old data
  const cutoff = data.TIME - 15;
  rawData = rawData.filter(d => d.TIME >= cutoff);

  const keys = Object.keys(data).filter(k => k !== "TIME");
  const sortedKeys = keys.slice().sort();
  const sortedSignals = signals.slice().sort();
  if (JSON.stringify(sortedKeys) !== JSON.stringify(sortedSignals)) {
    signals = keys;
    createCheckboxes();
  }

  drawPlot();
}

window.addEventListener("resize", resizeCanvas);
resizeCanvas();