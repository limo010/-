#coding=utf-8

# 现价开仓平仓 一键平仓  持仓查询
import requests
import time
import json
import threading
from send_email import save_data
json_name = "gate_xt_response日志.json"
try:
    with open('xt_cookie.json', encoding="utf-8") as file_obj:
        data_temp = json.load(file_obj)
    file_obj.close()
except Exception as e:
    print(e)
headers = {
    #':authority': 'www.xt.com',
    #':path': '/fapi/market/v1/public/q/depth?symbol=btc_usdt&level=500',
    'accept': 'application/json,text/plain,*/*',
    'accept-encoding': 'gzip,deflate,br',
    'authorization': data_temp['authorization'],
    # 'cookie': 'clientCode=1679463782440Wg2BOaxaVPKuxEnXpbA; _ga=GA1.1.620576045.1679463783; lang=hk; sajssdk_2015_cross_new_user=1; _scid=9b70f256-3cc8-492d-a184-dd8d4154c36d; countryId=1; _sctr=1|1679414400000; gt_captcha_v4_user=2c5d640c39d249278895abd3620eaf7b; sensorsdata2015jssdkcross={"distinct_id":"3261209379610","first_id":"18707d84e9815e-0f240795ceb24-26021051-1742820-18707d84e99df","identities":"eyIkaWRlbnRpdHlfbG9naW5faWQiOiIzMjYxMjA5Mzc5NjEwIiwiJGlkZW50aXR5X2Nvb2tpZV9pZCI6IjE4NzA3ZDg0ZTk4MTVlLTBmMjQwNzk1Y2ViMjQtMjYwMjEwNTEtMTc0MjgyMC0xODcwN2Q4NGU5OWRmIn0=","history_login_id":{"name":"$identity_login_id","value":"3261209379610"},"$device_id":"18707d84e9815e-0f240795ceb24-26021051-1742820-18707d84e99df"}; token=eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJkdWlzdW9oYW8xQG91dGxvb2suY29tIiwiaXNzIjoieHQuY29tIiwidXNlck5hbWUiOiJkdWlzdW9oYW8xQG91dGxvb2suY29tIiwidXNlcklkIjozMjYxMjA5Mzc5NjEwLCJ1c2VyQ29kZSI6ImMwMTFjM2QwNTE0M2YyYjI1MjEzNmQ5ODZmN2I2ZmU2IiwiYWNjb3VudElkIjoiMzI2MTIwOTM3OTYxMCIsInNjb3BlIjoiYXV0aCIsInRlbmFudElkIjoxLCJsYXN0QXV0aFRpbWUiOjE2Nzk0NjQxMDYzMjUsInNpZ25UeXBlIjoiVVAiLCJleHAiOjE2ODIwNTYxMDYsImRldmljZSI6IndlYiJ9.X9y9EOfm2zlsn4YGPXoY19F8h8N4PrzQjJ7cghhi-IRfckidvxxieSQNRCDds-9C_kqxIQ8TnQB1X28AbLYaAcekYtIQvSvDnohmUBFRbudcFCoP_bCrOreVD2JxCBGJrcL2m9_9pWAk73fFwAHOkS8Xul62Z-2XBRI2tmG1jjw; theme=light; currency=usd; _ga_CY0DPVC3GS=GS1.1.1679463783.1.1.1679466597.0.0.0; _ga_MK8XKWK7DV=GS1.1.1679463784.1.1.1679466597.0.0.0; JSESSIONID=DDC32033FF573B572F4EB78CF914E773; __cf_bm=gLYey7XBz7SLQSOzRitGrJNuHYWGqQ4h.ZSqjMyyoQQ-1679467396-0-AUnogN7kbt8dfIf4N7OaVgB/aVopMyof5JLy/DEd2OqnXes1wk5+YU+MwLrAKr5W0nVG80tWyX/TMlaYa9My1Ms=',
    # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',

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
def get_depth():
    url = "https://www.xt.com/fapi/market/v1/public/q/depth?symbol=btc_usdt&level=500"
    data = {
        "time": int(time.time() * 100),


        "reduceOnly": False,
        "postOnly": False,
        "timeInForce": "IOC"
    }
    response = requests.get(url=url, headers=headers)  # .content.decode()

    result = response.text
    rsl = json.loads(result)
    allSetA = []
    allSetB = []
    for item in rsl["result"]["b"]:
        allSetB.append(float(item[0]))
    for item in rsl["result"]["a"]:
        allSetA.append(float(item[0]))
    allSetA.sort()
    allSetB.sort()
    print(allSetA[0])
    print(allSetB[-1])
    return response, data

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
    return float(response.json()['result'][0]['totalAmount'])


if __name__ == '__main__':
    ts0 = time.time()
    print(get_xt_account())
    # open_order('btc_usdt',1,'BUY','LONG',0) # 限价开多0.0005
    # ts1 = time.time()
    # open_order('btc_usdt', 5, 'SELL', 'SHORT',27110)  # 限价开空0.0005
    # ts1 = time.time()
    # print("延迟", ts1-ts0)
    # close_all() # 一键平仓
    ts1 = time.time()
    print("延迟", ts1-ts0)
    # open_order('btc_usdt', 5, 'BUY', 'SHORT', 25070)#买入平空
    # open_order('btc_usdt', 5, 'SELL', 'LONG', 30000)  # 卖出平多
    # 持仓
    # while 1:
    #     time.sleep(0.1)
    #     get_hold()
    # print(headers)
    pass
