from easyquant import EasyMq

def callback(a, b, c, data):
    print(data)

easymq = EasyMq()
easymq.init_receive(exchange="stockcn.idx")
easymq.callback = callback
easymq.add_sub_key(routing_key="512880")
easymq.start()

# sleep(100)
