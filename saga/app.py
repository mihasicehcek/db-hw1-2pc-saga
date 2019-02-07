import sys

from workers import AmmountWorker, FlyCancelerWorker, FlyRegistratorWorker, HotelCancelerWorker, HotelRegistratorWorker

workers = [
    AmmountWorker(),
    FlyCancelerWorker(),
    FlyRegistratorWorker(),
    HotelCancelerWorker(),
    HotelRegistratorWorker()
]


for worker in workers:
    worker.start()

print("Workers are started")

for line in sys.stdin:
    if line == "q\n":
        print("workers are stopping")
        for worker in workers:
            worker.stop()
        for worker in workers:
            worker.join()
        print('workers stoped')
        sys.exit(0)


