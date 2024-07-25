export class ZoneDrawer {
  mouseStart = undefined;
  mouseEnd = undefined;
  oldZoneObject = undefined;
  mouseDown = false;
  onZoneUpdateCallback = undefined;

  constructor(canvasElement, zoneConfig) {
    this.canvasElement = canvasElement;
    this.context = canvasElement.getContext("2d");

    if (zoneConfig) {
      this.zone = zoneConfig;
      this.oldZoneObject = zoneConfig;
    }
  }

  addEvents() {
    this.abortController = new AbortController();
    const { signal } = this.abortController;
    this.canvasElement.addEventListener(
      "mousedown",
      (e) => this.onMouseDown(e),
      { signal }
    );
    this.canvasElement.addEventListener(
      "mousemove",
      (e) => this.onMouseMove(e),
      { signal }
    );
    this.canvasElement.addEventListener("mouseup", (e) => this.onMouseUp(e), {
      signal,
    });
  }

  removeEvents() {
    if (!this.abortController) return;

    this.abortController.abort();
    this.abortController = undefined;
  }

  onMouseDown(evt) {
    this.mouseDown = true;
    var rect = this.canvasElement.getBoundingClientRect();

    this.oldZoneObject = { ...this.zone };

    this.mouseStart = this.convertHtmlPosToCanvasPos(
      evt.clientX - rect.left,
      evt.clientY - rect.top
    );
    this.mouseEnd = undefined;
  }

  onMouseMove(evt) {
    if (!this.mouseDown) return;
    var rect = this.canvasElement.getBoundingClientRect();

    this.mouseEnd = this.convertHtmlPosToCanvasPos(
      evt.clientX - rect.left,
      evt.clientY - rect.top
    );
  }

  set zone(config) {
    this.mouseStart = config.topLeft;
    this.mouseEnd = config.bottomRight;
  }

  // Pretty inefficient, but ok for a prototype
  get zone() {
    if (!this.mouseStart || !this.mouseEnd) return {};

    const { x: startX, y: startY } = this.mouseStart;
    const { x: endX, y: endY } = this.mouseEnd;

    const zone = {};
    zone.topLeft = {
      x: Math.min(startX, endX),
      y: Math.min(startY, endY),
    };
    zone.bottomRight = {
      x: Math.max(startX, endX),
      y: Math.max(startY, endY),
    };

    return zone;
  }

  onMouseUp(evt) {
    // Don't update the zone if the bounding box for the zone is the same
    // or if topLeft or bottomRight are undefined
    if (this.zone.topLeft && this.zone.bottomRight) {
      const { x: tlX, y: tlY } = this.zone.topLeft;
      const { x: brX, y: brY } = this.zone.bottomRight;

      if (Math.abs(tlX - brX) > 0 && Math.abs(tlY - brY) > 0) {
        if (this.onZoneUpdateCallback) {
          this.onZoneUpdateCallback(this.zone);
        }
      }
    } else {
      this.zone = this.oldZoneObject;
    }

    this.mouseDown = false;
  }

  convertHtmlPosToCanvasPos(x, y) {
    const cw = this.canvasElement.width;
    const w = this.canvasElement.clientWidth;

    const htmlToCanvasRatio = cw / w;

    return {
      x: Math.round(x * htmlToCanvasRatio),
      y: Math.round(y * htmlToCanvasRatio),
    };
  }

  onZoneUpdate(callback) {
    this.onZoneUpdateCallback = callback;
  }

  render(color) {
    if (this.zone.topLeft && this.zone.bottomRight) {
      const rectWidth = this.zone.bottomRight.x - this.zone.topLeft.x;
      const rectHeight = this.zone.bottomRight.y - this.zone.topLeft.y;

      this.context.strokeStyle = color;
      this.context.lineWidth = 10;
      this.context.strokeRect(
        this.zone.topLeft.x,
        this.zone.topLeft.y,
        rectWidth,
        rectHeight
      );
    }
  }
}
