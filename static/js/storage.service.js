export function loadConfigForKey(key) {
  const zoneString = localStorage.getItem(key);

  if (zoneString) {
    return JSON.parse(zoneString);
  }

  return undefined;
}

export function saveConfigForKey(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}
