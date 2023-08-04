import time
import hashlib
import hmac
import requests
import json
from send_email import save_data
import threading

json_name = "gate_xt_response日志.json"
try:
    with open('set.json', encoding="utf-8") as file_obj:
        data_temp = json.load(file_obj)
    file_obj.close()
except Exception as e:
    print(e)
def gen_sign(method, url, query_string=None, payload_string=None):
    key = data_temp['key']        # api_key
    secret = data_temp['secret'] # api_secret

    t = time.time()
    m = hashlib.sha512()
    m.update((payload_string or "").encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
    sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}

def orders(size, close, symbol):
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    url = '/futures/usdt/orders'
    query_param = ''
    # 数量正数为开多，负数为开空，0为平仓;close = 1 平仓,
    auto_size = ""
    reduce_only = ""
    # 平仓
    if close == 1:
        if size < 0:
            auto_size = "close_long"
        else:
            auto_size = "close_short"
        size = 0
        close = False
        reduce_only = True
    # 减仓
    if close == 2:
        reduce_only = True
    body = {"contract":symbol,"size":size,"price":"0","tif":"ioc","close": close,"auto_size":auto_size,"reduce_only":reduce_only}
    body = json.dumps(body)
    # print(body)
    # `gen_sign` 的实现参考认证一章
    sign_headers = gen_sign('POST', prefix + url, query_param, body)
    headers.update(sign_headers)
    try:
        ts1 = time.time()
        r = requests.request('POST', host + prefix + url, headers=headers, data=body, timeout=10)
        ts2 = time.time()
        temp = {}
        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        # print(r.json())
        if size > 0:
            temp['gate'] = "开多"
        else:
            temp['gate'] = '开空'
        temp['延迟'] = ts2 - ts1
        temp['response'] = r.json()
        t1 = threading.Thread(target=save_data, args=(temp, json_name))
        t1.start()
    except Exception as e:
        print(e)


# 检查仓位代码
def cangweichaxun():
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    url = '/futures/usdt/positions'
    query_param = ''
    # `gen_sign` 的实现参考认证一章
    sign_headers = gen_sign('GET', prefix + url, query_param)
    headers.update(sign_headers)
    r = requests.request('GET', host + prefix + url, headers=headers, timeout=10)
    # print(r.json())
    return r.json()

def get_gate_acount():
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/futures/usdt/accounts'
    query_param = ''
    # `gen_sign` 的实现参考认证一章
    sign_headers = gen_sign('GET', prefix + url, query_param)
    headers.update(sign_headers)
    r = requests.request('GET', host + prefix + url, headers=headers)
    # print(r.json())
    return float(r.json()['available'])

def get_gate_hold():
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/futures/usdt/positions/BTC_USDT'
    query_param = ''
    # `gen_sign` 的实现参考认证一章
    sign_headers = gen_sign('GET', prefix + url, query_param)
    headers.update(sign_headers)
    r = requests.request('GET', host + prefix + url, headers=headers)
    # print(r.json())
    return (r.json()['size'])

if __name__ == '__main__':
    print(get_gate_hold())
    ts1 = time.time()
    # orders(1,1,'BTC_USDT')
    ts2 = time.time()
    print("延迟",ts2-ts1)
    pass
