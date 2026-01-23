from asyncio import futures as afutures
from concurrent import futures
from http import HTTPStatus
import omniscient_pb2_grpc
import omniscient_pb2
import grpc
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

class AddPaymentServicer(omniscient_pb2_grpc.AddPaymentServicer):
    def AddPayment(self, request, context):
        status = add_payment(request.store, request.amount)
        resp = omniscient_pb2.PaymentResponse(success=status)
        return resp

class QueryServicer(omniscient_pb2_grpc.QueryServicer):
    def Query(self, request, context):
        # do we fr need to return status?? ToDo decide if return status at all
        amount = query(request.start_date, request.stop_date)
        resp = omniscient_pb2.QueryResponse(success=True, amount=amount)
        return resp

class Message(BaseModel):
    text: str

# deprecated
def send_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": RECIPIENT_CHAT_ID, "text": text}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print("failed to send a message")

# deprecated                      status = api.add_payment(request.store, request.amount)
# @app.post("/sendtobot")
def send_to_bot(message: Message):
    print("sending to bot")
    send_message(message.text)
    return {"status": "ok"}


# ToDo: handle currency, upd comments
# Add payment
# We get data in form of "store/amount"
# No need for extra decoding bc its handled by fastapi
# @app.get("/add_payment/{secret}/{store}/{amount}")
def add_payment(store: str, amount: int) -> bool:
    now = datetime.datetime.now()
    print(f"Received new payment: {amount/100} EUR in {store} at {now}")

    check = Check(state.get_new_id(), amount, now, store, EUR_CODE)
    db_handler.put_check(check)

    return True



# Query the date range from database
# get string with dates, process into datetime objects, call query_date(from, to) from db_handler, return total amount
# ToDo: add time to query (is it really needed?)
# @app.get("/query/{secret}/{date_from}/{date_to}")
def query(date_from: str, date_to: str) -> int:
    print(f"received query call with date_from: {date_from}, date_to: {date_to}")

    # date format: 01.01.2026 through 31.12.2026
    fromd = datetime.datetime.strptime(date_from, "%d.%m.%Y")
    tod = datetime.datetime.strptime(date_to, "%d.%m.%Y")

    # int
    total = db_handler.query_date(fromd, tod)

    return total
    # return {"total": total/100}

# ToDo: add calculation of available spending, add endpoint to configure (do I calculate backend or frontend?)
# ToDo: upd requirements

# @app.get("/")
# @app.get("/health")
def health():
    return {"message": "Ok"}


# ToDo: refactor to concurrency instead of asyncio
async def runApi():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
    omniscient_pb2_grpc.add_AddPaymentServicer_to_server(AddPaymentServicer, server)
    omniscient_pb2_grpc.add_QueryServicer_to_server(QueryServicer, server)
    server.add_insecure_port("127.0.0.1:5003")
    # doesnt block
    server.start()
    # this thread doesnt really have anything left to do so we block it
    await server.wait_for_termination()

    # config = uvicorn.Config(app, port=5003)
    # server = uvicorn.Server(config)
    # await server.serve()