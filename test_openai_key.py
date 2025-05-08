import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    models = client.models.list()
    print("✅ OpenAI key works! Available models:")
    for m in models.data[:3]:
        print("-", m.id)
except Exception as e:
    print("❌ OpenAI key failed.")
    print("Error:", e)
