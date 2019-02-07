import postgresql
from kafka import KafkaConsumer, KafkaProducer
import multiprocessing
from json import JSONEncoder, JSONDecoder
from datetime import datetime

class AmmountWorker(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        dbAccount = postgresql.open('pq://pstg_test:pstg_test@localhost:9992/pstg_test')

        consumer = KafkaConsumer(bootstrap_servers='localhost:9092', consumer_timeout_ms=1000)
        consumer.subscribe(['hotel-registered'])

        while not self.stop_event.is_set():
            for message in consumer:
                producer = KafkaProducer(bootstrap_servers='localhost:9092')
                print(message)
                try:
                    updateAccount = dbAccount.prepare(
                        "UPDATE accounts SET ammount = ammount - $1 WHERE client_name = $2")
                    updateAccount(100000, 'a')
                    producer.send('funds-withdrawn', message.value)
                except postgresql.exceptions.CheckError:
                    producer.send('funds-withdrawn-error', message.value)
                producer.close()

class FlyCancelerWorker(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        dbFly = postgresql.open('pq://pstg_test:pstg_test@localhost:9990/pstg_test')
        deleteFlyBook = dbFly.prepare("delete from fly_booking where booking_id = $1")

        consumer = KafkaConsumer(bootstrap_servers='localhost:9092', consumer_timeout_ms=1000)
        consumer.subscribe(['funds-withdrawn-error'])

        while not self.stop_event.is_set():
            for message in consumer:
                dic = JSONDecoder().decode(str(message.value, 'utf-8'))
                deleteFlyBook(dic['fly_booking_id'])
                producer = KafkaProducer(bootstrap_servers='localhost:9092')
                producer.send('fly-calnceled', message.value)
                producer.close()

class FlyRegistratorWorker(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        dbFly = postgresql.open('pq://pstg_test:pstg_test@localhost:9990/pstg_test')
        insertFly = dbFly.prepare(
            "INSERT INTO fly_booking (client_name, fly_number, from_loc, to_loc, flying_date) VALUES ($1, $2, $3, $4, $5) RETURNING booking_id")

        consumer = KafkaConsumer(bootstrap_servers='localhost:9092', consumer_timeout_ms=1000)
        consumer.subscribe(['booking_initiated'])

        while not self.stop_event.is_set():
            for message in consumer:
                res = insertFly("a", "b", 'c', 'd', datetime.now())
                dic = {
                    'fly_booking_id': res[0].get(0)
                }
                producer = KafkaProducer(bootstrap_servers='localhost:9092')
                producer.send('fly-registered', bytes(JSONEncoder().encode(dic), encoding='utf-8'))
                producer.close()

class HotelCancelerWorker(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        dbHotel = postgresql.open('pq://pstg_test:pstg_test@localhost:9991/pstg_test')
        deleteHolelBook = dbHotel.prepare("delete from hotel_booking where booking_id = $1")

        consumer = KafkaConsumer(bootstrap_servers='localhost:9092', consumer_timeout_ms=1000)
        consumer.subscribe(['funds-withdrawn-error'])

        while not self.stop_event.is_set():
            for message in consumer:
                dic = JSONDecoder().decode(str(message.value, 'utf-8'))
                deleteHolelBook(dic['hotel_booking_id'])
                producer = KafkaProducer(bootstrap_servers='localhost:9092')
                producer.send('hotel-calnceled', message.value)
                producer.close()

class HotelRegistratorWorker(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        dbHotel = postgresql.open('pq://pstg_test:pstg_test@localhost:9991/pstg_test')
        insertHotel = dbHotel.prepare(
            "INSERT INTO hotel_booking (client_name, hotel_name, arrival_date, departure_date) VALUES ($1, $2, $3, $4) RETURNING booking_id")

        consumer = KafkaConsumer(bootstrap_servers='localhost:9092', consumer_timeout_ms=1000)
        consumer.subscribe(['fly-registered'])

        while not self.stop_event.is_set():
            for message in consumer:
                res = insertHotel("a", "b", datetime.now(), datetime.now())
                dic = JSONDecoder().decode(str(message.value, 'utf-8'))
                dic['hotel_booking_id'] = res[0].get(0)
                producer = KafkaProducer(bootstrap_servers='localhost:9092')
                producer.send('hotel-registered', bytes(JSONEncoder().encode(dic), encoding='utf-8'))
                producer.close()
