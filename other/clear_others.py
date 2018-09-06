import pymysql
import os
db = pymysql.connect('127.0.0.1', 'root', os.environ.get('MYSQL_PASSWORD'), 'demo')
cursor = db.cursor()
cursor.execute('DROP TABLE IF EXISTS students')
sql = '''CREATE TABLE others(
          id int PRIMARY KEY AUTO_INCREMENT,
          phone char(20) NOT NULL,
          nickName varchar(60) NOT NULL,
          avatarUrl text NOT NULL,
          openid text NOT NULL,
          did text,
          lastdid int,
          conti int DEFAULT 0,
          mark int DEFAULT 0,
          level int,
          freq int DEFAULT 0,
          qfreq int DEFAULT 0,
          )
          DEFAULT CHARSET=UTF8MB4'''
try:
     cursor.execute(sql)
     db.commit()
except:
     db.rollback()
     print('数据库错误')
db.close()