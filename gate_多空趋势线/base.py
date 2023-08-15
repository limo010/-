# 7795_7796
import json
import websocket
import random
import ssl
from flask import Flask, request
import time
import threading
import requests
import logging
import urllib3
from json_create import save_data
from requirement_GN import orders, cangweichaxun
# 禁止websocket日志输出
log = logging.getLogger('websocket')
log.setLevel(logging.WARNING)
# 禁用urllib3库的日志警告输出
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# 设置日志级别为ERROR或更高级别
logging.getLogger('urllib3').setLevel(logging.ERROR)
json_name1 = ''
error = ''
json_name2 = ''
key = ""
secret = ""
K_time = ''
# 多空趋势转换标记
flag = ''
side = ''
reduceOnly = ''
# 计算盈利和亏损
stop_loss_ = 0
profit_ = 0
app = Flask(__name__)
###################### 全局变量
beishu = ''
# 计算累计亏损
acclate_losses = ''
# 计算累计盈利
acclate_profits = ''
# 标记多头首仓位置
price0 = 0
# 标记空头首仓位置
price1 = 0
# 多头首仓
shoucang0 = ''
# 空头首仓
shoucang1 = ''
# 多头是否开仓
open0 = ''
open1 = ''
# 精度
precision = ''
# 首仓数量
cangwei0 = ''
cangwei1 = ''
@app.route('/trade', methods=['POST'])
def trade():
    global flag
    global side
    global reduceOnly
    global beishu
    global acclate_losses
    global acclate_profits
    global stop_loss_
    global profit_
    global price0
    global price1
    global shoucang0, shoucang1
    global open0, open1
    global cangwei0, cangwei1
    try:
        data = json.loads(request.data)
        print(data)
        direction = data['action2']
        # 不同交易所开单方式不同
        quantity = round(float(data['contracts']), precision) * 2
        quantity_beishu = quantity
        # 不同交易所交易精度不同 & 不同交易所最低交易个数不同
        prev_market_position = data['prev_market_position']
        symbol = data['symbol']
        if symbol == 'CFX_USDT':
            quantity = int(quantity / 10)
        elif symbol == 'XRP_USDT':
            quantity = int(quantity / 10)
        elif symbol == 'DOGE_USDT':
            quantity = int(quantity / 10)
        elif symbol == 'BCH_USDT':
            quantity = int(quantity * 100)
        elif symbol == 'SOL_USDT':
            quantity = int(quantity)
        # 数量过大不开仓
        open = 1
        if 'Long' in direction:
            if cangwei0 != 0:
                if quantity / cangwei0 > 10:
                    print('多头仓位过大不开仓')
                    open = 0
        elif 'Short' in direction:
            if cangwei1 != 0:
                if quantity / cangwei1 > 10:
                    print('空头仓位过大不开仓')
                    open = 0
        # 判断接收到的仓位是否过大
        if open:
            # 首次接收到多单
            if flag != 1 and 'Long' in direction:
                # 标记首仓价格
                if shoucang0 == 0:
                    shoucang0 = 1
                    price0 = float(data['price'])
                    cangwei0 = float(quantity)
                flag = 1
                print("空头--》多头，一键平空仓", '此单盈利或亏损', stop_loss_)
                # 计算累计亏损和累计盈利
                acclate_losses = acclate_losses + stop_loss_
                acclate_profits = acclate_profits + profit_
                # 倍数 出现亏损
                if acclate_losses < 0:
                    beishu = round(acclate_losses / (4 / 1000 * float(data['price']) * quantity_beishu) / 3, 0)
                    if beishu < 0 and abs(beishu) > 1:
                        beishu = abs(beishu)
                    else:
                        beishu = 1
                else:
                    beishu = 1

                print("实际倍数", beishu)
                # 一键平空仓
                print(orders(1, 1, symbol, 'ioc', '0'))
                # 保存临时变量
                temp = {}
                temp['beishu'] = beishu
                temp['acclate_profits'] = acclate_profits
                temp['acclate_losses'] = acclate_losses
                temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                temp['price0'] = price0
                temp['price1'] = price1
                # 多头首仓
                temp['shoucang0'] = shoucang0
                # 空头首仓
                temp['shoucang1'] = shoucang1
                # 多头是否开仓
                temp['open0'] = open0
                temp['open1'] = open1
                temp['cangwei0'] = cangwei0
                temp['cangwei1'] = cangwei1
                t1 = threading.Thread(target=save_data, args=(temp, json_name2, 'w'))
                t1.start()
                # 将开平仓记录保存
                temp = {}
                temp['开仓价'] = data['price']
                temp['content'] = '空头--》多头，一键平空仓'
                temp['倍数'] = beishu
                temp['累计盈利'] = acclate_profits
                temp['累计亏损'] = acclate_losses
                temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
                t1.start()
                time.sleep(1)
                print('是否能开单', open0)
                # 再开多
                if open0:
                    side = "BUY"
                    print('开多', '数量', quantity)
                    quantity = quantity * beishu
                    reduceOnly = "false"
                    print(orders(quantity, 0, symbol, 'ioc', '0'))
            # 正常开多
            elif flag == 1 and 'Long' in direction and open0:
                # 标记首仓价格
                if shoucang0 == 0:
                    shoucang0 = 1
                    price0 = float(data['price'])
                    cangwei0 = float(quantity)
                side = "BUY"
                quantity = quantity * beishu
                print('开多', '数量', quantity)
                reduceOnly = "false"
                print(orders(quantity, 0, symbol, 'ioc', '0'))
                # 保存临时变量
                temp = {}
                temp['beishu'] = beishu
                temp['acclate_profits'] = acclate_profits
                temp['acclate_losses'] = acclate_losses
                temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                temp['price0'] = price0
                temp['price1'] = price1
                # 多头首仓
                temp['shoucang0'] = shoucang0
                # 空头首仓
                temp['shoucang1'] = shoucang1
                # 多头是否开仓
                temp['open0'] = open0
                temp['open1'] = open1
                temp['cangwei0'] = cangwei0
                temp['cangwei1'] = cangwei1
                t1 = threading.Thread(target=save_data, args=(temp, json_name2, 'w'))
                t1.start()
            # 正常平多
            elif flag == 1 and 'long' in prev_market_position and direction == 'TakeProfit':
                # 标记首仓
                shoucang0 = 0
                # 计算累计盈利
                acclate_losses = acclate_losses + stop_loss_
                acclate_profits = acclate_profits + profit_
                open0 = 1
                side = "SELL"
                print('平多', '数量', quantity)
                print(orders(-1, 1, symbol, 'ioc', '0'))
                # 保存临时变量
                temp = {}
                temp['beishu'] = beishu
                temp['acclate_profits'] = acclate_profits
                temp['acclate_losses'] = acclate_losses
                temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                temp['price0'] = price0
                temp['price1'] = price1
                # 多头首仓
                temp['shoucang0'] = shoucang0
                # 空头首仓
                temp['shoucang1'] = shoucang1
                # 多头是否开仓
                temp['open0'] = open0
                temp['open1'] = open1
                temp['cangwei0'] = cangwei0
                temp['cangwei1'] = cangwei1
                t1 = threading.Thread(target=save_data, args=(temp, json_name2, 'w'))
                t1.start()
            # 首次接收到空单
            elif flag != 0 and 'Short' in direction:
                # 标记首仓价格
                if shoucang1 == 0:
                    shoucang1 = 1
                    price1 = float(data['price'])
                    cangwei1 = float(quantity)
                flag = 0
                print("多头--》空头，一键平多仓", '此单盈利或亏损', stop_loss_)
                # 计算累计亏损和累计盈利
                acclate_losses = acclate_losses + stop_loss_
                acclate_profits = acclate_profits + profit_
                # 倍数 出现亏损
                if acclate_losses < 0:
                    beishu = round(acclate_losses / (4 / 1000 * float(data['price']) * quantity_beishu) / 3, 0)
                    if beishu < 0 and abs(beishu) > 1:
                        beishu = abs(beishu)
                    else:
                        beishu = 1
                else:
                    beishu = 1
                print("实际倍数", beishu)
                # 一键平多
                print(orders(-1, 1, symbol, 'ioc', '0'))
                # 保存临时变量
                temp = {}
                temp['beishu'] = beishu
                temp['acclate_profits'] = acclate_profits
                temp['acclate_losses'] = acclate_losses
                temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                temp['price0'] = price0
                temp['price1'] = price1
                # 多头首仓
                temp['shoucang0'] = shoucang0
                # 空头首仓
                temp['shoucang1'] = shoucang1
                # 多头是否开仓
                temp['open0'] = open0
                temp['open1'] = open1
                temp['cangwei0'] = cangwei0
                temp['cangwei1'] = cangwei1
                t1 = threading.Thread(target=save_data, args=(temp, json_name2, 'w'))
                t1.start()
                temp = {}
                temp['开仓价'] = data['price']
                temp['content'] = '多头--》空头，一键平多仓'
                temp['倍数'] = beishu
                temp['累计盈利'] = acclate_profits
                temp['累计亏损'] = acclate_losses
                temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
                t1.start()
                time.sleep(1)
                print('是否能开单', open1)
                # 再开空
                if open1:
                    quantity = quantity * beishu
                    side = "SELL"
                    print('开空', '数量', quantity)
                    reduceOnly = "false"
                    print(orders(-quantity, 0, symbol, 'ioc', '0'))
            # 正常开空
            elif flag == 0 and 'Short' in direction and open1:
                # 标记首仓价格
                if shoucang1 == 0:
                    shoucang1 = 1
                    price1 = float(data['price'])
                    cangwei1 = float(quantity)
                side = "SELL"
                quantity = quantity * beishu
                print('开空', '数量', quantity)
                reduceOnly = "false"
                print(orders(-quantity, 0, symbol, 'ioc', '0'))
                # 保存临时变量
                temp = {}
                temp['beishu'] = beishu
                temp['acclate_profits'] = acclate_profits
                temp['acclate_losses'] = acclate_losses
                temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                temp['price0'] = price0
                temp['price1'] = price1
                # 多头首仓
                temp['shoucang0'] = shoucang0
                # 空头首仓
                temp['shoucang1'] = shoucang1
                # 多头是否开仓
                temp['open0'] = open0
                temp['open1'] = open1
                temp['cangwei0'] = cangwei0
                temp['cangwei1'] = cangwei1
                t1 = threading.Thread(target=save_data, args=(temp, json_name2, 'w'))
                t1.start()
            # 正常平空
            elif flag == 0 and 'short' in prev_market_position and direction == "TakeProfit":
                shoucang1 = 0
                # 计算累计盈利
                acclate_losses = acclate_losses + stop_loss_
                acclate_profits = acclate_profits + profit_
                open1 = 1
                side = "BUY"
                print('平空', '数量', quantity)
                print(orders(1, 1, symbol, 'ioc', '0'))
                # 保存临时变量
                temp = {}
                temp['beishu'] = beishu
                temp['acclate_profits'] = acclate_profits
                temp['acclate_losses'] = acclate_losses
                temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                temp['price0'] = price0
                temp['price1'] = price1
                # 多头首仓
                temp['shoucang0'] = shoucang0
                # 空头首仓
                temp['shoucang1'] = shoucang1
                # 多头是否开仓
                temp['open0'] = open0
                temp['open1'] = open1
                temp['cangwei0'] = cangwei0
                temp['cangwei1'] = cangwei1
                t1 = threading.Thread(target=save_data, args=(temp, json_name2, 'w'))
                t1.start()

            if flag == 1 and open0 == 0:
                # 将开平仓记录保存
                temp = {}
                temp['content'] = "多头跌幅过大"
                temp['累计盈利'] = acclate_profits
                temp['累计亏损'] = acclate_losses
                temp['倍数'] = beishu
                temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
                t1.start()
            elif flag == 0 and open1 == 0:
                temp = {}
                temp['content'] = "空头跌幅过大"
                temp['累计盈利'] = acclate_profits
                temp['累计亏损'] = acclate_losses
                temp['倍数'] = beishu
                temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
                t1.start()
            else:
                # 将开平仓记录保存
                temp = {}
                temp['open'] = side
                temp['reduceOnly'] = reduceOnly
                temp['开仓价'] = data['price']
                temp['quantity'] = quantity
                temp['累计盈利'] = acclate_profits
                temp['累计亏损'] = acclate_losses
                temp['倍数'] = beishu
                temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
                t1.start()
        return "success"
    except Exception as error:
        temp = {}
        temp['error'] = error
        t1 = threading.Thread(target=save_data, args=(temp, error, 'a'))
        t1.start()
        print(f"开单存在错误: {error}")
        return "failure"

# 获取全局变量
def get_base_data(json_name1_, error_, json_name2_, key_, secret_, precision_):
    global json_name1, json_name2, error
    global key, secret
    global beishu
    global acclate_losses,acclate_profits
    global price0, price1
    global shoucang0, shoucang1
    global open0, open1
    global precision
    global cangwei0, cangwei1
    json_name1 = json_name1_
    error = error_
    json_name2 = json_name2_
    key = key_
    secret = secret_
    precision = precision_
    try:
        with open(json_name2, encoding="utf-8") as file_obj:
            data_temp = json.load(file_obj)
        file_obj.close()
    except Exception as e:
        print(e)
    print(data_temp)
    ###################### 保存至变量
    beishu = data_temp['beishu']
    # 计算累计亏损
    acclate_losses = data_temp['acclate_losses']
    # 计算累计盈利
    acclate_profits = data_temp['acclate_profits']
    # 标记多头首仓位置
    price0 = data_temp['price0']
    # 标记空头首仓位置
    price1 = data_temp['price1']
    # 多头首仓
    shoucang0 = data_temp['shoucang0']
    # 空头首仓
    shoucang1 = data_temp['shoucang1']
    # 多头是否开仓
    open0 = data_temp['open0']
    open1 = data_temp['open1']
    cangwei0 = data_temp['cangwei0']
    cangwei1 = data_temp['cangwei1']

# 判断是否波动5%
def tiaojian0(symbol, work):
    global price0
    global price1
    global open0
    global open1

    while 1:
        time.sleep(0.3)
        # 多头跌幅
        if price0 != 0:
            if (price0 - work.symbol_price_last) / price0 > 0.05:
                open0 = 0
            # else:
            #     open0 = 1
        # 空头涨幅
        if price1 != 0:
            if (work.symbol_price_last - price1) / price1 > 0.05:
                open1 = 0
            # else:
            #     open1 = 1


# 盈利回实际亏损倍数回归正常
def win_stop_loss():
    global acclate_profits
    global acclate_losses
    global beishu
    while 1:
        time.sleep(1)
        if acclate_losses > 0:
            # 将开平仓记录保存
            temp = {}
            temp['累计盈利'] = acclate_profits
            temp['累计亏损'] = acclate_losses
            temp['倍数'] = beishu
            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
            t1.start()
            acclate_profits = 0
            acclate_losses = 0
            beishu = 1
            # 保存临时变量
            temp = {}
            temp['beishu'] = beishu
            temp['acclate_profits'] = acclate_profits
            temp['acclate_losses'] = acclate_losses
            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            temp['price0'] = price0
            temp['price1'] = price1
            # 多头首仓
            temp['shoucang0'] = shoucang0
            # 空头首仓
            temp['shoucang1'] = shoucang1
            # 多头是否开仓
            temp['open0'] = open0
            temp['open1'] = open1
            temp['cangwei0'] = cangwei0
            temp['cangwei1'] = cangwei1
            t1 = threading.Thread(target=save_data, args=(temp, json_name2, 'w'))
            t1.start()


# 实时计算实际亏损或者是实际盈利
def stop_loss(symbol, work):
    global stop_loss_
    global profit_
    global flag
    # 获取仓位信息
    while 1:
        time.sleep(5)
        try:
            data = cangweichaxun(symbol)
            # print(data)
            for data_ in data:
                # 空多头方向
                if float(data_['size']) > 0:
                    flag = 1
                elif float(data_['size']) < 0:
                    flag = 0
                # 多头止损
                if flag == 1:
                    if float(data_['size']) > 0:
                        stop_loss_ = float(data_['unrealised_pnl'])
                        profit_ = float(data_['unrealised_pnl'])
                # 空头止损
                elif flag == 0:
                    if float(data_['size']) < 0:
                        stop_loss_ = float(data_['unrealised_pnl'])
                        profit_ = float(data_['unrealised_pnl'])
        except Exception as e:
            print('未开仓{}'.format(symbol), e)


# 仓位千4 止盈
def take_profit(symbol, work):
    global acclate_profits
    global acclate_losses
    # 获取仓位信息
    while 1:
        time.sleep(1)
        try:
            data = cangweichaxun(symbol)
            for data_ in data:
                # print(data_)
                # 计算利润
                if float(data_['entry_price']) != 0:
                    profit = (work.symbol_price_last - float(data_['entry_price'])) / float(data_['entry_price'])
                if float(data_['size']) > 0:
                    if price0 != 0:
                        print("多头千4利润", profit * abs(float(data_['size'])), '累计盈利', acclate_profits, '累计亏损', acclate_losses, '倍数', beishu, '此单盈亏', stop_loss_, '数量', float(data_['size']),'跌幅', (price0 - work.symbol_price_last) / price0)
                    else:
                        print("多头千4利润", profit * abs(float(data_['size'])), '累计盈利', acclate_profits, '累计亏损',acclate_losses, '倍数', beishu, '此单盈亏', stop_loss_, '数量', float(data_['size']))
                    if profit > 4 / 1000:
                        # 计算累计盈利
                        acclate_losses = acclate_losses + stop_loss_
                        acclate_profits = acclate_profits + profit_
                        print("多头总仓位大于千4利润，平仓")
                        # 一键平多仓
                        print(orders(-1, 1, symbol, 'ioc', '0'))
                        # 将开平仓记录保存
                        temp = {}
                        temp['profit'] = profit
                        temp['content'] = "多头总仓位大于千4利润，平仓"
                        temp['累计盈利'] = acclate_profits
                        temp['累计亏损'] = acclate_losses
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
                        t1.start()
                        # 保存临时变量
                        temp = {}
                        temp['beishu'] = beishu
                        temp['acclate_profits'] = acclate_profits
                        temp['acclate_losses'] = acclate_losses
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['price0'] = price0
                        temp['price1'] = price1
                        # 多头首仓
                        temp['shoucang0'] = shoucang0
                        # 空头首仓
                        temp['shoucang1'] = shoucang1
                        # 多头是否开仓
                        temp['open0'] = open0
                        temp['open1'] = open1
                        temp['cangwei0'] = cangwei0
                        temp['cangwei1'] = cangwei1
                        t1 = threading.Thread(target=save_data, args=(temp, json_name2, 'w'))
                        t1.start()
                elif float(data_['size']) < 0:
                    if price1 != 0:
                        print("空头千4利润", profit * abs(float(data_['size'])), '累计盈利', acclate_profits, '累计亏损', acclate_losses, '倍数', beishu, '此单盈亏', stop_loss_, '数量', float(data_['size']), '涨幅',(work.symbol_price_last - price1) / price1)
                    else:
                        print("空头千4利润", profit * abs(float(data_['size'])), '累计盈利', acclate_profits, '累计亏损', acclate_losses, '倍数', beishu, '此单盈亏', stop_loss_, '数量', float(data_['size']))
                    if profit < -4 / 1000:
                        # 计算累计盈利
                        acclate_losses = acclate_losses + stop_loss_
                        acclate_profits = acclate_profits + profit_
                        print("空头总仓位大于千4利润，平仓")
                        # 一键平空仓
                        print(orders(1, 1, symbol, 'ioc', '0'))
                        # 将开平仓记录保存
                        temp = {}
                        temp['content'] = "空头总仓位大于千4利润，平仓"
                        temp['profit'] = profit
                        temp['累计盈利'] = acclate_profits
                        temp['累计亏损'] = acclate_losses
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
                        t1.start()
                        # 保存临时变量
                        temp = {}
                        temp['beishu'] = beishu
                        temp['acclate_profits'] = acclate_profits
                        temp['acclate_losses'] = acclate_losses
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['price0'] = price0
                        temp['price1'] = price1
                        # 多头首仓
                        temp['shoucang0'] = shoucang0
                        # 空头首仓
                        temp['shoucang1'] = shoucang1
                        # 多头是否开仓
                        temp['open0'] = open0
                        temp['open1'] = open1
                        temp['cangwei0'] = cangwei0
                        temp['cangwei1'] = cangwei1
                        t1 = threading.Thread(target=save_data, args=(temp, json_name2, 'w'))
                        t1.start()
        except Exception as e:
            print('未开仓{}'.format(symbol), e)


# 接收K线的数据 并 5% 风控
def get_K_data(symbol, time0):
    global K_time
    global data_k
    global acclate_profits
    global acclate_losses
    proxies = {}
    # 现货的数据
    url = 'https://api.binance.com/api/v3/klines?symbol=%s&interval=%s&limit=1'%(symbol, time0)
    while 1:
        time.sleep(0.5)
        try:
            response = requests.get(url, proxies=proxies)
            data_k = response.json()
            if ((float(data_k[0][4]) - float(data_k[0][1])) / float(data_k[0][1]) < -0.05 and K_time != timeStamp(data_k[0][0])) or ((float(data_k[0][4]) - float(data_k[0][1])) / float(data_k[0][1]) > 0.05 and K_time != timeStamp(data_k[0][0])):
                K_time = timeStamp(data_k[0][0])
                print("全部平仓")
                # 计算盈亏
                acclate_losses = acclate_losses + stop_loss_
                acclate_profits = acclate_profits + profit_
                #######################################平仓
                # 一键平多仓
                print(orders(-1, 1, symbol, 'ioc', '0'))
                # 一键平空仓
                print(orders(1, 1, symbol, 'ioc', '0'))
                # 将开平仓记录保存
                temp = {}
                temp['累计盈利'] = acclate_profits
                temp['累计亏损'] = acclate_losses
                temp['content'] = '波动5%, 全部平仓'
                temp['bodong'] = (float(data_k[0][4]) - float(data_k[0][1])) / float(data_k[0][1])
                temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
                t1.start()
        except:
            continue


# 接收币种的最新价格
class Bn_data_wss(object):
    def __init__(self, symbol):
        # 内置变量的引用
        self.symbol_price_last = 0
        url = 'wss://fstream.binance.com'   # 现货  将f去掉
        self.Symbollist = [symbol]
        self.Steamlist = []
        for symbol in self.Symbollist:
            self.Steamlist.append(symbol.lower() + 'usdt@aggTrade')   # @aggTrade (最新成交价)  depth5@100ms（深度）
        if len(self.Steamlist) == 1:
            self.open_url = url + '/ws/' + self.Steamlist[0]
        else:
            parameters = '/stream?streams='
            for v in self.Steamlist:
                parameters += f"{v}/"
            parameters = parameters[:-1]
            self.open_url = url + parameters

    def on_open(self, ws):
        pass

    def on_message(self, ws, message):
        if message == 'ping':
            ws.send('pong')
        rsl = json.loads(message)
        if len(self.Steamlist) == 1:
            stream = self.Symbollist
            data = rsl
        else:
            if 'data' in rsl:
                stream = rsl['stream']
                data = rsl['data']
            else:
                print('非正常数据')
                return ws

        L1 = random.randint(1, 7500)
        if L1 == 100:
            print('币安合约价格推送正常运行中')
        price_zuixin = data['p']
        for symbol in self.Symbollist:
            if symbol.lower() in stream or symbol.upper() in stream:
                # print("最新价:"+str(price_zuixin))
                self.symbol_price_last = float(price_zuixin)
                break

    def on_error(self, ws, error):

        print(str(error))

    def on_close(self, ws, param='', param2=''):
        print("Binance Open Connection closed")
        self.connection_open_api()

    def connection_open_api(self):
        # websocket.enableTrace(True)
        # 调试日志是否开启
        ws = websocket.WebSocketApp(self.open_url,
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        try:
            ws.run_forever(ping_interval=30, sslopt={"cert_reqs": ssl.CERT_NONE})
        except:
            ws.close()
        return ws


# 输入毫秒级的时间，转出正常格式的时间
def timeStamp(timeNum):
    timeStamp = float(timeNum / 1000)
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # print (otherStyleTime)
    return otherStyleTime


if __name__ == '__main__':
    # BTC_USDT
    # 获取全局变量
    json_name1_ = 'bch_7702_多空趋势线日志.json'
    error_ = 'error_7702_日志.json'
    json_name2_ = 'set_7704.json'
    key_ = ''
    secret_ = ''
    precision = 0
    thread8 = threading.Thread(target=get_base_data, args=(json_name1_, error_, json_name2_, key_, secret_, precision))
    thread8.start()
    # 接收价格
    symbol = "BCH"
    work = Bn_data_wss(symbol)
    thread2 = threading.Thread(target=work.connection_open_api)
    thread2.start()
    time.sleep(5)
    # 接收K线开盘时间
    thread4 = threading.Thread(target=get_K_data, args=("BCHUSDT", "2h"))
    thread4.start()
    time.sleep(3)
    # 盈利回实际亏损
    thread3 = threading.Thread(target=win_stop_loss)
    thread3.start()
    # 止损平仓时计算出实际亏损或者是实际盈利
    thread5 = threading.Thread(target=stop_loss, args=("BCH_USDT", work))
    thread5.start()
    time.sleep(3)
    # 仓位千4 止盈
    thread6 = threading.Thread(target=take_profit, args=("BCH_USDT", work))
    thread6.start()
    # 判断是否波动5%
    thread7 = threading.Thread(target=tiaojian0, args=('', work))
    thread7.start()
    time.sleep(3)
    app.run(host='127.0.0.1', port=7702, debug=False)