import requests
import json
import numpy as np
import time
from json_create import save_data
import threading
import random
import websocket
import ssl
import multiprocessing
from multiprocessing import Manager, Process, Queue
# export https_proxy=http://127.0.0.1:33210 http_proxy=http://127.0.0.1:33210 all_proxy=socks5://127.0.0.1:33211
# proxies = {
#     'http': 'http://127.0.0.1:33210',
#     'https': 'http://127.0.0.1:33210'
# }
json_name = "成交量策略4日志.json"

# 拿币安现货的数据
class Bn_data_wss(object):

    def __init__(self, queue, List, symbol):
        self.queue = queue
        self.List = List
        url = 'wss://stream.binance.com'   # 现货  将f去掉
        self.Symbollist = [symbol]
        self.Steamlist = []
        self.data_list = []
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
        # print(rsl)
        if len(self.data_list) > 20:
            del self.data_list[0]
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
        self.data_list.append(float(price_zuixin))
        self.List[1] = sum(self.data_list) / len(self.data_list)
        for symbol in self.Symbollist:
            if symbol.lower() in stream or symbol.upper() in stream:
                self.queue.put([[float(price_zuixin),0], 0])
                self.List[0] = float(price_zuixin)
                # print("最新价:", str(price_zuixin), '近20个价格的平均值', self.List[1])
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
            ws.run_forever(ping_interval=30)
        except:
            ws.close()
        return ws

class Work(object):

    def __init__(self,queue, List):
        self.queue = queue
        self.List = List
        pass

    # 输入毫秒级的时间，转出正常格式的时间
    def timeStamp(self, timeNum):
        timeStamp = float(timeNum/1000)
        timeArray = time.localtime(timeStamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        # print (otherStyleTime)
        return otherStyleTime

    def domain(self):
        proxies = {}
        url = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=10'
        flag = 0
        open_time = ""
        duocang = 0
        kongcang = 0
        strtime = time.strftime('%Y:%m:%d:%H:%M:%S', time.localtime())
        time_temp = str(strtime).split(":")[3]
        price_max = 0
        price_min = 0
        while 1:
            time.sleep(0.5)
            try:
                response = requests.get(url, proxies=proxies)
                data = response.json()
            except:
                continue
            # 除去异常点
            List_data_erorr = []
            for value in data:
                List_data_erorr.append(float(value[5]))
            # print(List_data_erorr)
            # 计算出均值
            mean = np.mean(List_data_erorr)
            # 计算出标准差
            std = np.std(List_data_erorr)

            print('原始数据:', '数据长度', len(data), '平均值', mean, '标准差', std)
            print()
            # 最新价
            price_last = self.List[0]
            if float(data[-1][4]) > float(data[-1][1]):
                print('开盘时间', self.timeStamp(data[-1][0]), '开盘价', data[-1][1], '收盘价', data[-1][4], '成交量', data[-1][5], '收盘时间', "最新价:", price_last, '近20个价格的平均值', self.List[1], self.timeStamp(data[-1][6]), '价格上涨')
            else:
                print('开盘时间', self.timeStamp(data[-1][0]), '开盘价', data[-1][1], '收盘价', data[-1][4], '成交量', data[-1][5], '收盘时间', "最新价:", price_last, '近20个价格的平均值', self.List[1], self.timeStamp(data[-1][6]), '价格下跌')
            print()
            threshold = 10  # 设定阈值为1.2倍标准差
            List_data_checked = [x for x in List_data_erorr if (x > mean - threshold * std)]
            List_data_checked = [x for x in List_data_checked if (x < mean + threshold * std)]
            # 预处理后的平均值
            mean_checked = np.mean(List_data_checked)
            # 预处理后的总成交量
            sum = np.sum(List_data_checked)
            print('成交量的取值范围', [mean - threshold * std, mean + threshold * std])
            print('预处理后:', '数据长度', len(List_data_checked), '总成交量', sum, '平均值', mean_checked)
            print()
            # 当前这个时间段的成交额大于50个K柱的成交额平均值
            if flag == 0 and open_time != str(self.timeStamp(data[-1][0])):
                if float(data[-1][5]) > mean_checked + 100:
                    # 开多 用近20个价格判断 最近的价格大于近20个价格的平均值开仓
                    if 2 * float(data[-1][9]) > float(data[-1][5]):
                        price_max = price_last
                        print('开多')
                        temp = {}
                        temp['open'] = '开多'
                        temp['开盘时间'] = str(self.timeStamp(data[-1][0]))
                        temp['开仓时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['最新价'] = str(price_last)
                        temp['方向成交量'] = 2 * float(data[-1][9]) - float(data[-1][5])
                        temp['成交量平均值'] = mean_checked
                        temp['价格平均值'] = self.List[1]
                        # 记录开盘时间
                        open_time = str(self.timeStamp(data[-1][0]))
                        flag = 1
                        duocang = 1
                    # 开空 用成交量判断方向
                    else:
                        price_min = price_last
                        print('开空')
                        temp = {}
                        temp['open'] = '开空'
                        temp['开盘时间'] = str(self.timeStamp(data[-1][0]))
                        temp['开仓时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['最新价'] = str(price_last)
                        temp['方向成交量'] = 2 * float(data[-1][9]) - float(data[-1][5])
                        temp['成交量平均值'] = mean_checked
                        temp['价格平均值'] = self.List[1]
                        # 记录开盘时间
                        open_time = str(self.timeStamp(data[-1][0]))
                        flag = 1
                        kongcang = 1
                    # 保存数据
                    t1 = threading.Thread(target=save_data, args=(temp, json_name))
                    t1.start()
            else:
                # 保存最高点和最低点
                if price_last > price_max:
                    price_max = price_last
                if price_min > price_last:
                    price_min = price_last
                # 回调5个价格平仓
                if price_max - price_last > 10:
                    # 平多
                    if duocang == 1:
                        print("平多")
                        duocang = 0
                        flag = 0
                        open_temp = "平多"
                        temp = {}
                        temp['open'] = open_temp
                        temp['开盘时间'] = str(self.timeStamp(data[-1][0]))
                        temp['平仓时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['最新价'] = price_last
                        temp['方向成交量'] = 2 * float(data[-1][9]) - float(data[-1][5])
                        temp['成交量平均值'] = mean_checked
                        temp['价格平均值'] = self.List[1]
                        temp['最高点'] = price_max
                        # 保存数据
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                if price_min - price_last < -10:
                    # 平空
                    if kongcang == 1:
                        print("平空")
                        kongcang = 0
                        flag = 0
                        open_temp = "平空"
                        temp = {}
                        temp['open'] = open_temp
                        temp['开盘时间'] = str(self.timeStamp(data[-1][0]))
                        temp['平仓时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['最新价'] = (price_last)
                        temp['方向成交量'] = 2 * float(data[-1][9]) - float(data[-1][5])
                        temp['成交量平均值'] = mean_checked
                        temp['价格平均值'] = self.List[1]
                        temp['最低点'] = price_min
                        # 保存数据
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()


            # 每一个小时要重启一下程序
            # strtime = time.strftime('%Y:%m:%d:%H:%M:%S', time.localtime())
            # if time_temp != str(strtime).split(":")[3]:
            #     print("新的一小时到来！")
            #     os.system("python my_strgy.py")



if __name__ == '__main__':
    multiprocessing.freeze_support()
    List = Manager().list()
    List.append(0)
    List.append(1)
    queue = Queue()

    work2 = Bn_data_wss(queue, List, "BTC")
    two = Process(target=work2.connection_open_api)

    work = Work(queue,List)
    one = Process(target=work.domain)
    one.start()
    two.start()
    one.join()
    two.join()
    pass


