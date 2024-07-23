const socket = io();

export function onEnterZone(callback) {
  socket.on("entered", callback);
}

export function onLeftZone(callback) {
  socket.on("left", callback);
}
