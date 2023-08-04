import websocket
import json
import random
from multiprocessing import Manager, Process, Queue
import multiprocessing


class Work1(object):

    def __init__(self, queue):
        self.queue = queue
        url = 'wss://stream.zoomex.com/usdt_public'   # 现货  将f去掉
        self.Symbollist = ['BTC']
        self.Steamlist = []
        for symbol in self.Symbollist:
            self.Steamlist.append(symbol.lower() + 'usdt@aggTrade')   # @aggTrade (最新成交价)  depth5@100ms（深度）
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

        L1 = random.randint(1, 7500)
        if L1 == 100:
            print('币安合约价格推送正常运行中')
        # print(data)
        # price_buy = data['a'][0][0]  # eth asks
        # price_sell = data['b'][0][0]  # eth bids
        price_zuixin = data['p']
        temp = {}
        for symbol in self.Symbollist:
            if symbol.lower() in stream or symbol.upper() in stream:
                # print('%s买一价：%s，卖一价：%s' % (symbol, str(price_buy), str(price_sell)))
                # print("最新价:"+str(price_zuixin))
                # temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                # self.progress_list[0] = [float(price_buy), float(price_sell)]
                self.queue.put([[float(price_zuixin),0], 0])
                break

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
            ws.run_forever(ping_interval=30)
        except:
            ws.close()
        return ws


if __name__ == '__main__':
    multiprocessing.freeze_support()
    queue = Queue()
    work1 = Work1(queue)