import hashlib
import hmac
import json
import requests
import urllib3
import time
from send_email import save_data
import threading
json_name = "binance_zoo_BTC_response日志.json"
def create_order(apiKey,secretKey,symbol,side,order_type,qty,price, position_idx):
    timestamp = int(time.time() * 10 ** 3)
    params = {
        "side": side,
        "symbol": symbol,
        "order_type": order_type,
        "qty": qty,
        "price": price,
        "time_in_force": "PostOnly",
        "api_key": apiKey,
        "timestamp": str(timestamp),
        "recv_window": "5000",
        "reduce_only": False,
        "close_on_trigger": False,
        "position_idx": position_idx
    }
    sign = ''
    for key in sorted(params.keys()):
        v = params[key]
        if isinstance(params[key], bool):
            if params[key]:
                v = 'true'
            else :
                v = 'false'
        sign += key + '=' + v + '&'
    sign = sign[:-1]
    hash = hmac.new(secretKey, sign.encode("utf-8"), hashlib.sha256)
    signature = hash.hexdigest()
    sign_real = {
        "sign": signature
    }
    # url = 'https://openapi.zoomex.com/private/linear/order/create'
    url = 'https://openapi.zoomex.com/private/v1/order/create/usdt'
    headers = {"Content-Type": "application/json"}
    body = dict(params,**sign_real)
    urllib3.disable_warnings()
    s = requests.session()
    s.keep_alive = False
    ts0 = time.time()
    response = requests.post(url, data=json.dumps(body), headers=headers,verify=False)
    ts1 = time.time()
    print('延迟', ts1-ts0)
    temp = {}
    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    if side == "Buy" and position_idx == "1":
        temp['xt'] = "开多"
    elif side == 'Buy' and position_idx == "2":
        temp['xt'] = "平空"
    elif side == 'Sell' and position_idx == "2":
        temp['xt'] = "开空"
    else:
        temp['xt'] = '平空'
    temp['延迟'] = ts1 - ts0
    temp['response'] = response.text
    t1 = threading.Thread(target=save_data, args=(temp, json_name))
    t1.start()
    print(response.text)

def main():
    apiKey = "rD7nfjacvdRB9ogWuw"
    secret = b"FwsujmWdGEet7S4ZC3FB5yIp7hqIrTGvxLco"
    # create_order(apiKey, secret,'UNIUSDT','Buy','Limit','1','10')
    create_order(apiKey, secret,'BTCUSDT-Perp','Buy','Market','0.001','0', '0') #for market order, we are just passing the price as 0

if __name__ == '__main__':
    main()