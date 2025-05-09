import pymongo
import requests
from check import Check
from urllib.parse import quote_plus
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv, get_key

__dotenv_path = find_dotenv()
load_dotenv(__dotenv_path)
__uri = "mongodb://%s:%s@%s" % (quote_plus(get_key(__dotenv_path, "MONGO_USR")), quote_plus(get_key(__dotenv_path, "MONGO_PWD")), quote_plus("192.168.2.31:27017"))
__dbclient = pymongo.MongoClient(__uri)
__db = __dbclient["Leo"]
__checks = __db["checks"]

def put_test() -> None:
    __checks.insert_one({"test": 1})

def put_check(check: Check) -> None:
    __checks.insert_one(check.__dict__)

def delete_check(id: str):
    __checks.delete_one({"id": id})

def is_check_in_db(check: Check) -> bool:
    return bool(__checks.find_one({"id": check.id}))

def get_month():
    today = datetime.today()
    month_begin = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    print(f"Getting checks from {month_begin}")
    query = {"date": {"$gte": month_begin}}
    return __checks.find(query)

def monthly_report() -> None:
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
    print(msg)
    send_to_bot(msg)

def get_day():
    today = datetime.today()
    day_begin = today - timedelta(days=1)
    print(f"Getting checks from {day_begin}")
    query = {"date": {"$gte": day_begin}}
    return __checks.find(query)


def daily_report() -> None:
    cursor = get_day()
    out: int = 0
    counter: int = 0
    for check in cursor:
        out += int(check["amount"] * 100)
        counter += 1

    if counter > 0:
        check_avg: float = round(out / counter / 100, 2)
        out: float = out / 100
        msg = f'''You have spent {out} Euro in the past 24h on groceries and stuff.
Your checks averaged {check_avg} Euro this day.'''
        print(msg)
        send_to_bot(msg)


def send_to_bot(msg: str):
    response = requests.post(url="http://127.0.0.1:6969/sendtobot", json={"text": msg}).json()
    print(f"\rSent the message to bot.\nReceived response: {response}")