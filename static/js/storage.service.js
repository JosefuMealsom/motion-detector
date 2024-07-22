export function loadZoneConfig(zone) {
  const zoneString = localStorage.getItem("zoneConfig");

  if (zoneString) {
    return JSON.parse(zoneString);
  }

  return {
    topLeft: undefined,
    bottomRight: undefined,
  };
}

export function saveZoneConfig(zone) {
  localStorage.setItem("zoneConfig", JSON.stringify(zone));
}

export function loadMinAreaConfig() {
  const zoneString = localStorage.getItem("minAreaConfig");
  if (zoneString) {
    return JSON.parse(zoneString);
  }

  return {
    topLeft: undefined,
    bottomRight: undefined,
  };
}

export function saveMinAreaConfig(minAreaZone) {
  localStorage.setItem("minAreaConfig", JSON.stringify(minAreaZone));
}
