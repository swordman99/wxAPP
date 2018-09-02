import pymysql
import os
db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
cursor = db.cursor()
cursor.execute('DROP TABLE IF EXISTS content')
sql = '''CREATE TABLE content(
          id int PRIMARY KEY AUTO_INCREMENT,
          content text
          )
          DEFAULT CHARSET=UTF8MB4'''
try:
     cursor.execute(sql)
     db.commit()
except:
	db.rollback()
	print('数据库错误')
db.close()
