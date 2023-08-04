import base64
import hashlib
import hmac
import json
from datetime import datetime
from urllib import parse

import requests

# 签名
def create_signature(access_key, secret_key, path_param: dict, api_uri, http_method='get'):
    """
    :param secret_key: Secret Key
    :param access_key: Access Key
    :param path_param: 请求参数
    :param http_method: HTTP 请求方法  「get、post」
    :param api_uri: API 接口路径
    :return:
    """
    params_to_sign = {'AccessKeyId': access_key,
                      'SignatureMethod': 'HmacSHA256',
                      'SignatureVersion': '2',
                      'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                      }
    params_to_sign.update(path_param)
    host = "perpetual.hotcoinex.io"
    method = http_method.upper()
    temp_params = sorted(params_to_sign.items(), key=lambda d: d[0], reverse=False)
    temp_params = parse.urlencode(temp_params)
    payload = '\n'.join([method, host, api_uri, temp_params]).encode(encoding='UTF-8')
    #print(payload.decode(encoding="utf-8"))
    secret_key = secret_key.encode(encoding='UTF-8')
    signature = base64.b64encode(hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest())
    params_to_sign['Signature'] = signature
    #print(signature)
    return params_to_sign


# GET请求
def get(access_key, secret_key, host, uri, path_param):
    headers = {
        'Content-Type': 'application/json'
    }
    params = create_signature(access_key, secret_key, path_param, uri, 'get')
    response = requests.get(host + uri, params=params, headers=headers, timeout=10)
    return response.json()


# POST请求
def post(access_key, secret_key, host, uri, path_param, body):
    headers = {
        'Content-Type': 'application/json'
    }
    params = create_signature(access_key, secret_key, path_param, uri, 'post')
    data = json.dumps(body)
    response = requests.post(host + uri, params=params, data=data, headers=headers, timeout=10)
    return response.json()