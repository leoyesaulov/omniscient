import asyncio
import argparse
import db_handler
import common
from datetime import datetime
from dotenv import get_key
from api import runApi

async def listen_to_input():
    loop = asyncio.get_event_loop()
    while True:
        user_input = await loop.run_in_executor(None, input, ">>> ")

        parsed = parser.parse_args(user_input.split())
        cmd = parsed.cmd[0]


        if cmd == "ping":
            print("pong")
            continue

        if cmd == "del":
            print(f"Deleting check with id {parsed.id} from the database")
            db_handler.delete_check(parsed.id)
            continue

        # if no if block hit
        print(f"I'm sorry, I didn't understand that.\nExpected one of: 'refresh'. Got '{cmd}'.")


async def main():
    await asyncio.gather(listen_to_input(), runApi())


if __name__ == '__main__':
    dotenv_path = common.dotenv_path

    token = get_key(dotenv_path, 'X_TOKEN')
    acc = get_key(dotenv_path, 'ACCOUNT')

    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", type=str, nargs=1, help="The command to execute")
    parser.add_argument("-d", "--date", type=str, required=False, default=datetime.today().strftime("%d.%m.%Y"), help="Date on the check")
    parser.add_argument("-a", "--amount", type=float, required=False, help="Amount paid")
    parser.add_argument("-n", "--description", "--name", type=str, required=False, help="Description of the check")
    parser.add_argument("-c", "--currencyCode", type=int, required=False, default=978, help="Currency code of the check")
    parser.add_argument("-id", "--id", type=str, required=False, help="ID of the check")

    asyncio.run(main())
