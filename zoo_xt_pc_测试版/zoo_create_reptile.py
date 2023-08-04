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
try:
    with open('zoo_cookie.json', encoding="utf-8") as file_obj:
        cookie_temp = json.load(file_obj)
    file_obj.close()
except Exception as e:
    print(e)

# cookie = """_by_l_g_d=5a6185c4-b81b-8d10-d021-b41ab65198b0; HMF_CI=362ec59bf670e7248ef757eb7661a21db0afa87b12bd3f3bf37b8fcf535e9d62afb990639c826858ab87203346efe92e9a3cf9a83f1c1b13b02b38aadef8be1aa6; sajssdk_2015_cross_new_user=1; _gid=GA1.2.361900216.1685685859; LANG_KEY=zh-TW; REGION_ZO_REG_AFF={"lang":"zh-TW","g":"5a6185c4-b81b-8d10-d021-b41ab65198b0","tdid":"31851b34-8eb1-4912-b47e-91d0a817b81c","platform":"web","app_id":10006,"source":"zoomex.com","medium":"","referrer":"www.zoomex.com/trade/usdt/BTCUSDT","url":"https://www.zoomex.com/zh-TW/login"}; sensorsdata2015jssdkcross={"distinct_id":"66968214","first_id":"1887ab4f3282f1-03d8ab5e76b1b0a-26021051-2073600-1887ab4f329418","identities":"eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTg4N2FiNGYzMjgyZjEtMDNkOGFiNWU3NmIxYjBhLTI2MDIxMDUxLTIwNzM2MDAtMTg4N2FiNGYzMjk0MTgiLCIkaWRlbnRpdHlfbG9naW5faWQiOiI2Njk2ODIxNCJ9","history_login_id":{"name":"$identity_login_id","value":"66968214"},"$device_id":"1887ab4f3282f1-03d8ab5e76b1b0a-26021051-2073600-1887ab4f329418"}; self-unbind-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNZW1iZXJJRCI6NjY5NjgyMTQsIkxvZ2luU3RhdHVzIjoyLCJzdWIiOiJzZWxmX3VuYmluZCIsImV4cCI6MTY4NTcyNDg1NSwibmJmIjoxNjg1NzIxMjU1fQ.ivtuvLSrgSyqveoeNAZjbgahRVg9abWQ2CBN-4vRRPY; secure-token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODU5ODA0OTEsInVzZXJfaWQiOjY2OTY4MjE0LCJub25jZSI6IjQzOTExYzAyIiwiZ2VuX3RzIjoxNjg1NzIxMjkxLCJwIjozLCJiIjoxLCJleHQiOnsibWN0IjoiMTY4NDY1NTQxNiIsInNpZCI6IktPUkVBIn19.5Trlmz0vmdFIw2J1wskLYPxgTzhT7d4rlnLdVM2fhHYzejbRYLjTSSyklsbhaVz_18YJFkz_ewSArWJG_f0bcg; b_t_c_k=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODU5ODA0OTEsInVzZXJfaWQiOjY2OTY4MjE0LCJub25jZSI6IjQzOTExYzAyIiwiZ2VuX3RzIjoxNjg1NzIxMjkxLCJwIjozLCJiIjoxLCJleHQiOnsibWN0IjoiMTY4NDY1NTQxNiIsInNpZCI6IktPUkVBIn19.PjwAQ9Jg_EDBk-rOgTcz6U-LGH4L_CIpZJ7nYBC2gq4; _ga_6C3WHZC2VW=GS1.1.1685721304.3.0.1685721304.0.0.0; _ga=GA1.1.1923950212.1685685859; _ga_E1M05R283H=GS1.1.1685721304.3.0.1685721304.0.0.0; _ga_R0JK8HS939=GS1.1.1685721304.3.1.1685721339.0.0.0"""
cookie = ""
Usertoken = cookie_temp['Usertoken']

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
    close_buy()

