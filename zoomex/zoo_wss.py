#coding=utf-8
import ssl
import websocket
import json
from multiprocessing import Manager, Process, Queue

class Bkex_wss(object):

    def __init__(self, queue):
        self.queue = queue
        self.url = 'wss://stream.zoomex.com/usdt_public'

    def on_open(self, ws):
        # ws.send('{"op": "subscribe", "args": ["orderBookL2_25.BTCUSDT-Perp"]}')
        ws.send('{"op": "subscribe", "args": ["instrument_info.100ms.BTCUSDT-Perp"]}')
        pass

    def on_message(self, ws, message):
        rsl = json.loads(message)
        # print(rsl)
        try:
            # print(rsl)
            print(rsl['data']['update'][0]['last_price'])
            # print('卖一', rsl['data']['update'][0]['price'],'买一', rsl['data']['update'][1]['price'])
        except:
            pass
    def on_error(self, ws, error):
        print("报错")
        print(str(error))

    def on_close(self, ws, param='', param2=''):
        print('关闭')
        self.connection_open_api()

    def connection_open_api(self):
        # 调试日志是否开启
        ws = websocket.WebSocketApp(self.url,
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        try:
            ws.run_forever(ping_interval=30, sslopt={"cert_reqs": ssl.CERT_NONE})
            print("连接成功!!!")
        except:
            ws.close()
        return ws

if __name__ == '__main__':
    queue = Queue()
    bitget = Bkex_wss(queue)
    bitget.connection_open_api()


