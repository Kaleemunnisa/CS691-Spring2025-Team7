
const express = require("express");
const http = require("http");
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Serve frontend files from the "public" directory
app.use(express.static("public"));

io.on("connection", (socket) => {
  console.log("🔌 New client connected:", socket.id);

  // Handle incoming chat messages
  socket.on("chat", (msg) => {
    socket.broadcast.emit("chat", { id: socket.id, msg });
  });

  // WebRTC signaling events
  socket.on("offer", (data) => {
    socket.to(data.to || getOtherSocket(socket.id)).emit("offer", {
      from: socket.id,
      offer: data.offer
    });
  });

  socket.on("answer", (data) => {
    socket.to(data.to).emit("answer", {
      from: socket.id,
      answer: data.answer
    });
  });

  socket.on("ice-candidate", (data) => {
    socket.to(data.to).emit("ice-candidate", {
      from: socket.id,
      candidate: data.candidate
    });
  });

  socket.on("disconnect", () => {
    console.log("❌ Client disconnected:", socket.id);
  });
});

// Utility to find another client (basic 1-to-1 pairing)
function getOtherSocket(currentSocketId) {
  const clients = Array.from(io.sockets.sockets.keys());
  const other = clients.find(id => id !== currentSocketId);
  return other || null;
}

server.listen(3000, () => {
  console.log("🚀 Socket.IO server running at http://localhost:3000");
});
