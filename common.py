import socket

# Common makros
EUR_CODE = 978
UAH_CODE = 980

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
MONGO_URI = f"{IPAddr}:27017"

# Common state vars
class State:
    def __init__(self):
        try:
            with open(".state", "r") as file:
                self.next_id = int(file.readline().strip())
        except IOError:
            with open(".state", "w") as file:
                self.next_id = 0
                file.write(f"{self.next_id}\n")

                file.flush()
                file.close()

    def update_statefile(self):
        with open(".state", "w") as file:
            file.write(f"{self.next_id}\n")

            file.flush()
            file.close()

    # returns current id counter value and increments it
    def get_new_id(self) -> int:
        current_id = self.next_id
        self.next_id += 1
        self.update_statefile()
        return current_id

state = State()