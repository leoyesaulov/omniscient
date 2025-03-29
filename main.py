import time
import asyncio
import requests
import db_handler
from check import Check
from asyncio import sleep
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv, get_key
from currency_codes import get_currency_by_numeric_code

__env = find_dotenv(".env")
load_dotenv(dotenv_path=__env)
__token = get_key(__env, 'X_TOKEN')
__acc = get_key(__env, 'ACCOUNT')

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
        print(f"You have spent {result.amount} {get_currency_by_numeric_code(str(result.currency)).name} at {result.description} at {result.date}.")
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

async def __listen_to_input():
    loop = asyncio.get_event_loop()
    while True:
        user_input = await loop.run_in_executor(None, input, ">>> ")

        input_arr = user_input.lower().split()

        if input_arr[0] == "refresh":
            __check()
            continue

        if input_arr[0] == "ping":
            print("pong")
            continue

        if  input_arr[0] == "month":
            db_handler.spent_this_month()
            continue

        if input_arr[0] == "add_this_month":
            __add_month()
            continue

        if input_arr[0] == "bot_test":
            db_handler.send_to_bot("test")
            continue

        # if no if block hit
        print(
            f"I'm sorry, I didn't understand that.\nExpected one of: 'refresh'. Got '{input_arr[0]}'.")

async def __run():
    __add_month()
    print("Database seems up to date.")
    await sleep(60)
    while True:
        __check()
        print(f"Automated update has been performed at {datetime.now()}.")
        await sleep(600)


async def __main():
    await asyncio.gather(__run(), __listen_to_input())


if __name__ == '__main__':
    __env = find_dotenv(".env")
    load_dotenv(dotenv_path=__env)

    __token = get_key(__env, 'X_TOKEN')
    __acc = get_key(__env, 'ACCOUNT')

    asyncio.run(__main())
