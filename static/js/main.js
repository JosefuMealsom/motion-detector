import { loadConfigForKey } from "./storage.service.js";
import { Zone } from "./zone.js";

const rawStreamCanvas = document.getElementById("raw-stream");
const rawStreamContext = rawStreamCanvas.getContext("2d");
const drawZoneButton = document.getElementById("draw-zone-area");
const drawMinAreaButton = document.getElementById("draw-min-area");
const resetBgButton = document.getElementById("reset-bg");

resetBgButton.addEventListener("click", () =>
  fetch("zone/reset", { method: "POST" })
);

const zone = new Zone(rawStreamCanvas, loadConfigForKey("zone-test"));

const img = new Image();
img.src = "/stream/raw";

img.addEventListener("load", () => {
  rawStreamCanvas.width = img.naturalWidth;
  rawStreamCanvas.height = img.naturalHeight;

  renderRawStream();
});

drawZoneButton.addEventListener("click", () => {
  zone.drawZone();
  drawZoneButton.classList.add("active");
  drawMinAreaButton.classList.remove("active");
});

drawMinAreaButton.addEventListener("click", () => {
  zone.drawMinDetectionArea();
  drawMinAreaButton.classList.add("active");
  drawZoneButton.classList.remove("active");
});

zone.onUpdate(() => {
  drawMinAreaButton.classList.remove("active");
  drawZoneButton.classList.remove("active");
});

function renderRawStream() {
  rawStreamContext.drawImage(img, 0, 0);

  zone.render();

  requestAnimationFrame(renderRawStream);
}
