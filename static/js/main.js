import { ZoneDrawer } from "./zone-drawer.js";
import { updateConfigFileOnServer } from "./server-update.service.js";
import { loadConfigForKey, saveConfigForKey } from "./storage.service.js";
import { onEnterZone, onLeftZone } from "./websocket.service.js";

const rawStreamCanvas = document.getElementById("raw-stream");
const rawStreamContext = rawStreamCanvas.getContext("2d");
const drawZoneButton = document.getElementById("draw-zone-area");
const drawMinAreaButton = document.getElementById("draw-min-area");
const drawMinBgAreaButton = document.getElementById("draw-min-bg-update-area");
const resetBgButton = document.getElementById("reset-bg");

resetBgButton.addEventListener("click", () =>
  fetch("zone/reset", { method: "POST" })
);

const img = new Image();
img.src = "/stream/raw";

img.addEventListener("load", () => {
  rawStreamCanvas.width = img.naturalWidth;
  rawStreamCanvas.height = img.naturalHeight;

  renderRawStream();
});

const zoneAreaDrawer = new ZoneDrawer(
  rawStreamCanvas,
  loadConfigForKey("zoneArea")
);
zoneAreaDrawer.onZoneUpdate((zone) => {
  updateConfigFileOnServer("/zone", {
    zoneArea: zone,
  });
  saveConfigForKey("zoneArea", zone);
  zoneAreaDrawer.removeEvents();
  drawZoneButton.classList.remove("active");
});

const minAreaDrawer = new ZoneDrawer(
  rawStreamCanvas,
  loadConfigForKey("minDetectionArea")
);
minAreaDrawer.onZoneUpdate((zone) => {
  updateConfigFileOnServer("/zone/min-detection-area", {
    minDetectionArea: calculateArea(zone),
  });
  saveConfigForKey("minDetectionArea", zone);
  minAreaDrawer.removeEvents();
  drawMinAreaButton.classList.remove("active");
});

const minBgUpdateDrawer = new ZoneDrawer(
  rawStreamCanvas,
  loadConfigForKey("minBgUpdateArea")
);
minBgUpdateDrawer.onZoneUpdate((zone) => {
  updateConfigFileOnServer("/zone/min-bg-update-area", {
    minBgUpdateArea: calculateArea(zone),
  });
  saveConfigForKey("minBgUpdateArea", zone);
  minBgUpdateDrawer.removeEvents();
  drawMinBgAreaButton.classList.remove("active");
});

function calculateArea(zone) {
  if (!zone || (!zone.topLeft && !zone.bottomRight)) {
    return undefined;
  }

  const width = Math.abs(zone.topLeft.x - zone.bottomRight.x);
  const height = Math.abs(zone.topLeft.y - zone.bottomRight.y);

  return width * height;
}

drawZoneButton.addEventListener("click", () => {
  zoneAreaDrawer.addEvents();
  minAreaDrawer.removeEvents();
  minBgUpdateDrawer.removeEvents();
  drawZoneButton.classList.add("active");
  drawMinAreaButton.classList.remove("active");
  drawMinBgAreaButton.classList.remove("active");
});

drawMinAreaButton.addEventListener("click", () => {
  minAreaDrawer.addEvents();
  zoneAreaDrawer.removeEvents();
  minBgUpdateDrawer.removeEvents();
  drawMinAreaButton.classList.add("active");
  drawZoneButton.classList.remove("active");
  drawMinBgAreaButton.classList.remove("active");
});

drawMinBgAreaButton.addEventListener("click", () => {
  minAreaDrawer.removeEvents();
  zoneAreaDrawer.removeEvents();
  minBgUpdateDrawer.addEvents();
  drawMinAreaButton.classList.remove("active");
  drawZoneButton.classList.remove("active");
  drawMinBgAreaButton.classList.add("active");
});

let zoneColor = "#FF0000";

onEnterZone(() => {
  zoneColor = "#FFFFFF";
});

onLeftZone(() => {
  zoneColor = "#FF0000";
});

function renderRawStream() {
  rawStreamContext.drawImage(img, 0, 0);

  drawZone(zoneAreaDrawer, zoneColor);
  drawZone(minAreaDrawer, "#00FF00");
  drawZone(minBgUpdateDrawer, "#0000FF");

  requestAnimationFrame(renderRawStream);
}

function drawZone(zoneDrawer, color) {
  const { zone } = zoneDrawer;

  if (zone.topLeft && zone.bottomRight) {
    const rectWidth = zone.bottomRight.x - zone.topLeft.x;
    const rectHeight = zone.bottomRight.y - zone.topLeft.y;

    rawStreamContext.strokeStyle = color;
    rawStreamContext.lineWidth = 10;
    rawStreamContext.strokeRect(
      zone.topLeft.x,
      zone.topLeft.y,
      rectWidth,
      rectHeight
    );
  }
}
