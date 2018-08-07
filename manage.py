from flask import Flask
from flask import request
import pymysql
import os
import json

db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
cursor = db.cursor()

app = Flask(__name__)


@app.route('/')
def index():
    s1 = '<h1>欢迎！</h1>'
    s2 = '<a href="http://www.miitbeian.gov.cn">京ICP备18040938号</a>'
    return s1 + s2


@app.route('/home', methods=['POST'])
def home():
	data = request.get_json(force=True)
	if data['id'] == '1':
		t = {}
		t['rank'] = '1'
		return json.dumps(t, ensure_ascii=False)
	else:
		t = {}
		t['rank'] = '0'
		return json.dumps(t, ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True)
