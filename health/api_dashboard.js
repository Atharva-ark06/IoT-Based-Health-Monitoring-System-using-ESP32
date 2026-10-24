"use strict";

const byId = (id) => document.getElementById(id);
const loginPanel = byId("loginPanel");
const dashboardPanel = byId("dashboardPanel");
const loginStatus = byId("loginStatus");
const historyStatus = byId("historyStatus");
let latestReadings = [];

function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("error", isError);
}

function showDashboard(visible) {
  loginPanel.classList.toggle("hidden", visible);
  dashboardPanel.classList.toggle("hidden", !visible);
  byId("logoutButton").classList.toggle("hidden", !visible);
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    credentials: "same-origin",
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  let payload = {};
  try { payload = await response.json(); } catch { /* Non-JSON errors are handled generically. */ }
  if (!response.ok) {
    const error = new Error(response.status === 401 ? "Please sign in again." : "Request failed. Check the API and try again.");
    error.status = response.status;
    throw error;
  }
  return payload;
}

function drawTemperatureChart(readings) {
  const canvas = byId("temperatureChart");
  const context = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  context.clearRect(0, 0, width, height);
  if (!readings.length) {
    byId("chartDescription").textContent = "No readings available to plot.";
    return;
  }
  const points = [...readings].reverse();
  const values = points.map((item) => Number(item.temperature)).filter(Number.isFinite);
  if (!values.length) return;
  const min = Math.min(...values) - 0.5;
  const max = Math.max(...values) + 0.5;
  const x = (index) => 30 + index * (width - 60) / Math.max(points.length - 1, 1);
  const y = (value) => height - 28 - ((value - min) / (max - min || 1)) * (height - 56);
  context.strokeStyle = "#34445f";
  context.lineWidth = 1;
  for (let grid = 0; grid < 4; grid += 1) {
    const gy = 20 + grid * (height - 48) / 3;
    context.beginPath(); context.moveTo(24, gy); context.lineTo(width - 20, gy); context.stroke();
  }
  context.strokeStyle = "#6ee7d8";
  context.lineWidth = 3;
  context.beginPath();
  values.forEach((value, index) => {
    if (index === 0) context.moveTo(x(index), y(value));
    else context.lineTo(x(index), y(value));
  });
  context.stroke();
  context.fillStyle = "#edf3ff";
  values.forEach((value, index) => {
    context.beginPath(); context.arc(x(index), y(value), 4, 0, Math.PI * 2); context.fill();
  });
  byId("chartDescription").textContent = values.length + " temperature samples shown. Values are sensor reports, not clinical conclusions.";
}

function renderReadings(readings) {
  latestReadings = readings;
  const latest = readings[0];
  byId("temperatureValue").textContent = latest ? Number(latest.temperature).toFixed(1) : "—";
  byId("bpmValue").textContent = latest ? String(latest.bpm) : "—";
  byId("deviceValue").textContent = latest ? latest.device_id : "—";
  byId("updatedValue").textContent = latest ? "Received " + new Date(latest.received_at).toLocaleString() : "No readings yet";

  const body = byId("readingsBody");
  body.replaceChildren();
  if (!readings.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.textContent = "No readings received yet. Start the simulator to create synthetic data.";
    row.append(cell); body.append(row);
  } else {
    for (const reading of readings) {
      const row = document.createElement("tr");
      for (const value of [
        new Date(reading.timestamp).toISOString(),
        reading.device_id,
        Number(reading.temperature).toFixed(1),
        String(reading.bpm),
      ]) {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.append(cell);
      }
      body.append(row);
    }
  }
  drawTemperatureChart(readings);
  setStatus(historyStatus, "Loaded " + readings.length + " reading(s).");
}

async function loadReadings() {
  setStatus(historyStatus, "Loading readings…");
  try {
    const result = await requestJson("/api/v1/dashboard/readings?limit=100", { method: "GET", headers: {} });
    renderReadings(result.readings || []);
  } catch (error) {
    if (error.status === 401) showDashboard(false);
    setStatus(historyStatus, error.message, true);
  }
}

byId("loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus(loginStatus, "Signing in…");
  const passwordInput = byId("password");
  try {
    await requestJson("/api/v1/dashboard/login", {
      method: "POST",
      body: JSON.stringify({ password: passwordInput.value }),
    });
    passwordInput.value = "";
    showDashboard(true);
    await loadReadings();
  } catch (error) {
    setStatus(loginStatus, error.message === "Please sign in again." ? error.message : "Sign-in failed. Check credentials and server configuration.", true);
  }
});

byId("refreshButton").addEventListener("click", loadReadings);
byId("logoutButton").addEventListener("click", async () => {
  try {
    await requestJson("/api/v1/dashboard/logout", { method: "POST", body: "{}" });
  } catch { /* Clear the visible session state even if the server is unreachable. */ }
  showDashboard(false);
  setStatus(loginStatus, "You have been signed out.");
});

// Do not assume a browser session exists; the protected endpoint is authoritative.
loadReadings().then(() => {
  if (historyStatus.classList.contains("error")) showDashboard(false);
  else showDashboard(true);
});
