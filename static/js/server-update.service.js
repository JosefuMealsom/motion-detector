export function updateZone(zone) {
  const zoneObject = { zoneArea: zone };

  const update = async () => {
    await fetch("/zone", {
      method: "POST",
      body: JSON.stringify(zoneObject),
      headers: { "Content-Type": "application/json" },
    });
  };

  update();
}

export function updateMinArea(minArea) {
  const zoneObject = { minArea: minArea };

  const update = async () => {
    await fetch("/zone/min-area", {
      method: "POST",
      body: JSON.stringify(zoneObject),
      headers: { "Content-Type": "application/json" },
    });
  };

  update();
}
