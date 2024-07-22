import { ZoneDrawer } from "./zone-drawer.js";
import { updateMinArea, updateZone } from "./server-update.service.js";
import {
  loadMinAreaConfig,
  loadZoneConfig,
  saveMinAreaConfig,
  saveZoneConfig,
} from "./storage.service.js";

const rawStreamCanvas = document.getElementById("raw-stream");
const rawStreamContext = rawStreamCanvas.getContext("2d");

const img = new Image();
img.src = "/stream/raw";

img.addEventListener("load", () => {
  rawStreamCanvas.width = img.naturalWidth;
  rawStreamCanvas.height = img.naturalHeight;

  renderRawStream();
});

const zoneAreaDrawer = new ZoneDrawer(rawStreamCanvas, loadZoneConfig());
zoneAreaDrawer.onZoneUpdate((zone) => {
  updateZone(zoneAreaDrawer.zone);
  saveZoneConfig(zone);
  zoneAreaDrawer.removeEvents();
  drawZoneButton.classList.remove("active");
});

const minAreaDrawer = new ZoneDrawer(rawStreamCanvas, loadMinAreaConfig());
minAreaDrawer.onZoneUpdate((zone) => {
  updateMinArea(calculateArea(minAreaDrawer.zone));
  saveMinAreaConfig(zone);
  minAreaDrawer.removeEvents();
  drawMinAreaButton.classList.remove("active");
});

function calculateArea(zone) {
  if (!zone || (!zone.topLeft && !zone.bottomRight)) {
    return undefined;
  }

  const width = Math.abs(zone.topLeft.x - zone.bottomRight.x);
  const height = Math.abs(zone.topLeft.y - zone.bottomRight.y);

  return width * height;
}

const drawZoneButton = document.getElementById("draw-zone-area");
const drawMinAreaButton = document.getElementById("draw-min-area");

drawZoneButton.addEventListener("click", () => {
  zoneAreaDrawer.addEvents();
  minAreaDrawer.removeEvents();
  drawZoneButton.classList.add("active");
  drawMinAreaButton.classList.remove("active");
});

drawMinAreaButton.addEventListener("click", () => {
  minAreaDrawer.addEvents();
  zoneAreaDrawer.removeEvents();
  drawMinAreaButton.classList.add("active");
  drawZoneButton.classList.remove("active");
});

function renderRawStream() {
  rawStreamContext.drawImage(img, 0, 0);

  drawZone(zoneAreaDrawer, "#FF0000");
  drawZone(minAreaDrawer, "#00FF00");

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
