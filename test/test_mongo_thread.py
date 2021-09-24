from easyquant import MongoIo
from threading import Thread
import time

mongo=MongoIo()
PAGE_SUM=100

class to_mongo_pool(Thread):
    def __init__(self, idx):
        Thread.__init__(self)
        # self.code = code
        self.idx = idx

        self.data = {"positionId": self.idx, "data": "data=%d" % self.idx}
    def run(self):
        save_to_mongo(self.data)


def save_to_mongo(data):
    db = mongo.db
    if db["test-mp"].update_one({'positionId': data['positionId']}, {'$set': data}, True):
        print('Saved to Mongo', data['positionId'])
    else:
        print('Saved to Mongo Failed', data['positionId'])

start_time = time.time()
pool = []
for i in range(PAGE_SUM):
    pool.append(to_mongo_pool(i))

for c in pool:
    c.start()

for c in pool:
    c.join()

# pool.map(to_mongo_pool,[i for i in range(PAGE_SUM)])
#
# pool.close()

# pool.join()

end_time = time.time()

print("总耗费时间%.2f秒" % (end_time - start_time))