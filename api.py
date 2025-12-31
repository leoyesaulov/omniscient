from http import HTTPStatus
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import find_dotenv, load_dotenv, get_key

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
BOT_TOKEN = get_key(dotenv_path, "BOT_API")
RECIPIENT_CHAT_ID = get_key(dotenv_path, "CHAT_ID")
API_SECRET = get_key(dotenv_path, "API_SECRET")

app = FastAPI()

class Message(BaseModel):
    text: str

# deprecated use
def send_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": RECIPIENT_CHAT_ID, "text": text}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print("failed to send a message")

# deprecated
@app.post("/sendtobot")
def send_to_bot(message: Message):
    print("sending to bot")
    send_message(message.text)
    return {"status": "ok"}

@app.get("/")
@app.get("/health")
def health():
    return {"message": "Ok"}

@app.get("/add_payment/{secret}/{payment}")
def add_payment(secret: str, payment: str):

    return HTTPStatus(200)

@app.get("/query/{secret}/{query}")
def query(secret: str, query: str):

    return HTTPStatus(200)