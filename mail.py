#!/usr/bin/python
# -*- coding: UTF-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os
import pymysql
import random


def send_and_insert(i, msg):
	receivers = [s[i][0]+'@pku.edu.cn']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
	if randid[i][0] < 10:
		ID = str(random.randint(1000,9999)) + '0' + str(randid[i][0])
	else:
		ID = str(random.randint(1000,9999)) + str(randid[i][0])
	message = MIMEText(name[i][0]+'同学:\n'+'您好！\n欢迎参加地学知识竞赛！\n' +
					   '您此次比赛的ID是：' + ID + '\n' +
					   msg, 'plain', 'utf-8')
	message['From'] = os.environ.get('MAIL_USERNAME')
	message['To'] = s[i][0]+'pku.edu.cn'
	message['Subject'] = Header('地学知识竞赛通知', 'utf-8')
	try:
		cursor.execute('UPDATE students\
		SET password = "%s"\
		WHERE id = " %s"'\
		 % (ID, randid[i][0]))
		db.commit()
		print('插入成功' + str(randid[i][0]))
		try:
			smtpObj.sendmail(sender, receivers, message.as_string())
			print('发送成功' + str(randid[i][0]))
		except:
			print('发送错误' + str(randid[i][0]))
	except:
		db.rollback()
		print('插入错误' + str(randid[i][0]))


db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
cursor = db.cursor()
cursor.execute('SELECT studentid FROM students')
s = cursor.fetchall()
cursor.execute('SELECT id FROM students')
randid = cursor.fetchall()
cursor.execute('SELECT name FROM students')
name = cursor.fetchall()
# 第三方 SMTP 服务
mail_host = "smtp.pku.edu.cn"  # 设置服务器
mail_user = os.environ.get('MAIL_USERNAME')    # 用户名
mail_pass = os.environ.get('MAIL_PASSWORD')   # 口令

smtpObj = smtplib.SMTP()
smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
smtpObj.login(mail_user, mail_pass)
sender = os.environ.get('MAIL_USERNAME')

# 邮件正文
msg = '希望您能记住这个ID，若是您进入决赛，我们将会要求您出示这个ID来验证您的身份。'
for i in range(len(s)):
	send_and_insert(i, msg)
db.close()
