const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const cors = require("cors");
const admin = require("firebase-admin");
const session = require("express-session");
const cookieParser = require("cookie-parser");
require("dotenv").config();
const LiteLLM = require("litellm");
const serviceAccount = require("./firebase-config.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});
LiteLLM.api_key = process.env.LITELLM_API_KEY;

const auth = admin.auth();
const app = express();
const server = http.createServer(app);
const allowedOrigins = ["http://localhost:3000", "http://localhost:3001"];
const io = new Server(server, {
  cors: {
    origin: allowedOrigins,
    credentials: true,
  },
});

app.use(
  cors({
    origin: allowedOrigins,
    credentials: true,
  })
);
app.use(express.json());
app.use(cookieParser());
app.use(
  session({
    secret: "your_secret_key",
    resave: false,
    saveUninitialized: false,
    cookie: { httpOnly: true, secure: false, maxAge: 24 * 60 * 60 * 1000 },
  })
);

app.post("/register", async (req, res) => {
  const { email, password } = req.body;
  try {
    const userRecord = await auth.createUser({ email, password });
    res.json({ message: "Registration successful", user: userRecord });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.post("/login", async (req, res) => {
  const { email, password } = req.body;
  try {
    const userRecord = await auth.getUserByEmail(email);
    const token = await admin.auth().createCustomToken(userRecord.uid);
    req.session.user = { uid: userRecord.uid, email };
    res.json({ message: "Login successful", token });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.get("/protected", (req, res) => {
  if (!req.session.user) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  res.json({ user: req.session.user });
});

app.post("/logout", (req, res) => {
  req.session.destroy(() => {
    res.json({ message: "Logged out successfully" });
  });
});

const prompt={role:"system", content:"you are expert mental health consultant. please only respond about mental health issues. if user asks something else return `Iam only here to guide about your mental health`. Respond to greeting messages from the user. Provide some youtube clickable video links to make them feel better based on the user mental condition."}

io.on("connection", (socket) => {
  console.log("User connected:", socket.id);

  socket.on("message", async (message) => {
    try {

      socket.broadcast.emit("message", { text: message, sent: false });
      const response = await LiteLLM.completion({
        model: "gpt-4o-mini",
        messages: [prompt,{ role: "user", content: message }],
        max_tokens: 100,
      });

      if (response.choices && response.choices.length > 0) {
        const aiMessage = response.choices[0].message?.content || "AI response error";

        setTimeout(() => {
          io.emit("message", { text: aiMessage, sent: false });
        }, 1000);
      } else {
        console.error("Unexpected LiteLLM response:", response);
      }
    } catch (error) {
      console.error("LiteLLM API error:", error);
    }
  });

  socket.on("disconnect", () => {
    console.log("User disconnected:", socket.id);
  });
});


const PORT = process.env.PORT || 4000;
server.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
