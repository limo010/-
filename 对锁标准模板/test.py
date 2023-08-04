import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(data)

def on_error(ws, error):
    print(error)
    pass

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    req = '{"time" : 123456, "channel" : "futures.order_book", "event": "subscribe", "payload" : ["BTC_USDT", "20", "0"]}'
    ws.send((req))

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://fx-ws.gateio.ws/v4/ws/usdt",
                                on_open = on_open,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
