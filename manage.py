from flask import Flask
from flask import request
import pymysql
import os
import json
import random
import requests


app = Flask(__name__)


@app.route('/')
def index():
    s1 = '<h1>欢迎！</h1>'
    s2 = '<a href="http://www.miitbeian.gov.cn">京ICP备18040938号</a>'
    return s1 + s2


@app.route('/openid', methods=['POST'])
def openid():
	db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
	cursor = db.cursor()
	data = request.json
	redata = {}
	redata['openID'] = ''
	url = 'https://api.weixin.qq.com/sns/jscode2session?' + \
	'appid=wxb1240864091b21d6&' + \
	'secret=da85186c1ca4474c7f95ea15bb21b4b7&' + \
	'js_code=' + data['code'] + \
	'&grant_type=authorization_code'
	r = requests.get(url)
	s1 = r.text
	s2 = s1.split('"')
	redata['openID'] = s2[7]
	db.close()
	return json.dumps(redata, ensure_ascii=False)


@app.route('/getfreq', methods=['POST'])
def getfreq():
	db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
	cursor = db.cursor()
	data = request.json
	redata = {}
	redata['freq'] = 0
	if cursor.execute("SELECT freq FROM students WHERE openid = '%s'" % (data['openID'])) != 0:
		freq = cursor.fetchall()
		redata['freq'] = freq[0][0]
	elif cursor.execute("SELECT freq FROM others WHERE openid = '%s'" % (data['openID'])) != 0:
		freq = cursor.fetchall()
		redata['freq'] = freq[0][0]
	db.close()
	return json.dumps(redata, ensure_ascii=False)


@app.route('/setfreq', methods=['POST'])
def setfreq():
	db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
	cursor = db.cursor()
	data = request.json
	redata = {}
	redata['freq'] = 0
	if cursor.execute("SELECT freq FROM students WHERE openid = '%s'" % (data['openID'])) != 0:
		freq = cursor.fetchall()
		redata['freq'] = freq[0][0]
		cursor.execute("UPDATE students \
						SET freq = '%d' \
						WHERE openid = '%s'" % (redata['freq'] + 1, data['openID']))
		db.commit()
	elif cursor.execute("SELECT freq FROM others WHERE openid = '%s'" % (data['openID'])) != 0:
		freq = cursor.fetchall()
		redata['freq'] = freq[0][0]
		cursor.execute("UPDATE others \
						SET freq = '%d' \
						WHERE openid = '%s'" % (redata['freq'] + 1, data['openID']))
		db.commit()
	db.close()
	return json.dumps(redata, ensure_ascii=False)


@app.route('/home', methods=['POST'])
def home():
	db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
	cursor = db.cursor()
	data = request.json
	wxinfo = data['userInfo']
	redata = {}
	redata['rank'] = [0, 0]
	redata['loged'] = False
	flag = 2
	if cursor.execute("SELECT mark FROM students WHERE openid = '%s'" % (data['openID'])) != 0:
		flag = 0
		mark = cursor.fetchall()
		redata['num'] = mark[0][0]  # 更新分数
		redata['loged'] = True  # 登录成功
		# 更新昵称、头像
		cursor.execute("UPDATE students\
					SET nickName = '%s',\
					avatarUrl = '%s'\
					WHERE openid = '%s'"\
					% (wxinfo['nickName'], wxinfo['avatarUrl'], data['openID']))
		try:
			db.commit()
		except:
			db.rollback()
			print('更新昵称、头像错误')
	elif cursor.execute("SELECT mark FROM others WHERE openid = '%s'" % (data['openID'])) != 0:
		flag = 1
		mark = cursor.fetchall()
		redata['num'] = mark[0][0]
		redata['loged'] = True
		cursor.execute("UPDATE others\
					SET nickName = '%s',\
					avatarUrl = '%s'\
					WHERE openid = '%s'"\
					% (wxinfo['nickName'], wxinfo['avatarUrl'], data['openID']))
		try:
			db.commit()
		except:
			db.rollback()
			print('更新昵称、头像错误')
	else:
		redata['num'] = 0
	#更新人数
	if flag == 0:
		sql4 = "SELECT COUNT(*) as srank FROM students\
				WHERE mark > '%d'" % (mark[0][0])
		cursor.execute(sql4)
		srank = cursor.fetchall()
		redata['rank'][1] = srank[0][0] + 1
		sql5 = "SELECT COUNT(*) as orank FROM others\
				WHERE mark > '%d'" % (mark[0][0])
		cursor.execute(sql5)
		orank = cursor.fetchall()
		redata['rank'][0] = srank[0][0] + orank[0][0] + 1
	elif flag == 1:
		sql4 = "SELECT COUNT(*) as srank FROM students\
				WHERE mark > '%d'" % (mark[0][0])
		cursor.execute(sql4)
		srank = cursor.fetchall()
		redata['rank'][1] = 0
		sql5 = "SELECT COUNT(*) as orank FROM others\
				WHERE mark > '%d'" % (mark[0][0])
		cursor.execute(sql5)
		orank = cursor.fetchall()
		redata['rank'][0] = srank[0][0] + orank[0][0] + 1
	#更新排行榜
	redata['init'] = {}
	redata['init']['sum'] = [0, 0]
	redata['init']['lists'] = []
	redata['init']['content'] = []
	cursor.execute('SELECT COUNT(*) as numnei FROM students')
	numnei = cursor.fetchall()
	cursor.execute('SELECT COUNT(*) as numwai FROM others')
	numwai = cursor.fetchall()
	redata['init']['sum'][0] = numwai[0][0] + numnei[0][0]
	redata['init']['sum'][1] = numnei[0][0]
	cursor.execute('SELECT avatarUrl,nickName,mark FROM students ORDER BY mark DESC LIMIT 10')
	school = cursor.fetchall()
	cursor.execute('SELECT avatarUrl,nickName,mark FROM students\
					UNION ALL\
					SELECT avatarUrl,nickName,mark FROM others\
					ORDER BY mark DESC\
					LIMIT 10')
	world = cursor.fetchall()
	redata['init']['lists'].append(world)
	redata['init']['lists'].append(school)
	cursor.execute('SELECT content FROM content')
	redata['init']['content'] = cursor.fetchall()
	return json.dumps(redata, ensure_ascii=False)


@app.route('/login', methods=['POST'])
def login():
	db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
	cursor = db.cursor()
	redata = {}
	redata['isMatch'] = True
	redata['rank'] = [0, 0]
	redata['num'] = 0
	redata['init'] = {}
	redata['init']['sum'] = [0, 0]
	redata['init']['lists'] = []
	data = request.json
	wxinfo = data['userInfo']
	info = data['value']
	#插入用户信息
	if data['type'] == 0:
		sql2 = "INSERT INTO students(name, stuid, phone, nickName, avatarUrl, openid, did)\
				values('%s', '%s', '%s', '%s', '%s', '%s', '0')"\
				% (info['name'], info['num'], info['phone'],\
				wxinfo['nickName'], wxinfo['avatarUrl'], data['openID'])
	else:
		sql2 = "INSERT INTO others(phone, nickName, avatarUrl, openid, did)\
				values('%s', '%s', '%s', '%s', '0')"\
				% (info['phone'],\
				wxinfo['nickName'], wxinfo['avatarUrl'], data['openID'])
	try:
	    cursor.execute(sql2)
	    db.commit()
	    if data['type'] == 0:
	    	import mail
	except:
		db.rollback()
		print('插入或更新错误')
	finally:
		pass
	#更新排名
	if data['type'] == 0:
		cursor.execute("SELECT mark FROM students WHERE openid = '%s'" % (data['openID']))
		mark = cursor.fetchall()
		sql3 = "SELECT mark FROM students\
				WHERE openid = '%s'" % (data['openID'])
		cursor.execute(sql3)
		mark = cursor.fetchall()
		sql4 = "SELECT COUNT(*) as srank FROM students\
				WHERE mark > '%d'" % (mark[0][0])
		cursor.execute(sql4)
		srank = cursor.fetchall()
		redata['rank'][1] = srank[0][0] + 1
		sql5 = "SELECT COUNT(*) as orank FROM others\
				WHERE mark > '%d'" % (mark[0][0])
		cursor.execute(sql5)
		orank = cursor.fetchall()
		redata['rank'][0] = srank[0][0] + orank[0][0] + 1
	else:
		cursor.execute("SELECT mark FROM others WHERE openid = '%s'" % (data['openID']))
		mark = cursor.fetchall()
		sql3 = "SELECT mark FROM others WHERE openid = '%s'" % (data['openID'])
		cursor.execute(sql3)
		mark = cursor.fetchall()
		sql4 = "SELECT COUNT(*) as srank FROM students\
				WHERE mark > '%d'" % (mark[0][0])
		cursor.execute(sql4)
		srank = cursor.fetchall()
		redata['rank'][1] = 0
		sql5 = "SELECT COUNT(*) as orank FROM others\
				WHERE mark > '%d'" % (mark[0][0])
		cursor.execute(sql5)
		orank = cursor.fetchall()
		redata['rank'][0] = srank[0][0] + orank[0][0] + 1
	redata['num'] = mark[0][0]
	#更新排行榜
	cursor.execute('SELECT avatarUrl,nickName,mark FROM students ORDER BY mark DESC LIMIT 10')
	school = cursor.fetchall()
	cursor.execute('SELECT avatarUrl,nickName,mark FROM students\
					UNION ALL\
					SELECT avatarUrl,nickName,mark FROM others\
					ORDER BY mark DESC\
					LIMIT 10')
	world = cursor.fetchall()
	redata['init']['lists'].append(world)
	redata['init']['lists'].append(school)
	#更新人数
	cursor.execute('SELECT COUNT(*) as numnei FROM students')
	numnei = cursor.fetchall()
	cursor.execute('SELECT COUNT(*) as numwai FROM others')
	numwai = cursor.fetchall()
	redata['init']['sum'][1] = numnei[0][0]
	redata['init']['sum'][0] = numwai[0][0] + numnei[0][0]
	db.close()
	return json.dumps(redata, ensure_ascii=False)


@app.route('/questionget', methods=['POST'])
def questionget():
	db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
	cursor = db.cursor()
	data = request.json
	redata = {}
	redata['title'] = ''
	redata['op'] = []
	redata['num'] = 0
	cursor.execute("SELECT COUNT(*) FROM questions")
	N = cursor.fetchall()
	flag = 0
	if cursor.execute("SELECT did FROM students WHERE openid = '%s'" % (data['openID'])) != 0:
		pass
	else:
		cursor.execute("SELECT did FROM others WHERE openid = '%s'" % (data['openID']))
		flag = 1
	did = cursor.fetchall()
	if did[0][0] == '0':
		question_id = random.randrange(1, N[0][0]+1)
	else:
		while 1:
			question_id = random.randrange(1, N[0][0]+1)
			if str(question_id) not in did[0][0]:
				break
	cursor.execute("SELECT title, opa, opb, opc, opd FROM questions\
			WHERE id = '%d'" % (question_id))
	question = cursor.fetchall()
	redata['title'] = question[0][0]
	for i in range(1, 5):
		redata['op'].append(question[0][i])
	if flag == 0:
		sql1 = "UPDATE students\
			   SET did = '%s'\
			   WHERE openid = '%s'" % (did[0][0] + ' ' + str(question_id), data['openID'])
		sql2 = "UPDATE students\
				SET lastdid = '%d'\
				WHERE openid = '%s'" % (question_id, data['openID'])
	else:
		sql1 = "UPDATE others\
			   SET did = '%s'\
			   WHERE openid = '%s'" % (did[0][0] + ' ' + str(question_id), data['openID'])
		sql2 = "UPDATE others\
				SET lastdid = '%d'\
				WHERE openid = '%s'" % (question_id, data['openID'])
	try:
		cursor.execute(sql1)
		cursor.execute(sql2)
		db.commit()
	except:
		cursor.rollback()
		print("更新did错误")
	if flag == 0:
		cursor.execute("SELECT mark FROM students WHERE openid = '%s'" % (data['openID']))
		mark = cursor.fetchall()
	else:
		cursor.execute("SELECT mark FROM others WHERE openid = '%s'" % (data['openID']))
		mark = cursor.fetchall()
	redata['num'] = mark[0][0]
	db.close()
	return json.dumps(redata, ensure_ascii=False)


@app.route('/questionjudge', methods=['POST'])
def questionjudge():
	db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
	cursor = db.cursor()
	data = request.json
	flag = 0
	redata = {}
	redata['judge'] = False
	redata['opr'] = ''
	if cursor.execute("SELECT lastdid,mark,conti FROM students WHERE openid = '%s'" % (data['openID'])) != 0:
		pass
	else:
		cursor.execute("SELECT lastdid,mark,conti FROM others WHERE openid = '%s'" % (data['openID']))
		flag = 1
	temp = cursor.fetchall()
	cursor.execute("SELECT opr FROM questions WHERE id = '%d'" % (temp[0][0]))
	opr = cursor.fetchall()
	redata['opr'] = opr[0][0]
	if data['userOp'] == opr[0][0]:
		redata['judge'] = True
		if temp[0][2] == 0:
			add = 1
		elif temp[0][2] == 1:
			add = 2
		else:
			add = 4
		if flag == 0:
			sql = "UPDATE students\
				   SET mark = '%d',\
				   conti = '%d'\
				   WHERE openid = '%s'" % (temp[0][1] + add, temp[0][2] + 1, data['openID'])
			try:
				cursor.execute(sql)
				db.commit()
			except:
				cursor.rollback()
				print("更新分数错误")
		else:
			sql = "UPDATE others\
				   SET mark = '%d',\
				   conti = '%d'\
				   WHERE openid = '%s'" % (temp[0][1] + add, temp[0][2] + 1, data['openID'])
			try:
				cursor.execute(sql)
				db.commit()
			except:
				cursor.rollback()
				print("更新分数错误")
	else:
		redata['judge'] = False
		if flag == 0:
			sql = "UPDATE students\
				   SET conti = 0\
				   WHERE openid = '%s'" % (data['openID'])
			try:
				cursor.execute(sql)
				db.commit()
			except:
				cursor.rollback()
				print("更新conti错误")
		else:
			sql = "UPDATE others\
				   SET conti = 0\
				   WHERE openid = '%s'" % (data['openID'])
			try:
				cursor.execute(sql)
				db.commit()
			except:
				cursor.rollback()
				print("更新conti错误")
	db.close()
	return json.dumps(redata, ensure_ascii=False)


@app.route('/finish', methods=['POST'])
def finish():
	db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
	cursor = db.cursor()
	data = request.json
	redata = {}
	redata['num'] = 0
	flag = 2
	if cursor.execute("SELECT mark FROM students WHERE openid = '%s'" % (data['openID'])) != 0:
		flag = 0
		pass
	else:
		cursor.execute("SELECT mark FROM others WHERE openid = '%s'" % (data['openID']))
		flag = 1
	mark = cursor.fetchall()
	redata['num'] = mark[0][0]
	if flag == 0:
		sql = "UPDATE students\
			   SET conti = 0\
			   WHERE openid = '%s'" % (data['openID'])
		try:
			cursor.execute(sql)
			db.commit()
		except:
			cursor.rollback()
			print("更新conti错误")
	else:
		sql = "UPDATE others\
			   SET conti = 0\
			   WHERE openid = '%s'" % (data['openID'])
		try:
			cursor.execute(sql)
			db.commit()
		except:
			cursor.rollback()
			print("更新conti错误")
	db.close()
	return json.dumps(redata, ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True)
