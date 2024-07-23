const socket = io();
socket.on("connect", function () {
  socket.on("detected", () => {
    console.log("Detected");
  });
});
