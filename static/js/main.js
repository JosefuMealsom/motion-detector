import { loadConfigForKey, saveConfigForKey } from "./storage.service.js";
import { onEnterZone, onLeftZone } from "./websocket.service.js";
import { Zone } from "./zone.js";
import { RangeInput } from "./range-input.js";

const rawStreamCanvas = document.getElementById("raw-stream");
const rawStreamContext = rawStreamCanvas.getContext("2d");
const drawZoneButton = document.getElementById("draw-zone-area");
const drawMinAreaButton = document.getElementById("draw-min-area");
const resetBgButton = document.getElementById("reset-bg");

resetBgButton.addEventListener("click", () =>
  fetch("zone/reset", { method: "POST" })
);

const config = loadConfigForKey("zone") || {};

const thresholdInput = new RangeInput(
  "threshold",
  "threshold-value",
  config["threshold"]
);
const minTimeInput = new RangeInput(
  "min-time",
  "min-time-value",
  config["minTime"]
);
const scaleInput = new RangeInput("scale", "scale-value", config["scale"]);

const erosionInput = new RangeInput(
  "erosion",
  "erosion-value",
  config["erosion"]
);
const dilationInput = new RangeInput(
  "dilation",
  "dilation-value",
  config["dilation"]
);
const blurFilterInput = new RangeInput(
  "blur-filter-size",
  "blur-filter-size-value",
  config["blurFilterSize"]
);

const zone = new Zone(rawStreamCanvas, config);

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

thresholdInput.onChange(updateConfigOnServer);
minTimeInput.onChange(updateConfigOnServer);
scaleInput.onChange(updateConfigOnServer);
erosionInput.onChange(updateConfigOnServer);
dilationInput.onChange(updateConfigOnServer);
blurFilterInput.onChange(updateConfigOnServer);

zone.onUpdate(() => {
  drawMinAreaButton.classList.remove("active");
  drawZoneButton.classList.remove("active");

  updateConfigOnServer();
});

async function updateConfigOnServer() {
  const data = {
    zoneArea: zone.zoneDrawer.zone,
    minDetectionArea: zone.minAreaDrawer.zone,
    threshold: thresholdInput.getValue(),
    minTime: minTimeInput.getValue(),
    scale: scaleInput.getValue(),
    erosion: erosionInput.getValue(),
    dilation: dilationInput.getValue(),
    blurFilterSize: blurFilterInput.getValue(),
  };

  const stringifiedData = JSON.stringify({
    ...data,
    minDetectionArea: zone.minDetectionArea(),
  });

  await fetch("zone", {
    method: "POST",
    body: stringifiedData,
    headers: { "Content-Type": "application/json" },
  });

  saveConfigForKey("zone", data);
}

onEnterZone(() => zone.setActiveState(true));
onLeftZone(() => zone.setActiveState(false));

function renderRawStream() {
  rawStreamContext.drawImage(img, 0, 0);

  zone.render();

  requestAnimationFrame(renderRawStream);
}
