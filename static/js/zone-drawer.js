export class ZoneDrawer {
  zone = {
    topLeft: undefined,
    topRight: undefined,
  };
  oldZoneObject = undefined;
  mouseDown = false;
  onZoneUpdateCallback = undefined;

  constructor(canvasElement, zoneConfig) {
    this.canvasElement = canvasElement;

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

    this.zone.topLeft = this.convertHtmlPosToCanvasPos(
      evt.clientX - rect.left,
      evt.clientY - rect.top
    );
    this.zone.bottomRight = undefined;
  }

  onMouseMove(evt) {
    if (!this.mouseDown) return;
    var rect = this.canvasElement.getBoundingClientRect();

    this.zone.bottomRight = this.convertHtmlPosToCanvasPos(
      evt.clientX - rect.left,
      evt.clientY - rect.top
    );
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
}
