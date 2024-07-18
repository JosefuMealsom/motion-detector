const rawStreamCanvas = document.getElementById("raw-stream");
const rawStreamContext = rawStreamCanvas.getContext("2d");

const img = new Image();
img.src = "/stream/raw";

img.addEventListener("load", () => {
  rawStreamCanvas.width = img.naturalWidth;
  rawStreamCanvas.height = img.naturalHeight;

  renderRawStream();
  setupZoneDrawingEvents(rawStreamCanvas);
});

zoneRectangle = loadZoneConfig();

function renderRawStream() {
  rawStreamContext.drawImage(img, 0, 0);

  if (zoneRectangle.topLeft && zoneRectangle.bottomRight) {
    const rectWidth = zoneRectangle.bottomRight.x - zoneRectangle.topLeft.x;
    const rectHeight = zoneRectangle.bottomRight.y - zoneRectangle.topLeft.y;

    rawStreamContext.strokeStyle = "#FF0000";
    rawStreamContext.lineWidth = 10;
    rawStreamContext.strokeRect(
      zoneRectangle.topLeft.x,
      zoneRectangle.topLeft.y,
      rectWidth,
      rectHeight
    );
  }

  requestAnimationFrame(renderRawStream);
}

function setupZoneDrawingEvents(canvasElement) {
  let mouseDown = false;
  canvasElement.addEventListener("mousedown", (evt) => {
    mouseDown = true;
    var rect = canvasElement.getBoundingClientRect();

    zoneRectangle.topLeft = convertHtmlPosToCanvasPos(
      rawStreamCanvas,
      evt.clientX - rect.left,
      evt.clientY - rect.top
    );
    zoneRectangle.bottomRight = undefined;
  });
  canvasElement.addEventListener("mousemove", (evt) => {
    if (!mouseDown) return;
    var rect = canvasElement.getBoundingClientRect();

    zoneRectangle.bottomRight = convertHtmlPosToCanvasPos(
      rawStreamCanvas,
      evt.clientX - rect.left,
      evt.clientY - rect.top
    );
  });

  canvasElement.addEventListener("mouseup", (evt) => {
    updateZone(zoneRectangle);

    mouseDown = false;
  });
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
  zoneString = localStorage.getItem("zoneConfig");
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

function convertHtmlPosToCanvasPos(canvasElement, x, y) {
  const cw = canvasElement.width;
  const w = canvasElement.clientWidth;

  const htmlToCanvasRatio = cw / w;

  return {
    x: Math.round(x * htmlToCanvasRatio),
    y: Math.round(y * htmlToCanvasRatio),
  };
}
