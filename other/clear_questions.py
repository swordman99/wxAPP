import pymysql
import os
db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
cursor = db.cursor()
cursor.execute('DROP TABLE IF EXISTS questions')
sql = '''CREATE TABLE questions(
          id int PRIMARY KEY AUTO_INCREMENT,
          title text NOT NULL,
          opa text NOT NULL,
          opb text NOT NULL,
          opc text NOT NULL,
          opd text NOT NULL,
          opr char(2))
          DEFAULT CHARSET=UTF8MB4'''
try:
     cursor.execute(sql)
     db.commit()
except:
	db.rollback()
	print('数据库错误')
db.close()
