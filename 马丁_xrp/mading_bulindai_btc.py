import json
from flask import Flask, request
import datetime
import threading
import random
import websocket
import ssl
import numpy as np
# GATE开单
from requirement_GN import *
from json_create import save_data

proxies = {
"http": "http://127.0.0.1:33210",
"https": "http://127.0.0.1:33210"
}
json_name = 'set_btc.json'
json_name1 = 'BTC日志.json'
symbol = "BTC_USDT"
# 程序每一次开启都要读取这个风险仓位###################################################
try:
    with open(json_name, encoding="utf-8") as file_obj:
        data_temp = json.load(file_obj)
    file_obj.close()
except Exception as e:
    print(e)
# 没开仓的风险仓位
risk_positions_ = data_temp["risk_positions_"]
# 风险仓位
risk_positions = data_temp["risk_positions"]
# 已处理的风险仓位
hangding_risk_positons = data_temp["hangding_risk_positons"]
# 首次开仓的价格和仓位
price1 = data_temp["price1"]
position1 = data_temp["position1"]
# 记录N倍仓位的风险时间
risk_time = data_temp["risk_time"]
# 记录每一次开仓的仓位
quantity = data_temp["quantity"]
# 记录每一次接收到的data
data = data_temp["data"]
# 记录减仓和加仓的K线时间
open_time = data_temp["open_time"]
# 记录action2
action2 = data_temp['action2']
# 记录tv是否正常开单
flag = data_temp['flag']
print(data_temp)

# K线的开盘时间
K_time = ""
diefu = 0
lower_band = 0
app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
def trade():
    global data
    global quantity
    global data_temp
    global flag
    try:
        data = json.loads(request.data)
        direction = data['action2']
        # 不同交易所开单方式不同
        quantity = int(round(float(data['contracts']), 4) * 10000)
        # 不同交易所交易精度不同 & 不同交易所最低交易个数不同
        prev_market_position = data['prev_market_position']
        side = "BUY"
        if 'Profit' in direction:
            if 'long' in prev_market_position:
                side = "SELL"
                print('平多', '数量btc', quantity, datetime.datetime.now())
            else:
                print('平空', '数量btc', quantity, datetime.datetime.now())
        else:
            if 'Short' in direction:
                side = "SELL"
                print('开空', '数量btc', quantity, datetime.datetime.now())
            else:
                print('开多', '数量btc', quantity, datetime.datetime.now())
        # 斜率小于45度不开仓
        if side == "BUY" and float(data['price']) > lower_band:
            # A开多
            t0 = threading.Thread(target=orders, args=(quantity, 0, symbol, 'ioc', '0'))
            t0.start()
            # 将开平仓记录保存
            temp = {}
            temp['open'] = side
            temp['开仓价'] = data['price']
            temp['quantity'] = quantity
            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            temp['下轨'] = lower_band
            t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
            t1.start()
            flag = 1
        elif side == "SELL":
            # A平多
            t0 = threading.Thread(target=orders, args=(-1, 1, symbol, 'ioc', '0'))
            t0.start()
            # 将开平仓记录保存
            temp = {}
            temp['open'] = side
            temp['平仓价'] = data['price']
            temp['quantity'] = quantity
            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            temp['下轨'] = lower_band
            t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
            t1.start()
            flag = 0
        else:
            flag = 0
            temp = {}
            temp['open'] = side
            temp['平仓价'] = data['price']
            temp['quantity'] = quantity
            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            temp['下轨'] = lower_band
            temp['事件'] = 'tv突破下轨，未开仓'
            t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
            t1.start()
        # 保存临时变量
        data_temp['data'] = data
        data_temp['flag'] = flag
        t1 = threading.Thread(target=save_data, args=(data_temp, json_name, 'w'))
        t1.start()
        return "success"
    except Exception as error:
        print(f"开单存在错误: {error}")
        return "failure"

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

# 接收K线的数据
data_k = []
def get_K_data(symbol, time0):
    global data_k
    global K_time
    # f是合约的数据  没有f是现货的数据
    url = 'https://fapi.binance.com/fapi/v1/klines?symbol=%s&interval=%s&limit=21' % (symbol, time0)
    while 1:
        time.sleep(1)
        try:
            response = requests.get(url, proxies=proxies)
            data_k = response.json()
            K_time = timeStamp(data_k[-1][0])
            print("K线开盘的时间", K_time)
        except:
            continue

# 计算布林带
def calculate_bollinger_bands(prices, window=21, width=2):
    # 计算中轨线（简单移动平均线）
    middle_band = np.convolve(prices, np.ones(window)/window, mode='valid')
    rolling_std = np.std(prices[window-21:] - middle_band, ddof=0)
    # 计算上轨线和下轨线
    upper_band = middle_band + width * rolling_std
    lower_band = middle_band - width * rolling_std
    return middle_band, upper_band, lower_band

# 检查风险
def check_risk(work):
    global risk_positions
    global hangding_risk_positons
    global price1
    global position1
    global risk_time
    global quantity
    global risk_positions_
    global action2
    global lower_band
    while 1:
        time.sleep(1)
        src = []
        time.sleep(1)
        if len(data_k) != 0:
            for data_ in data_k:
                src.append(float(data_[4]))
            src = src[::-1]
            prices = np.array(src)
            middle_band, upper_band, lower_band = calculate_bollinger_bands(prices, 21, 2)
            print("上轨线:", upper_band, '中轨线', middle_band, '下轨线', lower_band)
            try:
                # 针对首次开仓的情况
                if 'Buy #1' == str(data['action2']):
                    print("首次开仓")
                    risk_time = str(data['time'])
                    price1 = data['price']
                    position1 = round(float(data['contracts']), 0)
                    action2 = data['action2']
                    # 保存临时数据#############################################################################################
                    data_temp['price1'] = work.symbol_price_last
                    data_temp['position1'] = float(position1)
                    data_temp['risk_time'] = risk_time
                    data_temp['action2'] = action2
                    t1 = threading.Thread(target=save_data, args=(data_temp, json_name, 'w'))
                    t1.start()
                # 针对平仓之后的情况
                elif 'Profit' in str(data['action2']):
                    print("全部平仓")
                    price1 = 0
                    position1 = 0
                    risk_positions = []
                    risk_positions_ = []
                    risk_time = ''
                    hangding_risk_positons = []
                    quantity = 0
                    action2 = ""
                    data_temp['action2'] = action2
                    data_temp['price1'] = price1
                    data_temp['position1'] = position1
                    data_temp['risk_positions'] = risk_positions
                    data_temp['risk_time'] = risk_time
                    data_temp['hangding_risk_positons'] = hangding_risk_positons
                    data_temp['quantity'] = quantity
                    # 保存临时数据#############################################################################################
                    t1 = threading.Thread(target=save_data, args=(data_temp, json_name, 'w'))
                    t1.start()
                # 针对后面开仓的情况
                else:
                    # 次单开始循环执行警报 k > -1
                    # 如果tv正常开单，将之归为风险仓位，如果没有开单，则不理
                    if flag:
                        if (risk_time != str(data['time']) and price1 != 0) or (price1 != 0 and action2 != data['action2']):
                            # 保存危险仓位 后续以方便平仓
                            risk_positions.append([quantity, float(work.symbol_price_last)])
                            print("触发警戒线===================================================================================>")
                            print('首次开仓价格', price1, '首次开仓仓位', position1, '危险仓位', data['contracts'], '危险价格', data['price'], '危险仓位', risk_positions)
                            risk_time = str(data['time'])
                            action2 = data['action2']
                            # 保存临时数据#############################################################################################
                            data_temp['risk_positions'] = risk_positions
                            data_temp['risk_time'] = risk_time
                            data_temp['action2'] = action2
                            t1 = threading.Thread(target=save_data, args=(data_temp, json_name, 'w'))
                            t1.start()
                    else:
                        # 保存未开仓的数据
                        if (risk_time != str(data['time']) and price1 != 0) or (price1 != 0 and action2 != data['action2']):
                            # 保存危险仓位 后续以方便平仓
                            risk_positions_.append([quantity, float(work.symbol_price_last)])
                            print("触发警戒线===================================================================================>")
                            print('首次开仓价格', price1, '首次开仓仓位', position1, '危险仓位', data['contracts'], '危险价格', data['price'],'危险仓位', risk_positions)
                            risk_time = str(data['time'])
                            action2 = data['action2']
                            # 保存临时数据#############################################################################################
                            data_temp['risk_positions_'] = risk_positions_
                            data_temp['risk_time'] = risk_time
                            data_temp['action2'] = action2
                            t1 = threading.Thread(target=save_data, args=(data_temp, json_name, 'w'))
                            t1.start()
            except Exception as e:
                print("检测风险出现问题", e)
                pass

# 处理风险
def handling_risk(work):
    global hangding_risk_positons
    global risk_position
    global risk_positions_
    global price1
    global position1
    global risk_time
    global open_time
    global k
    global K_time
    global action2
    no_open_time = ""
    while 1:
        try:
            time.sleep(1)
            # 如果风险仓位不为 0
            if len(risk_positions) != 0 and work.symbol_price_last != 0:
                print("触发警戒线===================================================================================>")
                print('首次开仓价格', price1, '首次开仓仓位', position1, '最新价', work.symbol_price_last, '未处理的风险仓位', risk_positions, '已处理的风险仓位', hangding_risk_positons, '待补仓的仓位', risk_positions_, 'K线开盘的时间', K_time)
                # 1、N倍以上的单个仓位 利润大于30%-40%平仓
                for risk_position in risk_positions:
                    profit_ = (work.symbol_price_last - risk_position[1]) / risk_position[1]
                    if profit_ > 6/1000:
                        print('利润大于30%，平仓')
                        # 记录减仓时间 ###################################################################
                        open_time = K_time
                        # 减仓######################################################################
                        t0 = threading.Thread(target=orders, args=(-risk_position[0], 2, symbol, 'ioc', '0'))
                        t0.start()
                        # 删掉一个风险仓位
                        risk_positions.remove(risk_position)
                        # 增加一个已处理的风险仓位
                        hangding_risk_positons.append([risk_position[0], work.symbol_price_last])
                        # 保存临时数据#############################################################################################
                        data_temp["open_time"] = open_time
                        data_temp["risk_positions"] = risk_positions
                        data_temp["hangding_risk_positons"] = hangding_risk_positons
                        t1 = threading.Thread(target=save_data, args=(data_temp, json_name, 'w'))
                        t1.start()
                        # 保存开仓记录###############################################################
                        temp = {}
                        temp['open'] = "减仓"
                        temp['减仓价'] = work.symbol_price_last
                        temp['quantity'] = risk_position[0]
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['跌幅'] = diefu
                        temp['content'] = '利润大于30%，平仓'
                        t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
                        t1.start()
            # 2、平仓之后，若未来的K线低于上一个平仓的价格，两个价格之间大于千3，则收盘价开仓，数量与上一单的仓位相同，并记录持仓的开仓价格，和仓位
            if len(hangding_risk_positons) != 0:
                print("触发警戒线===================================================================================>")
                print('首次开仓价格', price1, '首次开仓仓位', position1, '最新价', work.symbol_price_last, '未处理的风险仓位', risk_positions, '已处理的风险仓位', hangding_risk_positons, '待补仓的仓位', risk_positions_, 'K线开盘的时间', K_time)
                for hangding_risk_positon in hangding_risk_positons:
                    # 减仓后的K线
                    if K_time != open_time:
                        # 两个价格大于千3
                        # print((hangding_risk_positon[1] - work.symbol_price_last) / work.symbol_price_last)
                        if (hangding_risk_positon[1] - work.symbol_price_last) / work.symbol_price_last > 6 / 1000:
                            print('减仓之后下一个K线持续下跌')
                            # 加仓###############################################################
                            t0 = threading.Thread(target=orders, args=(hangding_risk_positon[0], 0, symbol, 'ioc', '0'))
                            t0.start()
                            # 删掉一个已处理的风险仓位
                            hangding_risk_positons.remove(hangding_risk_positon)
                            # 增加一个风险仓位
                            risk_positions.append([hangding_risk_positon[0], work.symbol_price_last])
                            # 保存临时数据#############################################################################################
                            data_temp["hangding_risk_positons"] = hangding_risk_positons
                            data_temp["risk_positions"] = risk_positions
                            t1 = threading.Thread(target=save_data, args=(data_temp, json_name, 'w'))
                            t1.start()
                            # 保存开仓记录###############################################################
                            temp = {}
                            temp['open'] = "加仓"
                            temp['加仓价'] = work.symbol_price_last
                            temp['quantity'] = hangding_risk_positon[0]
                            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            temp['die'] = diefu
                            temp['content'] = '减仓之后下一个K线持续下跌,加仓'
                            t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
                            t1.start()
            # 当收盘价回到下轨 直接补仓
            if len(risk_positions_) != 0:
                if no_open_time != K_time:
                    no_open_time = K_time
                    if work.symbol_price_last > lower_band:
                        for risk_position_ in risk_positions_:
                            #  补仓##############################################################################
                            t0 = threading.Thread(target=orders, args=(risk_position_[0], 0, symbol, 'ioc', '0'))
                            t0.start()
                            # 增加一个风险仓位
                            risk_positions.append([risk_position_[0], work.symbol_price_last])
                            # 删除一个未补仓的风险仓位
                            risk_positions_.remove(risk_position_)
                            # 保存开仓记录###############################################################
                            temp = {}
                            temp['open'] = "补仓"
                            temp['补仓价'] = work.symbol_price_last
                            temp['quantity'] = risk_position_[0]
                            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            temp['下轨'] = lower_band
                            t1 = threading.Thread(target=save_data, args=(temp, json_name1, 'a'))
                            t1.start()
                        # 保存临时数据#############################################################################################
                        data_temp["risk_positions"] = risk_positions
                        data_temp["risk_positions_"] = risk_positions_
                        t1 = threading.Thread(target=save_data, args=(data_temp, json_name, 'w'))
                        t1.start()
            if len(risk_positions) == 0 and len(hangding_risk_positons) == 0:
                print("当前没有风险!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print('首次开仓价格', price1, '首次开仓仓位', position1, '最新价', work.symbol_price_last, '未处理的风险仓位', risk_positions, '已处理的风险仓位', hangding_risk_positons, 'K线开盘的时间', K_time, '跌幅', diefu, '待补仓的仓位', risk_positions_)
        except Exception as e:
            print("处理风险出现问题", e)

# 输入毫秒级的时间，转出正常格式的时间
def timeStamp(timeNum):
    timeStamp = float(timeNum / 1000)
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime

if __name__ == '__main__':
    # 接收K线数据
    work_one = threading.Thread(target=get_K_data,args=('BTCUSDT', '15m'))
    # 接收最新价格
    work2 = Bn_data_wss("BTC")
    work2_one = threading.Thread(target=work2.connection_open_api)
    # 检查风险
    work3 = threading.Thread(target=check_risk, args=(work2, ))
    # 处理风险
    work4 = threading.Thread(target=handling_risk, args=(work2, ))
    work_one.start()
    work2_one.start()
    work3.start()
    work4.start()
    # work_one.join()
    # work_two.join()
    # work2_one.join()
    app.run(host='127.0.0.1', port=7791, debug=False)
