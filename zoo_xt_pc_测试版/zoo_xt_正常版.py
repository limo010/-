import ssl
import websocket
import json
import time
import multiprocessing
import threading
from base_util_xt import open_order, close_all, get_xt_account, get_xt_profit
from json_create import save_data
from multiprocessing import Manager, Process, Queue
import os,signal
import zoo_create_reptile

json_name = "zoo_xt_BTC日志.json"

try:
    with open('volume.json', encoding="utf-8") as file_obj:
        volume_temp = json.load(file_obj)
    file_obj.close()
except Exception as e:
    print(e)



class Zoo_wss(object):

    def __init__(self, queue):
        self.queue = queue
        self.url = 'wss://stream.zoomex.com/usdt_public'

    def on_open(self, ws):
        # ws.send('{"op": "subscribe", "args": ["orderBookL2_25.BTCUSDT-Perp"]}')
        ws.send('{"op": "subscribe", "args": ["instrument_info.100ms.BTCUSDT-Perp"]}')
        pass

    def on_message(self, ws, message):
        rsl = json.loads(message)
        # print(rsl)
        try:
            # print(rsl)
            print(rsl['data']['update'][0]['last_price'])
            # print('卖一', rsl['data']['update'][0]['price'],'买一', rsl['data']['update'][1]['price'])
            self.queue.put([[float(rsl['data']['update'][0]['last_price']), float(rsl['data']['update'][0]['last_price'])], 0])
        except:
            pass
    def on_error(self, ws, error):
        print("报错")
        print(str(error))

    def on_close(self, ws, param='', param2=''):
        print('关闭')
        self.connection_open_api()

    def connection_open_api(self):
        # 调试日志是否开启
        ws = websocket.WebSocketApp(self.url,
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        try:
            ws.run_forever(ping_interval=30, sslopt={"cert_reqs": ssl.CERT_NONE})
            print("连接成功!!!")
        except:
            ws.close()
        return ws

class xt_wss(object):
    def __init__(self, queue):
        self.queue = queue
        self.url = 'wss://fstream.xt.com/ws/market?type=SYMBOL'   # 现货  将f去掉
        self.Symbollist = ['BTC']
        self.Steamlist = []
        self.allA =[]
        self.allB = []
        self.aPrice = 0
        self.bPrice = 0
        self.allSetA = set()
        self.allSetB = set()
    def on_open(self, ws):
        msg = '{"method":"subscribe","params":["ticker@btc_usdt","trade@btc_usdt","depth_update@btc_usdt","index_price@btc_usdt","mark_price@btc_usdt","fund_rate@btc_usdt"]}'
        ws.send(msg)
    def on_message(self, ws, message):
        if int(time.time()) % 10 == 0:
            ws.send('ping')
        try:
            rsl = json.loads(message)
            if rsl["topic"] == "depth_update":
                aparam = rsl["data"]["a"]
                bparam = rsl["data"]["b"]
                #tparam = rsl['data']['t']
                for a in aparam:
                    if float(a[0]) in self.allA:
                        if a[1] == '0':
                            del self.allA[self.allA.index(float(a[0]))]
                    else:
                        if a[1] != '0':
                            self.allA.append(float(a[0]))
                for b in bparam:
                    if float(b[0]) in self.allB:
                        if b[1] == '0':
                            del self.allB[self.allB.index(float(b[0]))]
                    else:
                        if b[1] != '0':
                            self.allB.append(float(b[0]))
                bparam = rsl["data"]["b"]
                self.aPrice,self.bPrice = sorted(self.allA)[0],sorted(self.allB)[-1]
                #print('卖一', self.aPrice, '买一', self.bPrice)
                self.queue.put([[float(self.aPrice), float(self.bPrice)], 1])
        except :
            pass

    def on_error(self, ws, error):

        print(str(error))

    def on_close(self, ws, param='', param2=''):
        print(" Open Connection closed")
        self.connection_open_api()

    def connection_open_api(self):
        ws = websocket.WebSocketApp(self.url,
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        try:
            ws.run_forever(ping_interval=30,sslopt={"cert_reqs": ssl.CERT_NONE})
        except:
            ws.close()
        return ws

class Work(object):

    def __init__(self, queue):
        self.queue = queue
        self.hc_price = 0
        self.hc_sell = 0
        self.hc_buy = 0
        self.xt_price = 0
        self.xt_sell = 0
        self.xt_buy = 0
        self.flag = 0
        self.profit = 15
        self.zoo_volume = zoo_create_reptile.qty
        self.xt_volume = volume_temp['xt_volume']

    def domian(self):
        tiaojian1 = 0
        tiaojian2 = 0
        time_end = 0

        work1 = Zoo_wss(self.queue)
        one = Process(target=work1.connection_open_api)

        work2 = xt_wss(self.queue)
        two = Process(target=work2.connection_open_api)

        one.start()
        two.start()

        pid = os.getpid()
        print(pid)
        # 风控1 统计本金是否充足
        # fengkong = Process(target=self.fengkong,args=(pid,))
        # fengkong.start()

        # 风控2 统计开单数，是否两个交易所持仓
        # fengkong1 = Process(target=self.fengkong1,args=(pid,))
        # fengkong1.start()

        hc_xt_buy_list = []
        hc_xt_sell_list = []
        LEN = 2000

        while True:
            data = self.queue.get()
            # print(data)

            # zoo的数据
            if data[1] == 0:
                self.hc_price = (data[0][0] + data[0][1]) / 2
                self.hc_sell = data[0][0]
                self.hc_buy = data[0][1]
            # xt的数据u
            else:
                self.xt_price = (data[0][0] + data[0][1]) / 2
                self.xt_sell = data[0][0]
                self.xt_buy = data[0][1]

            if len(hc_xt_buy_list) > LEN and len(hc_xt_sell_list) > LEN:
                del hc_xt_buy_list[0]
                del hc_xt_sell_list[0]

            if self.xt_price != 0 and self.hc_price != 0:
                hc_xt_buy_list.append(self.hc_buy - self.xt_sell)
                hc_xt_sell_list.append(self.hc_sell - self.xt_buy)
                hc_xt_buy_list_avg_price = sum(hc_xt_buy_list) / len(hc_xt_buy_list)
                hc_xt_sell_list_avg_price = sum(hc_xt_sell_list) / len(hc_xt_sell_list)
                print('zoo买一-xt卖一的平均值', hc_xt_buy_list_avg_price, 'zoo卖一-xt买一的平均值',hc_xt_sell_list_avg_price, len(hc_xt_buy_list), len(hc_xt_sell_list))
            if self.xt_price != 0 and self.hc_price != 0 and len(hc_xt_buy_list) > LEN:
                print('xt买一', self.xt_buy, 'xt卖一', self.xt_sell, 'zoo买一', self.hc_buy, 'zoo卖一', self.hc_sell, 'zoo买一-xt卖一-平均值',(self.hc_buy - self.xt_sell) - hc_xt_buy_list_avg_price, 'zoo卖一-xt买一-平均值',(self.hc_sell - self.xt_buy) - hc_xt_sell_list_avg_price)
            else:
                continue
            # 开仓
            if self.flag == 0:
                if time.time()-time_end > 10:
                    # hc开空  xt开多  条件1
                    if (self.hc_buy - self.xt_sell) - hc_xt_buy_list_avg_price > self.profit and abs(self.hc_buy-self.xt_sell) < 100:
                        time_start = time.time()
                        tiaojian1 = 1
                        self.flag = 1
                        # hc开空
                        t2 = threading.Thread(target=zoo_create_reptile.open_sell)
                        t2.start()
                        # xt开多
                        t2 = threading.Thread(target=open_order, args=('btc_usdt', self.xt_volume, 'BUY', 'LONG', 0))
                        t2.start()
                        temp = {}
                        temp['xt'] = '开多'
                        temp['zoo'] = '开空'
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['xt卖一'] = self.xt_sell
                        temp['zoo买一'] = self.hc_buy
                        temp['zoo买一-xt卖一-平均值'] = (self.hc_buy - self.xt_sell) - hc_xt_buy_list_avg_price
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                        pass
                    # hc开多  xt开空   条件2
                    elif (self.hc_sell - self.xt_buy) - hc_xt_sell_list_avg_price < -self.profit and self.flag == 0 and abs(self.hc_sell - self.xt_buy) < 100:
                        time_start = time.time()
                        tiaojian2 = 1
                        self.flag = 1
                        # hc开多
                        t2 = threading.Thread(target=zoo_create_reptile.open_buy)
                        t2.start()
                        # xt开空
                        t2 = threading.Thread(target=open_order, args=('btc_usdt', self.xt_volume, 'SELL', 'SHORT', 0))
                        t2.start()
                        temp = {}
                        temp['xt'] = '开空'
                        temp['zoo'] = '开多'
                        temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        temp['xt买一'] = self.xt_buy
                        temp['zoo卖一'] = self.hc_sell
                        temp['zoo卖一-xt买一-平均值'] = (self.hc_sell - self.xt_buy) - hc_xt_sell_list_avg_price
                        t1 = threading.Thread(target=save_data, args=(temp, json_name))
                        t1.start()
                        pass
            # 平仓
            else:
                # 条件1平仓  hc平空  xt平多
                if time.time() - time_start > 300:
                    if tiaojian1 == 1:
                        if (self.hc_sell - self.xt_buy) - hc_xt_sell_list_avg_price < -self.profit and abs(self.hc_sell - self.xt_buy) < 100:
                            time_end = time.time()
                            tiaojian1 = 0
                            self.flag = 0
                            # hc平空
                            t2 = threading.Thread(target=zoo_create_reptile.close_sell)
                            t2.start()
                            # xt平多
                            t2 = threading.Thread(target=close_all)
                            t2.start()
                            temp = {}
                            temp['zoo'] = '平空'
                            temp['xt'] = '平多'
                            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            temp['xt买一'] = self.xt_buy
                            temp['zoo卖一'] = self.hc_sell
                            temp['zoo卖一-xt买一-平均值'] = (self.hc_sell - self.xt_buy) - hc_xt_sell_list_avg_price
                            t1 = threading.Thread(target=save_data, args=(temp, json_name))
                            t1.start()
                    # 条件2平仓 hc平多  xt平空
                    if tiaojian2 == 1:
                        if (self.hc_buy - self.xt_sell) - hc_xt_buy_list_avg_price > self.profit and abs(self.hc_buy - self.xt_sell) < 100:
                            time_end = time.time()
                            tiaojian2 = 0
                            self.flag = 0
                            # hc平多
                            t2 = threading.Thread(target=zoo_create_reptile.close_buy)
                            t2.start()
                            # xt平空
                            t2 = threading.Thread(target=close_all)
                            t2.start()
                            temp = {}
                            temp['zoo'] = '平多'
                            temp['xt'] = '平空'
                            temp['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            temp['xt卖一'] = self.xt_sell
                            temp['zoo买一'] = self.hc_buy
                            temp['zoo买一-xt卖一-平均值'] = (self.hc_buy - self.xt_sell) - hc_xt_buy_list_avg_price
                            t1 = threading.Thread(target=save_data, args=(temp, json_name))
                            t1.start()
                    pass
    # def fengkong(self, pids):
    #     while 1:
    #         time.sleep(10)
    #         # 查询hc的账户余额
    #         try:
    #             if query_paks.account_inquiry(ACCESS_KEY, SECRET_KEY) < 55:
    #                 print("资金不足")
    #                 # xt 一键平仓
    #                 close_all()
    #                 # hc
    #                 query_paks.order_liquidation(ACCESS_KEY, SECRET_KEY, 'SHORT')
    #                 query_paks.order_liquidation(ACCESS_KEY, SECRET_KEY, 'LONG')
    #                 send_email('服务器214', '资金不足')
    #                 os.kill(pids, signal.SIGINT)
    #
    #             elif get_xt_account() < 55:
    #                 print("资金不足")
    #                 close_all()
    #                 query_paks.order_liquidation(ACCESS_KEY, SECRET_KEY, 'SHORT')
    #                 query_paks.order_liquidation(ACCESS_KEY, SECRET_KEY, 'LONG')
    #                 send_email('服务器214', '资金不足')
    #                 os.kill(pids, signal.SIGINT)
    #             else:
    #                 print("资金正常")
    #                 # os.kill(pids, signal.SIGINT)
    #         except:
    #             # send_email('服务器223', 'xt_cookie失效')
    #             # os.kill(pids, signal.SIGINT)
    #             pass
    # 风控1
    # def fengkong1(self, pids):
    #     # 风控2  1、检测开仓是否顺利 2、每日开仓数85单
    #     while 1:
    #         time.sleep(10)
    #         print("检测开单数、策略是否单边开正常运行中--->")
    #         data = []
    #         strtime = time.strftime('%Y:%m:%d:%H:%M:%S', time.localtime())
    #         temp = str(strtime).split(":")[3]
    #         try:
    #             with open('hc_xt_BTC_response日志.json', 'r', encoding="utf-8_sig") as f:
    #                 #   逐行读取文件内容
    #                 for line in f.readlines():
    #                     json_data = json.loads(line)
    #                     # 检测日志的开仓是否正常  不正常全部平仓 发送警报
    #                     if 'returnCode' in json_data['response'] or 'code' in json_data['response'] or 'id' in json_data['response']:
    #                         pass
    #                     # 平仓和发送警报
    #                     else:
    #                         print("检测到策略单边开！！！")
    #                         print(json_data['response'])
    #                         # xt 一键平仓
    #                         close_all()
    #                         # hc
    #                         query_paks.order_liquidation(ACCESS_KEY, SECRET_KEY, 'SHORT')
    #                         query_paks.order_liquidation(ACCESS_KEY, SECRET_KEY, 'LONG')
    #                         send_email('服务器214', '检测到策略单边开！！！')
    #                         os.kill(pids, signal.SIGINT)
    #                     # 统计每一天开仓数
    #                     data.append(json_data['time'])
    #             df = pd.DataFrame(data, columns=['time'])
    #             df['time'] = pd.to_datetime(df['time'])
    #             temp_time = time.strftime('%Y-%m-%d 08:00:00')
    #             if int(temp) > 8:
    #                 start_time = temp_time
    #             else:
    #                 start_time = '%Y-%m-' + str(int(temp_time.split(' ')[0].split('-')[-1]) - 1) + ' 08:00:00'
    #             end_time = '%Y-%m-' + str(int(start_time.split(' ')[0].split('-')[-1]) + 1) + ' 08:00:00'
    #             df_ = df[df['time'] > pd.to_datetime(time.strftime('%Y-%m-%d 08:00:00'))]
    #             df_1 = df_[df_['time'] < pd.to_datetime(time.strftime(end_time))]
    #             print('今日开单数', len(df_1) / 2, '合约持仓正常！！！')
    #             # 检测开仓数小于85单，达到85单直接平仓 关闭代码 发送警报
    #             if len(df_1) / 2 > 85:
    #                 send_email('服务器214', '开仓次数达到85！！！')
    #         except Exception as e:
    #             print(e)

    # 统计利润
    # def get_profit(self):
    #     # 每天下午4点 1点检测一次利润
    #     strtime = time.strftime('%Y:%m:%d:%H:%M:%S', time.localtime())
    #     temp = str(strtime).split(":")[3]
    #     flag = 1
    #     data = []
    #     while True:
    #         time.sleep(60)
    #         strtime = time.strftime('%Y:%m:%d:%H:%M:%S', time.localtime())
    #         print('统计利润正常运行中--->')
    #         try:
    #             if temp != str(strtime).split(":")[3]:
    #                 flag = 1
    #             elif temp == '16' or temp == '01' and flag == 1:
    #                 flag = 0
    #                 # 统计利润 并发送消息
    #                 response_hc = query_paks.profit(ACCESS_KEY, SECRET_KEY)
    #                 response_xt = get_xt_profit()
    #                 profit = float(response_hc['accountRights']) + float(response_xt['result'][0]['walletBalance'])
    #                 print('利润', profit)
    #                 # 今日开单数
    #                 with open('hc_xt_BTC_response日志.json', 'r', encoding="utf-8_sig") as f:
    #                     #   逐行读取文件内容
    #                     for line in f.readlines():
    #                         json_data = json.loads(line)
    #                         # 统计每一天开仓数
    #                         data.append(json_data['time'])
    #                 print(data)
    #                 df = pd.DataFrame(data, columns=['time'])
    #                 print(df)
    #                 df['time'] = pd.to_datetime(df['time'])
    #                 print(df['time'])
    #                 temp_time = time.strftime('%Y-%m-%d 08:00:00')
    #                 if int(temp) > 8:
    #                     start_time = temp_time
    #                 else:
    #                     start_time = '%Y-%m-' + str(int(temp_time.split(' ')[0].split('-')[-1]) - 1) + ' 08:00:00'
    #                 end_time = '%Y-%m-' + str(int(start_time.split(' ')[0].split('-')[-1]) + 1) + ' 08:00:00'
    #                 df_ = df[df['time'] > pd.to_datetime(time.strftime('%Y-%m-%d 08:00:00'))]
    #                 print(df_)
    #                 df_1 = df_[df_['time'] < pd.to_datetime(time.strftime(end_time))]
    #                 print(df_1)
    #                 print('今日开单数', len(df_1) / 2)
    #                 print('统计时间', strtime, '策略运行天数:',self.Caltime('2023-04-26', time.strftime('%Y-%m-%d', time.localtime())), '本金:', '200U', '利润',profit, '今日开单数', len(df_1) / 2)
    #                 temp = {}
    #                 temp['统计时间'] = strtime
    #                 temp['策略运行天数'] = str(self.Caltime('2023-04-26', time.strftime('%Y-%m-%d', time.localtime())))
    #                 temp['本金'] = '200U'
    #                 temp['利润'] = profit
    #                 temp['今日开单数'] = len(df_1) / 2
    #                 t0 = threading.Thread(target=save_data, args=(temp, '利润统计.json'))
    #                 t0.start()
    #                 send_email('服务器214利润', str(temp))
    #         except Exception as e:
    #             print(e)
    #             flag = 1

    # def Caltime(self, date1, date2):
    #     date1 = time.strptime(date1, "%Y-%m-%d")
    #     date2 = time.strptime(date2, "%Y-%m-%d")
    #     date1 = datetime.datetime(date1[0], date1[1], date1[2])
    #     date2 = datetime.datetime(date2[0], date2[1], date2[2])
    #     return date2 - date1

if __name__ == '__main__':
    multiprocessing.freeze_support()
    queue = Queue()
    work = Work(queue)
    three = Process(target=work.domian)
    # profit = Process(target=work.get_profit)
    # profit.start()
    three.start()
    three.join()
    # profit.join()