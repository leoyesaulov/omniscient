import time
import string
import random
import asyncio
import requests
import argparse
import db_handler
from check import Check
from asyncio import sleep
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv, get_key
from currency_codes import get_currency_by_numeric_code


def generate_id(length=17):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


def __to_unix(value: datetime):
    return time.mktime(value.timetuple())

def __get_url(from_date: datetime):
    return "https://api.monobank.ua/personal/statement/" + __acc + "/" + str(int(__to_unix(from_date)))

def __get_24h_statement():
    time = datetime.now() - timedelta(hours=24)
    statement = requests.get(__get_url(time), headers={'X-Token': __token}).json()
    return statement

def __process_check(check: dict):
    result = Check(check['id'], check['operationAmount']/(-100), datetime.fromtimestamp(check['time']), check['description'], check['currencyCode'])
    if not db_handler.is_check_in_db(result) and all([check['operationAmount'] <= 0, check['currencyCode'] != 980]):
        __print(f"You have spent {result.amount} {get_currency_by_numeric_code(str(result.currency)).name} at {result.description} at {result.date}.")
        db_handler.send_to_bot(f"You have spent {result.amount} {get_currency_by_numeric_code(str(result.currency)).name} at {result.description} at {result.date}.")
        db_handler.put_check(result)

def __process_statement(statement: list):
    for check in statement:
        __process_check(check)

def __check():
    __statement = __get_24h_statement()
    __process_statement(__statement)

def __get_month_statement():
    time = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    statement = requests.get(__get_url(time), headers={'X-Token': __token}).json()
    return statement

def __add_month():
    __statement = __get_month_statement()
    __process_statement(__statement)

def __add_excel(path: str):
    print("Adding excel not implemented yet")

async def __listen_to_input():
    loop = asyncio.get_event_loop()
    while True:
        user_input = await loop.run_in_executor(None, input, ">>> ")

        parsed = parser.parse_args(user_input.split())
        cmd = parsed.cmd[0]

        if cmd == "refresh":
            __check()
            continue

        if cmd == "ping":
            print("pong")
            continue

        if  cmd == "month":
            __add_month()
            db_handler.monthly_report()
            continue

        if cmd == "bot_test":
            db_handler.send_to_bot("test")
            continue

        if cmd == "add_excel":
            print("Add excel command received. Functionality no implemented yet")
            continue

        if cmd == "del":
            print(f"Deleting check with id %s from the database", parsed.id)
            db_handler.delete_check(parsed.id)
            continue

        if cmd == "add":
            check = Check(generate_id(), parsed.amount, datetime.strptime(parsed.date, "%d.%m.%Y"), parsed.description, parsed.currencyCode)
            db_handler.put_check(check)
            print("Seems like success")
            continue

        # if no if block hit
        print(f"I'm sorry, I didn't understand that.\nExpected one of: 'refresh'. Got '{cmd}'.")

def __print(msg: str) -> None:
    print(f"\r{msg}", flush=True)
    print(">>> ", end="", flush=True)

async def __run():
    __add_month()
    print("Database seems up to date.")
    await sleep(60)

    while True:
        __check()

        now = datetime.now()
        __print(f"Automated update has been performed at {now}.")
        if now.hour == 21:
            db_handler.daily_report()
            if now.month < (now + timedelta(days=1)).month:
                db_handler.monthly_report()

        await sleep(3600)


async def __main():
    await asyncio.gather(__run(), __listen_to_input())


if __name__ == '__main__':
    __env = find_dotenv(".env")
    load_dotenv(dotenv_path=__env)

    __token = get_key(__env, 'X_TOKEN')
    __acc = get_key(__env, 'ACCOUNT')

    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", type=str, nargs=1, help="The command to execute")
    parser.add_argument("-d", "--date", type=str, required=False, default=datetime.today().strftime("%d.%m.%Y"), help="Date on the check")
    parser.add_argument("-a", "--amount", type=float, required=False, help="Amount paid")
    parser.add_argument("-n", "--description", "--name", type=str, required=False, help="Description of the check")
    parser.add_argument("-c", "--currencyCode", type=int, required=False, default=978, help="Currency code of the check")
    parser.add_argument("-id", "--id", type=str, required=False, help="ID of the check")

    asyncio.run(__main())
