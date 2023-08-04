#coding=utf-8
import ssl
import websocket
import json
from multiprocessing import Manager, Process, Queue
import time
class Bkex_wss(object):

    def __init__(self, queue):
        self.queue = queue
        time = self.get_millisecond()
        self.url = 'wss://ws2.zoomex.com/realtime_loc_w?timestamp=' + str(time)
        print(self.url)

    def get_millisecond(slef):
        """
        :return: 获取精确毫秒时间戳,13位
        """
        millis = int(round(time.time() * 1000))
        return millis

    def on_open(self, ws):
        ws.send('{op: "unsubscribe", args: ["index_quote_20.H.BTCUSDT.1"]}')
        print(1)
        pass

    def on_message(self, ws, message):
        rsl = json.loads(message)
        # print(rsl)
        try:
            # print(rsl)
            print('卖一', rsl['data']['update'][0]['price'],'买一', rsl['data']['update'][1]['price'])
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
                                    on_close=self.on_close,
                                    header={
                                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50'
                                    })
        try:
            ws.run_forever(ping_interval=30)
            print("连接成功!!!")
        except:
            ws.close()
        return ws

if __name__ == '__main__':
    queue = Queue()
    bitget = Bkex_wss(queue)
    bitget.connection_open_api()


