import base_util_hc
import time
from json_create import save_data
import threading
json_name = "hc_xt_BTC_response日志.json"
# hotcoin api-key
ACCESS_KEY = ""
SECRET_KEY = ""
# 账户余额查询
def account_inquiry(ACCESS_KEY, SECRET_KEY):
    HOST = "https://api-ct.hotcoin.fit"
    params = {
    }
    contract_code = 'btcusdt'
    uri = f'/api/v1/perpetual/account/assets/{contract_code}'
    response = base_util_hc.get(ACCESS_KEY, SECRET_KEY, HOST, uri, params)
    #print('账户权益: ' + response['accountRights'])
    #print('当前币种: ' + response['currencyCodeDisplayName'])
    return response['availableMargin']
# 一键平仓
def order_liquidation(ACCESS_KEY, SECRET_KEY, direction):
    HOST = "https://api-ct.hotcoin.fit"
    params = {
    }
    body = {
    }
    contract_code = 'btcusdt'
    ts0 = time.time()
    if direction == "LONG":
        uri_long = f'/api/v1/perpetual/products/{contract_code}/long/closePosition' # 平所有多仓
        response = base_util_hc.post(ACCESS_KEY, SECRET_KEY, HOST, uri_long, params, body)
    else:
        uri_short = f'/api/v1/perpetual/products/{contract_code}/short/closePosition' # 平所有空仓
        response = base_util_hc.post(ACCESS_KEY, SECRET_KEY, HOST, uri_short, params, body)
    ts1 = time.time()
    temp = {}
    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    temp['hc'] = '平仓'
    temp['延迟'] = ts1-ts0
    temp['response'] = response
    t1 = threading.Thread(target=save_data, args=(temp, json_name))
    t1.start()
    print(response)
    print("一键平仓延迟", ts1-ts0)
# 订单处理器
def order_processor(ACCESS_KEY, SECRET_KEY, type, side, amount):
    HOST = "https://api-ct.hotcoin.fit"
    params = {
    }
    dict_data = {
        'type': type,  # 10 限价或条件单 11 市价
        'side': side,  # open_long 开多 open_short 开空 close_long 平多 close_short 平空
        'price': "",
        'amount': amount,
        'beMaker': "0",
        'tag': "1",
    }
    contract_code = 'btcusdt'
    uri = f'/api/v1/perpetual/products/{contract_code}/order'
    ts0 = time.time()
    response = base_util_hc.post(ACCESS_KEY, SECRET_KEY, HOST, uri, params, dict_data)
    ts1 = time.time()
    temp = {}
    temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    if side == "open_long":
        temp['hc'] = '开多'
    else:
        temp['hc'] = '开空'
    temp['延迟'] = ts1-ts0
    temp['response'] = response
    t1 = threading.Thread(target=save_data, args=(temp, json_name))
    t1.start()
    print("hc_orderId: " + str(response['id']))

if __name__ == '__main__':
    order_liquidation(ACCESS_KEY, SECRET_KEY,'SHORT')