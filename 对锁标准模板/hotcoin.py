import websocket
import json
import time
import datetime
import multiprocessing
from multiprocessing import Manager, Process, Queue

class hotcoin_wss(object):
    def __init__(self, queue):
        self.queue = queue
        self.url = 'wss://wss-ct.hotcoin.fit'
    def on_open(self, ws):
        # sub = '{"event": "subscribe","params": {"biz": "perpetual","type": "ticker","contractCode": "btcusdt","zip": false,"serialize": false}}'
        sub = '{"event": "subscribe","params": {"biz": "perpetual","type": "depth","contractCode": "btcusdt","zip": false,"serialize": false}}'
        ws.send(sub)
        pass
    def on_message(self, ws, message):
        if int(time.time()) % 240 == 0:
            ws.send('ping')
        rsl = json.loads(message)
        print(rsl)
        #print('hotcoin\t'+ str(datetime.datetime.fromtimestamp(rsl['data'][0][0] / 1000)) + ' buy ' + rsl['data'][0][9] + ' sell ' + rsl['data'][0][10])
        pass
    def on_error(self, ws, error):
        print(str(error))
    def on_close(self, ws, param1='', param2=''):
        self.connection_open_api()
    def connection_open_api(self):
        ws = websocket.WebSocketApp(self.url,
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        try:
            ws.run_forever(ping_interval=30)
        except:
            ws.close()
        return ws

class xt_wss(object):
    def __init__(self, queue):
        self.queue = queue
        self.url = 'wss://fstream.xt.com/ws/market?type=SYMBOL'   # 现货  将f去掉
        self.Symbollist = ['BTC']
        self.Steamlist = []
        self.allA =[]
        self.allB = []
        self.aPrice = 0
        self.bPrice = 0
        self.allSetA = set()
        self.allSetB = set()
    def on_open(self, ws):
        msg = '{"method":"subscribe","params":["ticker@btc_usdt","trade@btc_usdt","depth_update@btc_usdt","index_price@btc_usdt","mark_price@btc_usdt","fund_rate@btc_usdt"]}'
        ws.send(msg)
    def on_message(self, ws, message):
        if int(time.time()) % 10 == 0:
            ws.send('ping')
        try:
            rsl = json.loads(message)
            if rsl["topic"] == "depth_update":
                aparam = rsl["data"]["a"]
                bparam = rsl["data"]["b"]
                tparam = rsl['data']['t']
                for a in aparam:
                    if float(a[0]) in self.allA:
                        if a[1] == '0':
                            del self.allA[self.allA.index(float(a[0]))]
                    else:
                        if a[1] != '0':
                            self.allA.append(float(a[0]))
                for b in bparam:
                    if float(b[0]) in self.allB:
                        if b[1] == '0':
                            del self.allB[self.allB.index(float(b[0]))]
                    else:
                        if b[1] != '0':
                            self.allB.append(float(b[0]))
                bparam = rsl["data"]["b"]
                self.aPrice,self.bPrice = sorted(self.allA)[0],sorted(self.allB)[-1]
                #print('卖一', self.aPrice, '买一', self.bPrice)
                print('xt\t' + str(datetime.datetime.fromtimestamp(tparam / 1000)) + ' buy ' + str(float(self.bPrice)) + ' sell ' + str(float(self.aPrice)))
                #self.queue.put([[float(self.aPrice), float(self.bPrice)], 1, tparam])
        except :
            pass

    def on_error(self, ws, error):

        print(str(error))

    def on_close(self, ws, param='', param2=''):
        print(" Open Connection closed")
        self.connection_open_api()

    def connection_open_api(self):
        ws = websocket.WebSocketApp(self.url,
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        try:
            ws.run_forever(ping_interval=30)
        except:
            ws.close()
        return ws

class Work(object):

    def __init__(self, queue):
        self.queue = queue

    def domian(self):

        work1 = hotcoin_wss(self.queue)
        one = Process(target=work1.connection_open_api)
        one.start()

        #work2 = xt_wss(self.queue)
        #two = Process(target=work2.connection_open_api)
        #two.start()

        while True:
            data = self.queue.get()
            print(data)
        pass

if __name__ == '__main__':
    multiprocessing.freeze_support()
    queue = Queue()
    work = Work(queue)
    three = Process(target=work.domian)
    three.start()
    three.join()