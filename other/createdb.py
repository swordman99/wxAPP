import pymysql
import os
db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
cursor = db.cursor()
cursor.execute('DROP TABLE IF EXISTS students')
sql1 = '''CREATE TABLE students(
          id int PRIMARY KEY AUTO_INCREMENT,
          name varchar(25) NOT NULL,
          studentid char(20) NOT NULL,
          phonenumber char(20) NOT NULL,
          mark char(8),
          level char(8),
          password char(8))
          DEFAULT CHARSET=UTF8MB4'''
cursor.execute('DROP TABLE IF EXISTS questions')
sql2 = '''CREATE TABLE questions(
          id int PRIMARY KEY AUTO_INCREMENT,
          title text NOT NULL,
          opa text NOT NULL,
          opb text NOT NULL,
          opc text NOT NULL,
          opd text NOT NULL,
          opr char(2) NOT NULL)
          DEFAULT CHARSET=UTF8MB4'''
try:
     cursor.execute(sql1)
     cursor.execute(sql2)
     db.commit()
except:
	db.rollback()
	print('数据库错误')
db.close()
