import grpc
import datetime
import db_handler
from protobufs import omniscient_pb2
from protobufs import omniscient_pb2_grpc

from check import Check
from concurrent import futures
from common import EUR_CODE, state

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
        print(f"Query processing successful. QueryResponse:\n{resp}")
        return resp

# ToDo: handle currency
# Add payment
def add_payment(store: str, amount: int) -> bool:
    now = datetime.datetime.now()
    print(f"Received new payment: {amount/100} EUR in {store} at {now}")

    check = Check(state.get_new_id(), amount, now, store, EUR_CODE)
    db_handler.put_check(check)

    return True



# Query the date range from database
# get string with dates, process into datetime objects, call query_date(from, to) from db_handler, return total amount
def query(date_from: str, date_to: str) -> int:
    print(f"received query call with date_from: {date_from}, date_to: {date_to}")

    # date format: 01.01.2026 through 31.12.2026
    fromd = datetime.datetime.strptime(date_from, "%d.%m.%Y")
    tod = datetime.datetime.strptime(date_to, "%d.%m.%Y")

    # int
    total = db_handler.query_date(fromd, tod)

    return total

# calculate info on spending trajectory, prepare to send back
def spending_trajectory():
    pass

# configure monthly allowance available
# use state.allowance for persistence
def configure_monthly_allowance(new_allowance: int):
    pass

# ToDo: add calculation of available spending, add endpoint to configure (do I calculate backend or frontend?)
# ToDo: upd requirements


# ToDo: refactor to concurrency instead of asyncio
def runApi():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
    omniscient_pb2_grpc.add_AddPaymentServicer_to_server(AddPaymentServicer(), server)
    omniscient_pb2_grpc.add_QueryServicer_to_server(QueryServicer(), server)
    server.add_insecure_port("127.0.0.1:5003")
    # doesnt block
    server.start()
    # this thread doesnt really have anything left to do so we block it
    server.wait_for_termination()