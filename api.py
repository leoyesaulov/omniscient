import requests
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import find_dotenv, load_dotenv, get_key

__dotenv_path = find_dotenv()
load_dotenv(__dotenv_path)
BOT_TOKEN = get_key(__dotenv_path, "BOT_API")
RECIPIENT_CHAT_ID = get_key(__dotenv_path, "CHAT_ID")

app = FastAPI()

def send_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": RECIPIENT_CHAT_ID, "text": text}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print("failed to send a message")

class Message(BaseModel):
    text: str
@app.post("/sendtobot")
def send_to_bot(message: Message):
    print("sending to bot")
    send_message(message.text)
    return {"status": "ok"}

@app.get("/")
@app.get("/health")
def health():
    return {"message": "Ok"}