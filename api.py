from http import HTTPStatus
import requests
import uvicorn
import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import get_key
from check import Check
import db_handler
import common
from common import EUR_CODE

dotenv_path = common.dotenv_path
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
# We get data in form of "store/amount"
# No need for extra decoding bc its handled by fastapi
@app.get("/add_payment/{secret}/{store}/{amount}")
def add_payment(secret: str, store: str, amount: str):
    if secret != API_SECRET:
        return HTTPStatus(403)

    # payment_arr = payment.split(sep="-")
    # store  = payment_arr[0]
    # amount = payment_arr[1]
    amount_numerical = int(float(amount.replace(',', '.')) * 100)

    now = datetime.datetime.now()
    print(f"Received new payment: {amount_numerical/100} EUR in {store} at {now}")

    check = Check(state.get_new_id(), amount_numerical, now, store, EUR_CODE)
    db_handler.put_check(check)

    return HTTPStatus(200)

# Query the date range from database
# get string with dates, process into datetime objects, call query_date(from, to) from db_handler, return total amount
# ToDo: add time to query
@app.get("/query/{secret}/{date_from}/{date_to}")
def query(secret: str, date_from: str, date_to: str):
    if secret != API_SECRET:
        return HTTPStatus(403)

    print(f"received query call with date_from: {date_from}, date_to: {date_to}")

    # date format: 01.01.2026 through 31.12.2026
    fromd = datetime.datetime.strptime(date_from, "%d.%m.%Y")
    tod = datetime.datetime.strptime(date_to, "%d.%m.%Y")

    total = db_handler.query_date(fromd, tod)

    return {"total": total}

@app.get("/")
@app.get("/health")
def health():
    return {"message": "Ok"}



async def runApi():
    config = uvicorn.Config(app, port=5003)
    server = uvicorn.Server(config)
    await server.serve()