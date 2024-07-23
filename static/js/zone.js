import { saveConfigForKey } from "./storage.service.js";
import { ZoneDrawer } from "./zone-drawer.js";

export class Zone {
  constructor(canvas, zoneConfig = {}) {
    this.id = zoneConfig.id;
    this.zoneDrawer = new ZoneDrawer(canvas, zoneConfig.zoneArea);
    this.minAreaDrawer = new ZoneDrawer(canvas, zoneConfig.minDetectionArea);
    this.canvas = canvas;
    this.canvasContext = canvas.getContext("2d");
    this.addCallbacks();
  }

  addCallbacks() {
    this.zoneDrawer.onZoneUpdate(() => this.update());
    this.minAreaDrawer.onZoneUpdate(() => this.update());
  }

  onUpdate(callback) {
    this.updateCallback = callback;
  }

  drawZone() {
    this.removeEvents();
    this.zoneDrawer.addEvents();
  }

  drawMinDetectionArea() {
    this.removeEvents();
    this.minAreaDrawer.addEvents();
  }

  removeEvents() {
    this.zoneDrawer.removeEvents();
    this.minAreaDrawer.removeEvents();
  }

  update() {
    if (!this.zoneDrawer.zone || !this.minAreaDrawer.zone) return;

    const data = {
      zoneArea: this.zoneDrawer.zone,
      minDetectionArea: this.calculateArea(this.minAreaDrawer.zone),
    };

    const stringifiedData = JSON.stringify(data);

    const update = async () => {
      await fetch("zone", {
        method: "POST",
        body: stringifiedData,
        headers: { "Content-Type": "application/json" },
      });
    };

    saveConfigForKey("zone", {
      zoneArea: this.zoneDrawer.zone,
      minDetectionArea: this.minAreaDrawer.zone,
    });

    if (this.updateCallback) this.updateCallback();

    update();
    this.removeEvents();
  }

  calculateArea(zone) {
    if (!zone || (!zone.topLeft && !zone.bottomRight)) {
      return undefined;
    }

    const width = Math.abs(zone.topLeft.x - zone.bottomRight.x);
    const height = Math.abs(zone.topLeft.y - zone.bottomRight.y);

    return width * height;
  }

  render() {
    this.zoneDrawer.render("#FF0000");
    this.minAreaDrawer.render("#00FF00");
  }
}
