import postgresql
from datetime import datetime
import sys
import uuid


def app():
    transaction_id = uuid.uuid4().hex
    dbFly = postgresql.open('pq://pstg_test:pstg_test@localhost:9990/pstg_test')
    insertFly = dbFly.prepare(
        "INSERT INTO fly_booking (client_name, fly_number, from_loc, to_loc, flying_date) VALUES ($1, $2, $3, $4, $5)")
    dbHotel = postgresql.open('pq://pstg_test:pstg_test@localhost:9991/pstg_test')
    insertHotel = dbHotel.prepare(
        "INSERT INTO hotel_booking (client_name, hotel_name, arrival_date, departure_date) VALUES ($1, $2, $3, $4)")
    dbAccount = postgresql.open('pq://pstg_test:pstg_test@localhost:9992/pstg_test')
    updateAccount = dbAccount.prepare("UPDATE accounts SET ammount = ammount - $1 WHERE client_name = $2")

    try:
        dbFly.execute("begin;")
        insertFly("a", "b", 'c', 'd', datetime.now())
        dbFly.execute("PREPARE TRANSACTION '"+transaction_id+"';")
    except postgresql.exceptions.CheckError:
        return 1

    try:
        dbHotel.execute("begin;")
        insertHotel("a", "b", datetime.now(), datetime.now())
        dbHotel.execute("PREPARE TRANSACTION '"+transaction_id+"';")
    except postgresql.exceptions.CheckError:
        dbFly.execute("ROLLBACK PREPARED '"+transaction_id+"';")
        return 1

    try:
        dbAccount.execute("begin;")
        updateAccount(50, 'a')
        dbAccount.execute("PREPARE TRANSACTION '"+transaction_id+"';")
    except postgresql.exceptions.CheckError:
        dbFly.execute("ROLLBACK PREPARED '"+transaction_id+"';")
        dbHotel.execute("ROLLBACK PREPARED '"+transaction_id+"';")
        return 1

    dbFly.execute("COMMIT PREPARED '"+transaction_id+"';")
    dbHotel.execute("COMMIT PREPARED '"+transaction_id+"';")
    dbAccount.execute("COMMIT PREPARED '"+transaction_id+"';")
    return 0

if __name__ == "__main__":
    sys.exit(app())

