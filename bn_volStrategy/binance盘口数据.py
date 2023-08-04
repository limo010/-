import requests
import json
import multiprocessing
from multiprocessing import Manager, Process, Queue
import websocket
import ssl
import random
class Bn_data_wss(object):

    def __init__(self, queue, List, symbol):
        self.queue = queue
        self.List = List
        self.list = []
        self.list_asks = []
        self.list_bids = []
        url = 'wss://stream.binance.com'   # 现货  将f去掉
        self.Symbollist = [symbol]
        self.Steamlist = []
        for symbol in self.Symbollist:
            self.Steamlist.append(symbol.lower() + 'usdt@depth20@100ms')   # @aggTrade (最新成交价)  depth5@100ms（深度）
        if len(self.Steamlist) == 1:
            self.open_url = url + '/ws/' + self.Steamlist[0]
        else:
            parameters = '/stream?streams='
            for v in self.Steamlist:
                parameters += f"{v}/"
            parameters = parameters[:-1]
            self.open_url = url + parameters

    def on_open(self, ws):
        pass

    def on_message(self, ws, message):
        if message == 'ping':
            ws.send('pong')
        rsl = json.loads(message)
        # print(rsl)
        if len(self.Steamlist) == 1:
            stream = self.Symbollist
            data = rsl
        else:
            if 'data' in rsl:
                stream = rsl['stream']
                data = rsl['data']
            else:
                print('非正常数据')
                return ws
        sum_asks = 0
        sum_bids = 0
        for value in rsl['asks']:
            # print('ask', value)
            sum_asks = sum_asks + float(value[1])
        for value in rsl['bids']:
            # print('bid', value)
            sum_bids = sum_bids + float(value[1])
        # print("asks总值", sum_asks, "bids总值", sum_bids, 'asks-bids差值', sum_asks - sum_bids)
        self.list.append(sum_bids - sum_asks)
        self.list_asks.append(sum_asks)
        self.list_bids.append(sum_bids)
        L1 = random.randint(1, 7500)
        if L1 == 100:
            print('币安合约价格推送正常运行中')
        if len(self.list) > 1000:
            print("买票1000次平均值 - 卖盘1000次平均值", sum(self.list_bids)/len(self.list_bids) - sum(self.list_asks)/len(self.list_asks))
            del self.list[0]
            del self.list_asks[0]
            del self.list_bids[0]
        # # price_zuixin = data['p']
        # for symbol in self.Symbollist:
        #     if symbol.lower() in stream or symbol.upper() in stream:
        #         print("最新价:"+str(price_zuixin))
        #         # self.queue.put([[float(price_zuixin),0], 0])
        #         # self.List[0] = float(price_zuixin)
        #         break

    def on_error(self, ws, error):

        print(str(error))

    def on_close(self, ws, param='', param2=''):
        print("Binance Open Connection closed")
        self.connection_open_api()

    def connection_open_api(self):
        # websocket.enableTrace(True)
        # 调试日志是否开启
        ws = websocket.WebSocketApp(self.open_url,
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        try:
            ws.run_forever(ping_interval=30, sslopt={"cert_reqs": ssl.CERT_NONE})
        except:
            ws.close()
        return ws

if __name__ == '__main__':
    multiprocessing.freeze_support()
    List = Manager().list()
    List.append(0)
    queue = Queue()
    work2 = Bn_data_wss(queue, List, "BTC")
    two = Process(target=work2.connection_open_api)
    two.start()