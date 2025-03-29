import pymongo
import requests
from check import Check
from datetime import datetime
from urllib.parse import quote_plus
from dotenv import load_dotenv, find_dotenv, get_key

__dotenv_path = find_dotenv()
load_dotenv(__dotenv_path)
__uri = "mongodb://%s:%s@%s" % (quote_plus(get_key(__dotenv_path, "MONGO_USR")), quote_plus(get_key(__dotenv_path, "MONGO_PWD")), quote_plus("127.0.0.1:27017"))
__dbclient = pymongo.MongoClient(__uri)
__db = __dbclient["Leo"]
__checks = __db["checks"]

def put_test() -> None:
    __checks.insert_one({"test": 1})

def put_check(check: Check) -> None:
    __checks.insert_one(check.__dict__)

def is_check_in_db(check: Check) -> bool:
    return __checks.find_one({"id": check.id}) is not None

def get_month():
    today = datetime.today()
    month_begin = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    print(f"Getting checks from {month_begin}")
    query = {"date": {"$gte": month_begin}}
    return __checks.find(query)

def spent_this_month() -> None:
    cursor = get_month()
    out: int = 0
    counter: int = 0
    for check in cursor:
        out += int(check["amount"]*100)
        counter += 1

    check_avg: float = round(out / counter / 100, 2)
    day_avg: float = round(out / datetime.today().day / 100, 2)
    out: float = out / 100
    msg = f'''You have spent {out} Euro this month on groceries and stuff.
Your checks averaged {check_avg} Euro this month.
Your expenses averaged {day_avg} Euro per day this month.'''
    print(msg)                                                                  #ToDo: fix input
    send_to_bot(msg)

def send_to_bot(msg: str):
    response = requests.post(url="http://127.0.0.1:6969/sendtobot", json={"text": msg}).json()
    print(f"Sent the message {msg} to bot,\n Received response: {response}")