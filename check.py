import datetime

class Check:
    def __init__(self, id: str, amount: int, date: datetime, description: str, currencyCode: int):
        self.id = id
        self.amount = amount
        self.date = date
        self.description = description      # the store
        self.currency = currencyCode