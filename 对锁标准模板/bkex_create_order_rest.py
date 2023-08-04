#coding=utf-8

import requests
import time
import json
import threading
from send_email import save_data
json_name = "bkex_xt_BTC_response日志.json"
# 获取cookie
try:
    with open('bkex_cookie.json', encoding="utf-8") as file_obj:
        data_temp = json.load(file_obj)
    file_obj.close()
except Exception as e:
    print(e)
headers_2 = {
        'user-agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'accept-language': 'zh-cn',
        'future_source': '1',
        'authorization': data_temp['authorization'],
        'future_token': 'dd5d1f192640800c5c1fa70278a04c56abf6da857e2f3f26c2a6dfea43aa526e',
        'phpsessid': 'dd5d1f192640800c5c1fa70278a04c56abf6da857e2f3f26c2a6dfea43aa526e',
        # 'cookie':'_cfuvid=Dm_C52kHVOBGFYX3hvtLZAjKX5qXBBspOx6Is4W7UFc-1679464126551-0-604800000; lang=zh; upDownTheme=greenUpRedDown; defaultExchangeRate=ALL; ga_cookie_ga=GA1.2.612917342.1679464227; ga_cookie_ga_gid=GA1.2.1822655824.1679464227; _ga=GA1.2.612917342.1679464227; _gid=GA1.2.1116104081.1679464227; deviceId=ed876c2b6c367c9862cdc31f9f256804; token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ6Z2xpbGlhbmc5ODhAMTI2LmNvbSIsInVzZXJJZCI6IjIwMjIxMTAyMTIwNDEwMDk5MzAwMDg2ODkiLCJpcCI6IjQzLjE1NC4yNS41MiIsImlhdCI6MTY3OTQ2NDMyNCwiZXhwIjoxNjgyMDU2MzI0fQ.cjVxDhQe6JAVe2glg1M15EYpbgB-ifxdk9yGPhoNcQE; locale=zh-cn; i18next=zh; bun=zglilian****@126.com; phpsessid=d265dcdae7d440d982c3794ce250459ed2a8bd965209f80cb49efaa8b2b538e9; __cf_bm=THJ63Cs2h8BfEzkehAOWqd9.cIqXLIC.a_7QsvcCmo0-1679467970-0-AdjcGL18lwEaERv8855Qnqh46t5F3SLPMVW01j9hKa1IpaSFg2lmXigFFX0CmsFHCn9OK6ggBZjbSlhLjVIVvFA=',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://swap.bkex.com',
        'referer': 'https://swap.bkex.com/contract/LIVE_USDT/btc_usdt',
    }

def main(a,user1):
    if user1 == '开多':
        data = '{"symbol":"btc_usdt","side":1,"type":2,"amount":"'+str(a)+'","leverage":100,"triggerType":1,"openType":1}:'#amoun参数调整数量
        ts0 = time.time()
        response = requests.post(url='https://swap.bkex.com/swapapi/wi/order/open',headers=headers_2,data=data).content.decode()
        ts1 = time.time()
        temp = {}
        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        temp['bkex'] = '开多'
        temp['延迟'] = ts1 - ts0
        temp['response'] = response
        t1 = threading.Thread(target=save_data, args=(temp, json_name))
        t1.start()
        return response

    elif user1 == '开空':
        data = '{"symbol":"btc_usdt","side":2,"type":2,"amount":"'+str(a)+'","leverage":100,"triggerType":1,"openType":1}:'  # amoun参数调整数量
        ts0 = time.time()
        response = requests.post(url='https://swap.bkex.com/swapapi/wi/order/open', headers=headers_2,data=data).content.decode()
        ts1 = time.time()
        temp = {}
        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        temp['bkex'] = '开空'
        temp['延迟'] = ts1 - ts0
        temp['response'] = response
        t1 = threading.Thread(target=save_data, args=(temp, json_name))
        t1.start()
        return response


# ping_cang_bkex
def ping_bkex():
    data = '{"symbol":"btc_usdt"}: '
    ts0 = time.time()
    response = requests.post(url='https://swap.bkex.com/swapapi/wi/order/closeAll',headers=headers_2,data=data).content.decode()
    ts1 = time.time()
    temp = {}
    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    temp['bkex'] = '平仓'
    temp['延迟'] = ts1 - ts0
    temp['response'] = response
    t1 = threading.Thread(target=save_data, args=(temp, json_name))
    t1.start()
    return response

if __name__ == '__main__':
    # print(main(0.01, '开多'))
    # print(main(0.01, '开空'))
    ts0 = time.time()
    # print(ping_bkex())
    ts1 = time.time()
    # print("延迟", ts1-ts0)
    # print(headers_2)
    pass