from http import HTTPStatus
import requests
import uvicorn
import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import find_dotenv, load_dotenv, get_key
from check import Check
import db_handler
import common
from common import EUR_CODE

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
state = common.state
BOT_TOKEN = "" #get_key(dotenv_path, "BOT_API")
RECIPIENT_CHAT_ID = "" #get_key(dotenv_path, "CHAT_ID")
API_SECRET = get_key(dotenv_path, "API_SECRET")

app = FastAPI()

class Message(BaseModel):
    text: str

# deprecated
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


# Add payment
# We get data in form of "store-amount"
@app.get("/add_payment/{secret}/{payment}")
def add_payment(secret: str, payment: str):
    if secret != API_SECRET:
        return HTTPStatus(403)

    payment_arr = payment.split(sep="-")
    store  = payment_arr[0]
    amount = payment_arr[1]

    now = datetime.datetime.now()
    check = Check(state.get_new_id(), int(amount), now, store, EUR_CODE)
    db_handler.put_check(check)

    print(f"Received new payment: {amount} EUR in {store} at {now}")
    return HTTPStatus(200)

# Query the date range from database
# ToDo: get string with dates, process into datetime objects, call query_date(from, to) from db_handler, return total amount
@app.get("/query/{secret}/{query}")
def query(secret: str, query: str):
    if secret != API_SECRET:
        return HTTPStatus(403)


    return HTTPStatus(200)

@app.get("/")
@app.get("/health")
def health():
    return {"message": "Ok"}



async def runApi():
    config = uvicorn.Config(app, port=5003)
    server = uvicorn.Server(config)
    await server.serve()