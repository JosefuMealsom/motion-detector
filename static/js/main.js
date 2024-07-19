import { ZoneDrawer } from "./zone-drawer.js";

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
zoneAreaDrawer.onZoneUpdate((zone) => updateZone(zone));

function renderRawStream() {
  rawStreamContext.drawImage(img, 0, 0);

  const { zone } = zoneAreaDrawer;

  if (zone.topLeft && zone.bottomRight) {
    const rectWidth = zone.bottomRight.x - zone.topLeft.x;
    const rectHeight = zone.bottomRight.y - zone.topLeft.y;

    rawStreamContext.strokeStyle = "#FF0000";
    rawStreamContext.lineWidth = 10;
    rawStreamContext.strokeRect(
      zone.topLeft.x,
      zone.topLeft.y,
      rectWidth,
      rectHeight
    );
  }

  requestAnimationFrame(renderRawStream);
}

function updateZone(zoneObject) {
  const update = async () => {
    const response = await fetch("/zone", {
      method: "POST",
      body: JSON.stringify(zoneObject),
      headers: { "Content-Type": "application/json" },
    });
  };

  saveZoneConfig(zoneObject);

  update();
}

function loadZoneConfig() {
  const zoneString = localStorage.getItem("zoneConfig");
  if (zoneString) {
    return JSON.parse(zoneString);
  }

  return {
    topLeft: undefined,
    bottomRight: undefined,
  };
}

function saveZoneConfig(zoneObject) {
  localStorage.setItem("zoneConfig", JSON.stringify(zoneObject));
}
