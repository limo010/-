import base as bs
import threading
import time
from flask import Flask, request
if __name__ == '__main__':
    # 获取全局变量
    json_name1_ = 'bch_7704_多空趋势线日志.json'
    error_ = 'error_7704_日志.json'
    json_name2_ = 'set_7704.json'
    key_ = ''
    secret_ = ''
    precision = 1
    thread8 = threading.Thread(target=bs.get_base_data, args=(json_name1_, error_, json_name2_, key_, secret_, precision))
    thread8.start()
    # 接收价格
    symbol = "BCH"
    work = bs.Bn_data_wss(symbol)
    thread2 = threading.Thread(target=work.connection_open_api)
    thread2.start()
    time.sleep(3)
    # 接收K线开盘时间
    thread4 = threading.Thread(target=bs.get_K_data, args=("BCHUSDT", "2h"))
    thread4.start()
    time.sleep(3)
    # 盈利回实际亏损
    thread3 = threading.Thread(target=bs.win_stop_loss)
    thread3.start()
    # 止损平仓时计算出实际亏损或者是实际盈利
    thread5 = threading.Thread(target=bs.stop_loss, args=("BCH_USDT", work))
    thread5.start()
    time.sleep(3)
    # 仓位千4 止盈
    thread6 = threading.Thread(target=bs.take_profit, args=("BCH_USDT", work))
    thread6.start()
    # 判断是否波动5%
    thread7 = threading.Thread(target=bs.tiaojian0, args=('', work))
    thread7.start()
    time.sleep(3)
    bs.app.run(host='127.0.0.1', port=7702, debug=False)