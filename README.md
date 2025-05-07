# 🌟 LUMINA – AI-Assisted Mental Health Support Platform

LUMINA is a real-time, AI-assisted mental health support platform that provides safe, anonymous, and stigma-free emotional support. Powered by GPT-4, it enables users to chat or talk with trained volunteers, while AI models flag high-risk content for immediate action.

---

## 🧠 Key Features

- 💬 Real-time GPT-4 powered chatbot
- 🎤 WebRTC voice support
- 🔐 Google and GitHub OAuth login
- 📈 Chart.js-based progress dashboard
- 💾 SQLite support (PostgreSQL optional)
- 🧠 Message classification with GPT-4

---

## ⚙️ Tech Stack

| Component    | Technology          |
|--------------|---------------------|
| Backend      | Flask (Python)      |
| AI Engine    | GPT-4 (LiteLLM)     |
| Realtime     | WebRTC, Socket.IO   |
| Auth         | Google, GitHub OAuth|
| Frontend     | HTML/CSS/JS, Chart.js |
| Database     | SQLite / PostgreSQL |
| Deployment   | Gunicorn + Nginx    |

---

## 🛠 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/lumina.git
cd lumina
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add Environment Variables
Create a `.env` file:
```env
HF_TOKEN=your-huggingface-api-token
LITELLM_API_KEY=your-litellm-api-key
OPENAI_API_KEY=your-openai-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
SECRET_KEY=your-flask-secret-key
```

### 4. Initialize Database
```bash
python scripts/init_db.py
```

### 5. Run the App
```bash
flask run
```

---

## 🔄 Realtime Server (Optional)
```bash
cd realtime-server
npm install
node server.js
```

---

## 📃 License
MIT License

---

## 👨‍💻 Contributors
- Pavan Ganeshreddy Yeruva
- Snehanjani Pati
- Sravya Vemireddy
- Sireesha Gangarapu
- Pravallika Challa
