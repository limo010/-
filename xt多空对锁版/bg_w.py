import websocket
import json
from multiprocessing import Queue, Process, Value
import threading
import time
from datetime import datetime

class SymbolWApp(websocket.WebSocketApp):
    def __init__(self, url, header=None, on_open=None, on_message=None, on_error=None, on_close=None, on_ping=None, on_pong=None, on_cont_message=None, keep_running=True, get_mask_key=None, cookie=None, subprotocols=None, on_data=None, socket=None):
        super().__init__(url, header, on_open, on_message, on_error, on_close, on_ping, on_pong, on_cont_message, keep_running, get_mask_key, cookie, subprotocols, on_data, socket)
        self._symbol = 'BTCUSDT'

def on_open_bg(ws):

    ws.send(json.dumps({
            "op":"subscribe",
            "args":[
                {
                    "instType":"mc",
                    "channel":"books1",
                    "instId":ws._symbol
                }
            ]
        }))
    
    def keep_alive():
        if ws.sock and ws.sock.connected:
            ws.send('ping')
            t = threading.Timer(25, keep_alive)
            t.start()

    print("Connection established")
    keep_alive()


def on_message_bg(ask: Value, bid: Value, message: str):
    """处理WebSocket接收到的消息"""
    data = json.loads(message)
    try:
        if data['data']:

            a = float(data['data'][0]['asks'][0][0])
            b = float(data['data'][0]['bids'][0][0])
            ask.value = a
            bid.value = b
            print(f'{datetime.now().strftime("%H:%M:%S.%f")} xt', ask.value, bid.value)
            time.sleep(0.01)

    except Exception as e:
        pass

def on_close_bg(ws):
    print('连接关闭bitget')

def on_error_bg(ws, error):
    pass


def ws_bg(ask: Value, bid: Value, symbol: str):
    """WebSocket进程,用于获取ETH Ticker数据"""
    socket = f'wss://ws.bitget.com/mix/v1/stream'
    ws = SymbolWApp(socket,on_message=lambda ws, msg: on_message_bg(ask, bid, msg),on_open=on_open_bg,on_error=on_error_bg)
    ws._symbol = symbol
    ws.run_forever(ping_interval=25,ping_timeout=10)

if __name__ == '__main__':
    h_ask_eth = Value('f', 0.0)
    h_bid_eth = Value('f', 0.0)
    symbol = "BTCUSDT"
    p = Process(target=ws_bg, args=(h_ask_eth,h_bid_eth,symbol,))
    p.start()
   
