import requests
from fake_headers import Headers
import time
import json
import threading
from json_create import save_data
json_name = "zoo_xt_BTC_response日志.json"
headers = Headers()
user_agent = headers.generate()['User-Agent']
url = "https://api2.zoomex.com/v3/linear/private/order/create"
# 读取cookie
try:
    with open('zoo_cookie.json', encoding="utf-8") as file_obj:
        data_temp = json.load(file_obj)
    file_obj.close()
except Exception as e:
    print(e)

cookie = data_temp['cookie']
Usertoken = data_temp['Usertoken']

# 读取开仓的数量
try:
    with open('volume.json', encoding="utf-8") as file_obj:
        volume_temp = json.load(file_obj)
    file_obj.close()
except Exception as e:
    print(e)

qty = volume_temp['zoo_volume']
qtyX = volume_temp['zoo_volume'] * 100000000

def generte_headers(cookie):
    headers = Headers()
    user_agent = headers.generate()['User-Agent']
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Content-Length": "415",
        "Content-Type": "application/json",
        "Guid": "4fd04c3f-6f46-a984-5e28-3643fc15a869",
        "Origin": "https://www.zoomex.com",
        "Platform": "pc",
        "Referer": "https://www.zoomex.com/",
        "Usertoken": Usertoken,
        "X-Client-Tag": "00-7171ddcfd019b39d6460ac5d1cc18313-c74f426f49e619be-01",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "cookie": cookie,
        "User-Agent": user_agent
    }
    return headers

# 开多
data = {
    "basePrice": "",
    "closeOnTrigger": False,
    "leverageE2": "10000",
    "orderType": "Market",
    "positionIdx": 1,
    "price": "",
    "qtyX": qtyX,   # 300000  = 0.003 btc
    "reduceOnly": False,
    "side": "Buy",
    "slTriggerBy": "LastPrice",
    "symbol": "BTCUSDT-Perp",
    "timeInForce": "ImmediateOrCancel",
    "tpTriggerBy": "LastPrice",
    "type": "Activity",
    "triggerBy": "LastPrice",
    "triggerPrice": "",
    "action": "Open",
    "qtyType": 0,
    "qtyTypeValue": 0,
    "preCreateId": "",
    "coin": "BTC"
}

# 开空
data2 = {
    "basePrice": "",
    "closeOnTrigger": False,
    "leverageE2": "10000",
    "orderType": "Market",
    "positionIdx": 2,
    "price": "",
    "qtyX": qtyX,
    "reduceOnly": False,
    "side": "Sell",
    "slTriggerBy": "LastPrice",
    "symbol": "BTCUSDT-Perp",
    "timeInForce": "ImmediateOrCancel",
    "tpTriggerBy": "LastPrice",
    "type": "Activity",
    "triggerBy": "LastPrice",
    "triggerPrice": "",
    "action": "Open",
    "qtyType": 0,
    "qtyTypeValue": 0,
    "preCreateId": "",
    "coin": "BTC"
}

# 平多
data3 = {
    "basePrice": "",
    "closeOnTrigger": False,
    "leverageE2": "10000",
    "leverage": "100",
    "orderType": "Market",
    "positionIdx": 1,
    "price": "",
    "qtyX": qtyX,
    "qty": qty,
    "reduceOnly": False,
    "side": "Sell",
    "symbol": "BTCUSDT-Perp",
    "timeInForce": "GoodTillCancel",
    "type": "Activity",
    "action": "Close",
    "preCreateId": ""
}

# 平空
data4 = {
    "basePrice": "",
    "closeOnTrigger": False,
    "leverageE2": "10000",
    "leverage": "100",
    "orderType": "Market",
    "positionIdx": 2,
    "price": "",
    "qtyX": qtyX,
    "qty": qty,
    "reduceOnly": False,
    "side": "Buy",
    "symbol": "BTCUSDT-Perp",
    "timeInForce": "GoodTillCancel",
    "type": "Activity",
    "action": "Close",
    "preCreateId": ""
}

headers = generte_headers(cookie)

def open_buy():
    ts1 = time.time()
    response = requests.post(url=url, headers=headers, json=data)
    ts2 = time.time()
    result = response.json()
    print('开多', result)
    print("延迟", ts2-ts1)
    temp = {}
    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    temp['zoo'] = "开多"
    temp['延迟'] = ts2-ts1
    temp['response'] = result
    t1 = threading.Thread(target=save_data, args=(temp, json_name))
    t1.start()

def open_sell():
    ts1 = time.time()
    response = requests.post(url=url, headers=headers, json=data2)
    ts2 = time.time()
    result = response.json()
    print('开空', result)
    print("延迟", ts2-ts1)
    temp = {}
    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    temp['zoo'] = "开空"
    temp['延迟'] = ts2-ts1
    temp['response'] = result
    t1 = threading.Thread(target=save_data, args=(temp, json_name))
    t1.start()

def close_buy():
    ts1 = time.time()
    response = requests.post(url=url, headers=headers, json=data3)
    ts2 = time.time()
    result = response.json()
    print('平多', result)
    print("延迟", ts2-ts1)
    temp = {}
    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    temp['zoo'] = "平多"
    temp['延迟'] = ts2-ts1
    temp['response'] = result
    t1 = threading.Thread(target=save_data, args=(temp, json_name))
    t1.start()

def close_sell():
    ts1 = time.time()
    response = requests.post(url=url, headers=headers, json=data)
    ts2 = time.time()
    result = response.json()
    print('平空', result)
    print("延迟", ts2-ts1)
    temp = {}
    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    temp['zoo'] = "平空"
    temp['延迟'] = ts2-ts1
    temp['response'] = result
    t1 = threading.Thread(target=save_data, args=(temp, json_name))
    t1.start()


if __name__ == '__main__':
    close_sell()

