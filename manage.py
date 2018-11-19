from flask import Flask
from flask import request
import pymysql
import os
import json
import random
import requests
import hashlib


def to_bytes(text):
    if isinstance(text, bytes):
        return text
    elif isinstance(text, (str, int, float)):
        return str(text).encode('utf-8')
    else:
        raise TypeError
SHA1 = lambda data: hashlib.sha1(to_bytes(data)).hexdigest()


app = Flask(__name__)


@app.route('/')
def index():
    s1 = '欢迎访问微信小程序“地学知识竞赛”后台网站！'
    s2 = '<a href="http://www.miitbeian.gov.cn">京ICP备18040938号-1</a>'
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
	print(s1)
	s2 = s1.split('"')
	redata['openID'] = SHA1(to_bytes(SHA1(to_bytes(s2[7]))))
	db.close()
	return json.dumps(redata, ensure_ascii=False)


@app.route('/getfreq', methods=['POST'])
def getfreq():
	db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
	cursor = db.cursor()
	data = request.json
	redata = {}
	redata['last'] = 0
	freqall = 4
	if cursor.execute("SELECT freq FROM students WHERE openid = '%s'" % (data['openID'])) != 0:
		freq = cursor.fetchall()
		redata['last'] = freqall - freq[0][0]
	elif cursor.execute("SELECT freq FROM others WHERE openid = '%s'" % (data['openID'])) != 0:
		freq = cursor.fetchall()
		redata['last'] = freqall - freq[0][0]
	db.close()
	redata['nexttime'] = '暂定12月1日'
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
	print(wxinfo)
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
	db.close()
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
	if data['type'] == 0 and \
	cursor.execute("SELECT openid FROM students WHERE openid = '%s'" % (data['openID'])) == 0:
		sql2 = "INSERT INTO students(name, stuid, phone, nickName, avatarUrl, openid, did)\
				values('%s', '%s', '%s', '%s', '%s', '%s', '0')"\
				% (info['name'], info['num'], info['phone'],\
				wxinfo['nickName'], wxinfo['avatarUrl'], data['openID'])
	elif data['type'] == 1 and\
	cursor.execute("SELECT openid FROM others WHERE openid = '%s'" % (data['openID'])) == 0:
		sql2 = "INSERT INTO others(phone, nickName, avatarUrl, openid, did)\
				values('%s', '%s', '%s', '%s', '0')"\
				% (info['phone'],\
				wxinfo['nickName'], wxinfo['avatarUrl'], data['openID'])
	else:
		#更新排名
		if cursor.execute("SELECT mark FROM students WHERE openid = '%s'" % (data['openID'])) != 0:
			mark = cursor.fetchall()
			if mark == ():
				mark = [[0]]
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
		elif cursor.execute("SELECT mark FROM others WHERE openid = '%s'" % (data['openID'])) != 0:
			mark = cursor.fetchall()
			if mark == ():
				mark = [[0]]
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
		print("排名")
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
		print("排行榜")
		#更新人数
		cursor.execute('SELECT COUNT(*) as numnei FROM students')
		numnei = cursor.fetchall()
		cursor.execute('SELECT COUNT(*) as numwai FROM others')
		numwai = cursor.fetchall()
		redata['init']['sum'][1] = numnei[0][0]
		redata['init']['sum'][0] = numwai[0][0] + numnei[0][0]
		print("人数")
		db.close()
		return json.dumps(redata, ensure_ascii=False)
	try:
	    cursor.execute(sql2)
	    db.commit()
	    #if data['type'] == 0:
	    #	import mail
	except:
		db.rollback()
		print('插入信息错误')
	finally:
		pass
	#更新排名
	if cursor.execute("SELECT mark FROM students WHERE openid = '%s'" % (data['openID'])) != 0:
		mark = cursor.fetchall()
		if mark == ():
			mark = [[0]]
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
	elif cursor.execute("SELECT mark FROM others WHERE openid = '%s'" % (data['openID'])) != 0:
		mark = cursor.fetchall()
		if mark == ():
			mark = [[0]]
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
	print("排名")
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
	print("排行榜")
	#更新人数
	cursor.execute('SELECT COUNT(*) as numnei FROM students')
	numnei = cursor.fetchall()
	cursor.execute('SELECT COUNT(*) as numwai FROM others')
	numwai = cursor.fetchall()
	redata['init']['sum'][1] = numnei[0][0]
	redata['init']['sum'][0] = numwai[0][0] + numnei[0][0]
	print("人数")
	cursor.execute('SELECT content FROM content')
	redata['init']['content'] = cursor.fetchall()
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
	oprtemp = 0
	cursor.execute("SELECT COUNT(*) FROM questions")
	N = cursor.fetchall()
	flag = 2
	if cursor.execute("SELECT did FROM students WHERE openid = '%s'" % (data['openID'])) != 0:
		did = cursor.fetchall()
		cursor.execute("SELECT qfreq FROM students WHERE openid = '%s'" % (data['openID']))
		qfreq = cursor.fetchall()
		flag = 0
	else:
		cursor.execute("SELECT did FROM others WHERE openid = '%s'" % (data['openID']))
		did = cursor.fetchall()
		cursor.execute("SELECT qfreq FROM others WHERE openid = '%s'" % (data['openID']))
		qfreq = cursor.fetchall()
		flag = 1
	if qfreq[0][0] > 50:
		return "请勿作弊"
	else:
		if did[0][0] == '0':
			question_id = random.randrange(1, N[0][0]+1)
		else:
			while 1:
				question_id = random.randrange(1, N[0][0]+1)
				if str(question_id) not in did[0][0]:
					break
		cursor.execute("SELECT title, opa, opb, opc, opd, opr FROM questions\
				WHERE id = '%d'" % (question_id))
		question = cursor.fetchall()
		redata['title'] = question[0][0]
		temp = 0
		if question[0][5] == 'a':
			temp = 1
		elif question[0][5] == 'b':
			temp = 2
		elif question[0][5] == 'c':
			temp = 3
		elif question[0][5] == 'd':
			temp = 4
		lst = [1, 2, 3, 4]
		random.shuffle(lst)
		for i in range(len(lst)):
			if lst[i] == temp:
				oprtemp = i + 1
			redata['op'].append(question[0][lst[i]])
		if flag == 0:
			sql = "UPDATE students\
				   SET did = '%s',\
					lastdid = '%d',\
					lastjudge = 0,\
					qfreq = '%d',\
					oprtemp = '%d'\
					WHERE openid = '%s'" % \
					(did[0][0] + ' ' + str(question_id), question_id, qfreq[0][0] + 1,\
					 oprtemp, data['openID'])
		else:
			sql = "UPDATE others\
				   SET did = '%s',\
					lastdid = '%d',\
					lastjudge = 0,\
					qfreq = '%d',\
					oprtemp = '%d'\
					WHERE openid = '%s'" % \
					(did[0][0] + ' ' + str(question_id), question_id, qfreq[0][0] + 1,\
					 oprtemp, data['openID'])
		try:
			cursor.execute(sql)
			db.commit()
		except:
			cursor.rollback()
			print("更新错误")
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
	flag = 2
	redata = {}
	redata['judge'] = False
	redata['opr'] = ''
	opr = ''
	if cursor.execute("SELECT lastdid,mark,conti,lastjudge,oprtemp FROM students WHERE openid = '%s'" % (data['openID'])) != 0:
		flag = 0
	else:
		cursor.execute("SELECT lastdid,mark,conti,lastjudge,oprtemp FROM others WHERE openid = '%s'" % (data['openID']))
		flag = 1
	temp = cursor.fetchall()
	if temp[0][3] == 1:
		return "请勿作弊"
	else:
		if temp[0][4] == 1:
			opr = 'a'
		elif temp[0][4] == 2:
			opr = 'b'
		elif temp[0][4] == 3:
			opr = 'c'
		elif temp[0][4] == 4:
			opr = 'd'
		redata['opr'] = opr
		if data['userOp'] == redata['opr']:
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
					   conti = '%d',\
					   lastjudge = 1\
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
					   conti = '%d',\
					   lastjudge = 1\
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


@app.route('/sharereward', methods=['POST'])
def sharereward():
	db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
	cursor = db.cursor()
	data = request.json
	redata = {}
	redata['flag'] = 0
	if cursor.execute("SELECT conti FROM students WHERE openid = '%s'" % (data['openID'])) != 0:
		sql = "UPDATE students\
			   SET conti = '%d'\
			   WHERE openid = '%s'" % (1, data['openID'])
		try:
			cursor.execute(sql)
			db.commit()
			redata['flag'] = 1
		except:
			cursor.rollback()
			print("更新conti错误")
	elif cursor.execute("SELECT conti FROM others WHERE openid = '%s'" % (data['openID'])) != 0:
		sql = "UPDATE others\
			   SET conti = '%d'\
			   WHERE openid = '%s'" % (1, data['openID'])
		try:
			cursor.execute(sql)
			db.commit()
			redata['flag'] = 1
		except:
			cursor.rollback()
			print("更新conti错误")
	db.close()
	return json.dumps(redata, ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True)
