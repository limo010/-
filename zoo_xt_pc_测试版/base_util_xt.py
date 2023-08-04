#coding=utf-8
# 现价开仓平仓 一键平仓  持仓查询
import requests
import time
import json
import threading
from json_create import save_data
json_name = "zoo_xt_BTC_response日志.json"
try:
    with open('xt_cookie.json', encoding="utf-8") as file_obj:
        data_temp = json.load(file_obj)
    file_obj.close()
except Exception as e:
    print(e)

headers = {
    'accept': 'application/json,text/plain,*/*',
    'accept-encoding': 'gzip,deflate,br',
    'authorization': data_temp['authorization'],
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

# 持仓查询
def get_hold():
    try:
        url = "https://www.xt.com/fapi/user/v1/position/list?isPredict=true&isDelivery=true"
        response = requests.get(url=url, headers=headers)  # .content.decode()
        print(response)
        result = response.json()
        try:
            for value in result['result']:
                print(value['symbol'],value['positionSide'],str(value['positionSize'])+"张")
        except Exception as e:
            print(e)
        # print(result)
    except Exception as e:
        print(e)

def open_order(symbol,origQty,orderSide,positionSide,price):
    url = "https://www.xt.com/fapi/trade/v1/order/create"
    form_data = {
        'symbol': symbol,
        'origQty': origQty,
        'triggerPriceType': 'MARK_PRICE',
        'orderType': 'MARKET',
        'price': price,
        'timeInForce': 'IOC',
        'orderSide': orderSide,
        'positionSide': positionSide}
    ts0 = time.time()
    response = requests.post(url=url, headers=headers, data = form_data)
    ts1 = time.time()
    temp = {}
    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    if orderSide == "BUY":
        temp['xt'] = "开多"
    else:
        temp['xt'] = "开空"
    temp['延迟'] = ts1 - ts0
    temp['response'] = response.text
    t1 = threading.Thread(target=save_data, args=(temp, json_name))
    t1.start()
    print(response.text)

def close_all():
    url = "https://www.xt.com/fapi/user/v1/position/close-all"
    ts0 = time.time()
    response = requests.post(url=url, headers=headers)
    ts1 = time.time()
    temp = {}
    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    temp['xt'] = "平仓"
    temp['延迟'] = ts1-ts0
    temp['response'] = response.text
    t1 = threading.Thread(target=save_data, args=(temp, json_name))
    t1.start()
    print(response.text)

def get_xt_account():
    url = 'https://www.xt.com/fapi/user/v1/compat/balance/list'
    response = requests.get(url,headers=headers)
    # print('xt账户余额', response.json())
    return float(response.json()['result'][0]['totalAmount'])

def get_xt_profit():
    url = 'https://www.xt.com/fapi/user/v1/compat/balance/list'
    response = requests.get(url,headers=headers)
    print('xt账户余额', response.json())
    return (response.json())

if __name__ == '__main__':
    ts0 = time.time()
    # open_order('btc_usdt',50,'BUY','LONG',0) # 限价开多0.0005
    # ts1 = time.time()
    # print("延迟", ts1-ts0)
    # open_order('btc_usdt', 5, 'SELL', 'SHORT',27110)  # 限价开空0.0005
    # ts1 = time.time()
    # print("延迟", ts1-ts0)
    # close_all() # 一键平仓
    # xt账户余额查询
    print(get_xt_account())
    ts1 = time.time()
    print("延迟", ts1-ts0)
    # open_order('btc_usdt', 5, 'BUY', 'SHORT', 25070)#买入平空
    # open_order('btc_usdt', 5, 'SELL', 'LONG', 30000)  # 卖出平多
