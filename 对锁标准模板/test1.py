from send_email import save_data
import random
# bkex开单
from bkex_create_order_rest import ping_bkex, main
# xt开单
from xt_create_order_rest import open_order, close_all
import multiprocessing
from multiprocessing import Queue, Process
import json
import websocket
import time
import threading
import json
json_name = "gate_xt_BTC日志.json"

class gate_wss(object):

    def __init__(self, queue):
        self.queue = queue
        self.url = 'wss://fx-ws.gateio.ws/v4/ws/usdt'

    def on_open(self, ws):
        sub = '{"time" : 123456, "channel" : "futures.order_book", "event": "subscribe", "payload" : ["BTC_USDT", "20", "0"]}'
        ws.send(sub)
        pass

    def on_message(self, ws, message):
        rsl = json.loads(message)
        # print(rsl)
        try:
            print('ask', rsl['result']['asks'][0]['p'], 'bids', rsl['result']['bids'][0]['p'])
            self.queue.put([[float(rsl['result']['asks'][0]['p']), float(rsl['result']['bids'][0]['p'])],0])
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
    gate = gate_wss(queue)
    one = Process(target=gate.connection_open_api)
    one.start()
