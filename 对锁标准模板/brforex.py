#coding=utf-8
import requests
import time
import json
import threading
from send_email import save_data
json_name = "xt_bitforex_response日志.json"
try:
    with open('bitforex_cookie.json', encoding='utf-8') as file_obj:
        data_temp = json.load(file_obj)
    file_obj.close()
except Exception as e:
    print(e)
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'referer': 'https://www.bitforex.com/hk/perpetual/btc_usd',
    'cookie': data_temp['cookie'],
    'origin': 'https://www.bitforex.com',
    # 'content-length': 38,
    'content-type': "application/json;charset=UTF-8"
}

# 限价对手价
#开仓/限价
# 开多参数
# {"symbol":"swap-usd-btc","side":1,"source":"1","type":2,"transactionPin":"","orderQty":"2","price":0}
# 开空参数 orderQty 是数量美元
# {"symbol":"swap-usd-btc","side":2,"source":"1","type":2,"transactionPin":"","orderQty":"2","price":0}
# 单向持仓模式  平多单开空就行，平空单开多
# type等于1是限价，type等于2是市价
def get_cang(side, vulome, price,type):
    url = 'https://www.bitforex.com/contract/swap/order'
    data = {"symbol":"swap-usd-btc","side":side,"source":"1","type":type,"transactionPin":"","orderQty":vulome,"price": price}
    ts0 = time.time()
    response = requests.post(url,headers=headers,json=data).json()
    ts1 = time.time()
    temp = {}
    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    if side == 1:
        temp['bitforex'] = "开多"
    else:
        temp['bitforex'] = "开空"
    temp['延迟'] = ts1 - ts0
    temp['response'] = response
    t1 = threading.Thread(target=save_data, args=(temp, json_name))
    t1.start()
    print(response)
    return response

#平仓
def get_ping_cang():
    url = 'https://www.bitforex.com/contract/swap/position'
    data = {"price":24685,"orderQty":4,"type":4,"source":"1","symbol":"swap-usd-btc","transactionPin":""}
    response = requests.post(url,headers=headers,json=data).json()
    return response

#条件委托
def tiao_creat(side, vulome, price):
    # "fixedPrice": 24508.5,
    url = 'https://www.bitforex.com/contract/swap/condition/create'
    data = {"symbol":"swap-usd-btc","side":side,"source":"1","type":1,"transactionPin":"","direction":2,"priceType":1,"triggerPrice":"10","volume":vulome,"price":price,"fixedPrice": 24508.5}
    response = requests.post(url,headers=headers,json=data).json()
    return response
# orderId = tiao_creat()['data']['orderId']


#撤单
#time.sleep(15)
def che_creat(orderId):
    url = 'https://www.bitforex.com/contract/swap/order'
    data = {"orderId":f"{orderId}","source":"1","symbol":"swap-usd-btc"}
    print(data)
    response = requests.delete(url,headers=headers,json=data).json()
    return response

if __name__ == '__main__':
    # 方向 数量 0代表的是对手价
    # print(get_cang(1, 1, 19768)) # 开多
    # print(get_cang(2, 2, 0)) # 开空
    # orderId = tiao_creat(1,1,21986)['data']['orderId']
    # print(type(orderId))
    # print(orderId)
    # time.sleep(3)
    # print(che_creat('2161976712408603550'))
    # print(tiao_creat(1,1,24508)['data']['orderId'])
    t1 = threading.Thread(target=get_cang, args=(1, 1, 27500, 1))
    t1.start()
    pass