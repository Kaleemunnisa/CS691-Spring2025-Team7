import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from litellm import completion  # type: ignore
import os
from dotenv import load_dotenv
load_dotenv()
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
import re
import sqlite3
import torch
import random
import json
import torch.nn.functional as F
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, g
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification
from huggingface_hub import login
import logging
from werkzeug.security import generate_password_hash, check_password_hash

# === Setup Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Load environment variables ===
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY")

if not HF_TOKEN:
    raise RuntimeError("Please set the HF_TOKEN environment variable.")
if not LITELLM_API_KEY:
    raise RuntimeError("Please set the LITELLM_API_KEY environment variable.")

# === Authenticate with Hugging Face Hub ===
login(token=HF_TOKEN)

# === Load Models ===
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

GPT2_MODEL_ID = "mahesh006/mentalhealthgpt"
tokenizer_gpt2 = AutoTokenizer.from_pretrained(GPT2_MODEL_ID, use_auth_token=True)
model_gpt2 = AutoModelForCausalLM.from_pretrained(GPT2_MODEL_ID, use_auth_token=True).to(DEVICE)
model_gpt2.eval()

BERT_MODEL_ID = "mahesh006/mentalhealthbert"
tokenizer_bert = AutoTokenizer.from_pretrained(BERT_MODEL_ID, use_auth_token=True)
model_bert = AutoModelForSequenceClassification.from_pretrained(BERT_MODEL_ID, use_auth_token=True).to(DEVICE)
model_bert.eval()

valid_labels = ["Mild", "Moderate", "Severe", "No Depression"]

SYMPTOMS = [
    "sleep", "appetite", "interest", "fatigue", "worthlessness", "concentration",
    "agitation", "suicidal ideation", "sleep disturbance", "aggression",
    "panic attacks", "hopelessness", "restlessness", "low energy"
]

app = Flask(__name__)

# === Load environment variables ===
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # ✅ Use secure secret from .env

DATABASE = 'users.db'
conversation_state = {}
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # ✅ already correct
# === Register Google OAuth ===
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_url="/google_login"
)
app.register_blueprint(google_bp, url_prefix="/auth")

# === Register GitHub OAuth ===
github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    redirect_url="/github_login"
)
app.register_blueprint(github_bp, url_prefix="/auth")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db
def save_progress(user, mood, session_completed, sleep, energy, focus, stress):
    db = get_db()
    db.execute('''
        INSERT INTO progress (user, mood, session_completed, sleep, energy, focus, stress)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user, mood, session_completed, sleep, energy, focus, stress))
    db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                mood INTEGER,
                session_completed INTEGER,
                sleep INTEGER,
                energy INTEGER,
                focus INTEGER,
                stress INTEGER
            );
        ''')
        db.commit()



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        try:
            db = get_db()
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (email, password))
            db.commit()
            return redirect(url_for('signin'))
        except sqlite3.IntegrityError:
            return "Username already exists."
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (email,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session['user'] = email
            return redirect(url_for('home'))
        else:
            return "Invalid email or password."
    return render_template('signin.html')

@app.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Failed to fetch user info from Google.", 400
    email = resp.json().get("email")
    session["user"] = email
    return redirect(url_for("home"))

@app.route("/github_login")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    if not resp.ok:
        return "Failed to fetch user info from GitHub.", 400
    username = resp.json().get("login")
    session["user"] = username
    return redirect(url_for("home"))
@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (email,)).fetchone()
        if user:
            # Simulate sending reset email
            return render_template('forgot.html', message="✅ Reset link has been sent to your email.")
        else:
            return render_template('forgot.html', message="❌ Email not found. Please check and try again.")
    return render_template('forgot.html')


@app.route('/signout')
def signout():
    session.pop('user', None)
    return redirect(url_for('signin'))

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('signin'))
    return render_template('index.html')

@app.route('/progress')
def progress():
    if 'user' not in session:
        return redirect(url_for('signin'))
    return render_template('progress.html')

@app.route('/api/progress')
def get_progress():
    if 'user' not in session:
        return jsonify({"error": "Not authorized"}), 403

    db = get_db()
    rows = db.execute('SELECT * FROM progress WHERE user = ? ORDER BY timestamp ASC', (session['user'],)).fetchall()

    data = {
        "mood": [row["mood"] for row in rows],
        "session": [row["session_completed"] for row in rows],
        "labels": [row["timestamp"][:10] for row in rows],
        "survey": {
            "sleep": rows[-1]["sleep"],
            "energy": rows[-1]["energy"],
            "mood": rows[-1]["mood"],
            "focus": rows[-1]["focus"],
            "stress": rows[-1]["stress"],
        } if rows else {}
    }
    return jsonify(data)



@app.route('/Mindfulness')
def mindfulness_page():
    if 'user' not in session:
        return redirect(url_for('signin'))
    return render_template('Mindfulness.html')

@app.route('/grounding')
def grounding():
    return render_template('grounding.html')  

@app.route('/sleep')
def sleep():
    return render_template('sleep.html')  

@app.route('/movement')
def movement():
    return render_template('movement.html')  

@app.route('/supportzone')
def supportzone():
    return render_template('supportzone.html')

@app.route('/memory')
def memory():
    return render_template('memory.html')

@app.route('/doodle')
def doodle():
    return render_template('doodle.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/slider')
def puzzle():
    return render_template('slider.html')

@app.route('/supportive')
def supportive():
    return render_template('supportive.html')




@app.route('/chat', methods=['POST'])
def chat():
    if 'user' not in session:
        return jsonify({"response": "Unauthorized. Please sign in first."}), 401

    data = request.get_json(force=True)
    user_id = session['user']
    user_message = data.get('message', '').strip().lower()

    if user_id not in conversation_state:
        conversation_state[user_id] = {
            "step": 0,
            "responses": {},
            "mode": "survey"
        }

    state = conversation_state[user_id]
    step = state["step"]
    mode = state.get("mode", "survey")


    # Optional Survey Skip
    if user_message in ["skip", "skip survey", "i want to talk", "support"]:
        state["mode"] = "support"
        state["survey_done"] = False
        state["depression_label"] = "Not Assessed"
        state["history"] = ""
        return jsonify({"response": "🧠 Survey skipped. You can now talk to me freely — I'm here to support you 💬"})

    if mode == "survey":
        if step == 0 and not user_message.isdigit():
            return jsonify({
                "response": f"Let's begin! How often do you experience {SYMPTOMS[0]}? (1 to 6)\nType 'skip' if you'd prefer to talk directly."
            })

        if step < len(SYMPTOMS):
            current_symptom = SYMPTOMS[step]
            try:
                rating = int(user_message)
                if not (1 <= rating <= 6):
                    raise ValueError()
                state["responses"][current_symptom] = rating
                state["step"] += 1

                if state["step"] < len(SYMPTOMS):
                    next_symptom = SYMPTOMS[state["step"]]
                    return jsonify({"response": f"How often do you experience {next_symptom}? (1 to 6)"})
                else:
                    symptom_str = "; ".join([f"{k}={v}" for k, v in state["responses"].items()])
                    prompt = f"Input Symptoms: {symptom_str}; Prediction: Depression State ="
                    label, conf, model_used = generate_depression_prediction_ensemble(prompt)
                    state["survey_done"] = True
                    state["mode"] = "support"
                    state["depression_label"] = label
                    # Save survey data as progress
                    save_progress(
                        user=user_id,
                        mood=state["responses"].get("mood", 3),
                        session_completed=1,
                        sleep=state["responses"].get("sleep", 3),
                        energy=state["responses"].get("low energy", 3),
                        focus=state["responses"].get("concentration", 3),
                        stress=state["responses"].get("stress", 3),
                    )

                    state["history"] = ""
                    return jsonify({
                        "response": f"✅ Survey complete! You are likely experiencing **{label}** depression (Confidence: {conf:.2%}, Model: {model_used}).\n\nYou can now talk to me freely — I'm here to support you 💬"
                    })
            except ValueError:
                return jsonify({"response": f"Please enter a number between 1 and 6 for how often you experience {SYMPTOMS[step]}."})

    if mode == "support":
        chat_history = state.get("history", "")
        chat_prompt = (
            "You are a compassionate and emotionally intelligent AI assistant helping someone who is feeling emotionally low.\n"
            "Please respond kindly, supportively, and avoid repeating the user.\n"
            f"{chat_history}User: {user_message}\nAI:"
        )

        try:
            response = completion(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a mental health support assistant."},
                    {"role": "user", "content": chat_prompt}
                ],
                max_tokens=150
            )

            reply = response.choices[0].message["content"].strip()
            if not reply or len(reply) < 5:
                reply = "I'm here for you. Would you like to talk more about how you're feeling?"

            full_history = f"{chat_history}User: {user_message}\nAI: {reply}\n"
            state["history"] = "\n".join(full_history.splitlines()[-10:])

            return jsonify({"response": reply})

        except Exception as e:
            print("GPT-4o-mini error:", e)
            return jsonify({"response": "Sorry, something went wrong. But I'm still here for you. Try again in a moment 💙"})

def generate_depression_prediction_gpt2(prompt: str):
    inputs = tokenizer_gpt2(prompt, return_tensors="pt", truncation=True).to(DEVICE)
    output = model_gpt2.generate(
        **inputs,
        max_new_tokens=20,
        temperature=0.7,
        top_k=10,
        do_sample=True,
        return_dict_in_generate=True,
        output_scores=True,
        pad_token_id=tokenizer_gpt2.eos_token_id,
        eos_token_id=tokenizer_gpt2.eos_token_id
    )
    decoded = tokenizer_gpt2.decode(output.sequences[0], skip_special_tokens=True)
    match = re.search(r"Depression State\s*=?\s*([A-Za-z\s]+)", decoded)
    if match:
        predicted_raw = match.group(1).strip().lower()
        for label in valid_labels:
            if label.lower() in predicted_raw:
                probs = [torch.max(F.softmax(score[0], dim=-1)).item() for score in output.scores]
                confidence = sum(probs) / len(probs) if probs else 0.0
                return label, confidence
    return "Unknown", 0.0

def generate_depression_prediction_bert(prompt: str):
    inputs = tokenizer_bert(prompt, return_tensors="pt", truncation=True, padding=True).to(DEVICE)
    with torch.no_grad():
        logits = model_bert(**inputs).logits
        probs = F.softmax(logits, dim=-1)
        prediction_idx = torch.argmax(probs, dim=-1).item()
        confidence = probs[0, prediction_idx].item()
        return valid_labels[prediction_idx], confidence

def generate_depression_prediction_ensemble(prompt: str):
    label_gpt, conf_gpt = generate_depression_prediction_gpt2(prompt)
    label_bert, conf_bert = generate_depression_prediction_bert(prompt)
    return (label_bert, conf_bert, "BERT") if conf_bert >= conf_gpt else (label_gpt, conf_gpt, "GPT-2")

# === AI Quiz Endpoint ===
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/get-question")
def get_question():
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": (
                "Generate a short, positive, reflective question that promotes mental wellness, "
                "along with 4 uplifting answer choices. Respond ONLY in this JSON format:\n"
                '{ "question": "Your question here", "answers": ["A", "B", "C", "D"] }'
            )}],
            temperature=0.8
        )

        content = response.choices[0].message.content.strip()
        print("GPT Response:", content)

        import re, json
        match = re.search(r'\{[\s\S]+\}', content)
        if match:
            data = json.loads(match.group(0))
            return jsonify(data)

        raise ValueError("Response not JSON-formatted")

    except Exception as e:
        print("❌ OpenAI error or JSON parsing failed:", str(e))
        return jsonify({
            "question": "What brings you calm today?",
            "answers": ["A deep breath", "A quiet moment", "A kind thought", "A nature walk"]
        })




if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
