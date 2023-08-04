#coding=utf-8

import websocket
import json
from multiprocessing import Manager, Process, Queue

class Bkex_wss(object):

    def __init__(self, queue):
        self.queue = queue
        self.url = 'wss://fapi.bkex.com/fapi/v2/ws'

    def on_open(self, ws):
        sub = '{"event":"sub","topic":"btc_usdt.10deep"}'
        ws.send(sub)
        pass

    def on_message(self, ws, message):
        rsl = json.loads(message)
        print(rsl)
        try:
            print('ask', rsl['data']['asks'][0], 'bid', rsl['data']['bids'][0])
        except:
            pass
    def on_error(self, ws, error):
        print(str(error))

    def on_close(self, ws, param='', param2=''):
        self.connection_open_api()

    def connection_open_api(self):
        # 调试日志是否开启
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

if __name__ == '__main__':
    queue = Queue()
    bitget = Bkex_wss(queue)
    bitget.connection_open_api()


