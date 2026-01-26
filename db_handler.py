import common
import pymongo
from check import Check
from dotenv import get_key
from urllib.parse import quote_plus
from datetime import datetime, timedelta

dotenv_path = common.dotenv_path
uri = "mongodb://%s:%s@%s" % (quote_plus(get_key(dotenv_path, "MONGO_USR")), quote_plus(get_key(dotenv_path, "MONGO_PWD")), quote_plus(common.MONGO_URI))
dbclient = pymongo.MongoClient(uri)
db = dbclient["Leo"]
checks = db["checks"]

def put_test() -> None:
    checks.insert_one({"test": 1})

def put_check(check: Check) -> None:
    checks.insert_one(check.__dict__)

def delete_check(id: str):
    checks.delete_one({"id": id})

def is_check_in_db(check: Check) -> bool:
    return bool(checks.find_one({"id": check.id}))

def get_month():
    today = datetime.today()
    month_begin = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    print(f"Getting checks from {month_begin}")
    query = {"date": {"$gte": month_begin}}
    return checks.find(query)

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

def get_day():
    today = datetime.today()
    day_begin = today - timedelta(days=1)
    print(f"Getting checks from {day_begin}")
    query = {"date": {"$gte": day_begin}}
    return checks.find(query)


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

# queries the database for all payments between two timestamps, returns total amount
def query_date(start: datetime, end: datetime) -> int:
    sum: int = 0
    query = {
        "$and": [
            {"date": {"$gte": start}},
            {"date": {"$lte": end}}
        ]
    }
    cursor = checks.find(query)
    for check in cursor:
        sum += int(check["amount"] * 100)

    return sum