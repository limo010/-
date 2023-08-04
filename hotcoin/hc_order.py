import base64
import hashlib
import hmac
import urllib
import urllib.parse
import urllib.request
import requests

from datetime import datetime

def order_processor(type, side, amount):
    ACCESS_KEY = ""
    SECRET_KEY = ""
    API_HOST = 'api-ct.hotcoin.fit'
    API_RUL = 'https://' + API_HOST
    def paramsSign(params, paramsPrefix, accessSecret):
        host = "api.hotcoin.top"
        method = paramsPrefix['method'].upper()
        uri = paramsPrefix['uri']
        tempParams = urllib.parse.urlencode(sorted(params.items(), key=lambda d: d[0], reverse=False))
        payload = '\n'.join([method, host, uri, tempParams]).encode(encoding='UTF-8')
        accessSecret = accessSecret.encode(encoding='UTF-8')
        return base64.b64encode(hmac.new(accessSecret, payload, digestmod=hashlib.sha256).digest())

    def http_post_request(url, params, data, timeout=10):
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url=url, params=params, headers=headers, data=data, timeout=timeout)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json()

    def get_utc_str():
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    def api_key_post(params, data, API_URI, timeout=10):
        method = 'POST'

        params_to_sign = {'AccessKeyId': ACCESS_KEY,
                          'SignatureMethod': 'HmacSHA256',
                          'SignatureVersion': '2',
                          'Timestamp': get_utc_str()}
        host_name = urllib.parse.urlparse(API_RUL).hostname
        host_name = host_name.lower()
        paramsPrefix = {"host": host_name, 'method': method, 'uri': API_URI}
        params_to_sign.update(params)
        params_to_sign['Signature'] = paramsSign(params_to_sign, paramsPrefix, SECRET_KEY).decode(encoding='UTF-8')
        url = 'https://api-ct.hotcoin.fit' + API_URI
        print(url)
        return http_post_request(url, params_to_sign, data, timeout)

    def order_send(datasend, contractCode, timeout=10):
        params = {
        }
        data = datasend
        API_RUI = '/api/v1/perpetual/products/' + contractCode + 'order'
        return api_key_post(params, data, API_RUI, timeout)

    dict_data = {
        'type': type,  # 10 限价或条件单 11 市价
        'side': side,  # open_long 开多 open_short 开空 close_long 平多 close_short 平空
        'price': "",
        'amount': amount,
        'beMaker': "0",
        'tag': "1",
    }

    datasend = str(dict_data)
    contractCode = "btcusdt/"
    res_data = order_send(datasend, contractCode, timeout=10)
    print("hc_orderId: " + str(res_data['id']))

# order_processor('11', 'open_long', 1)

