#!/usr/local/bin python
# -*- coding: utf8 -*-

'''Mysql Connect Instance.

日期：2016-03-11
作者：Fan Yitian
注意：使用前正确安装pymysql	
'''

import pymysql
import time


class MySQL(object):
	"""对pymysql进行简单封装"""

	error_code = '' # MySQL错误码

	_instance = None	# 类实例
	_conn = None		# 数据库conn
	_cur = None			# 游标

	_TIMEOUT = 30 		# 默认超时时间 
	_timecount = 0 		# 连接时间数量

	def __init__(self, dbconfig):

		"""构造器：根据数据库连接参数，连接数据库"""
		try:
			self._conn = pymysql.connect(
				host = dbconfig['host'],
				port = dbconfig.get('port', 3306),
				user = dbconfig['user'],
				passwd = dbconfig['passwd'],
				db = dbconfig.get('db', None),
				charset = dbconfig.get('charset', 'utf8')
				)
		except Exception as e:
			self.error_code = e.args[0]
			error_msg = 'Mysql Connect Error!', e.args[0], e.args[1]
			print(error_msg)

			# 设置重试机制
			# 如果没有超过预设超时时间，则再次尝试连接 
			if self._timecount < self._TIMEOUT :
				interval = 5
				self._timecount += interval
				time.sleep(interval)
				return self.__init__(dbconfig)
			else :
				raise Exception(error_msg)

		# 返回字段是否为字典 pymysql.cursors.DictCursor
		# cur = self._conn.cursor(pymysql.cursors.DictCursor)
		self._cur = self._conn.cursor()
		self._instance = pymysql


	def query(self, sql):
		"""执行 Execute"""
		try:
			self._cur.execute('SET NAMES utf8') 		# 设置默认编码
			result = self._cur.execute(sql)
		except Exception as e:
			print('数据库错误, %s' % (e))
			result = False
		return result


	def update(self, sql):
		"""执行UPDATE操作"""
		try:
			self._cur.execute('SET NAMES utf8')
			result = self._cur.execute(sql)
			self._conn.commit()
		except Exception as e:
			self.error_code = e.args[0]
			print('数据库错误, %s' % (e))
			result = False
		return result


	def delete(self, sql):
		"""执行DELETE操作"""
		try:
			self._cur.execute('SET NAMES utf8')
			result = self._cur.execute(sql)
			self._conn.commit()
		except Exception as e:
			self.error_code = e.args[0]
			print('数据库错误, %s' % (e))
			result = False
		return result

	
	def insert(self, sql):
		"""执行INSERT操作, 返回自增id"""
		try:
			# self._cur.execute('SET NAMES utf8')
			self._cur.execute(sql)	
			self._conn.commit()
			result = self._conn.insert_id()
		except Exception as e:
			self.error_code = e.args[0]
			print('数据库错误, %s' % (e))
			result = False
		return result


	def fetchAllRows(self):
		"""返回结果列表"""
		return self._cur.fetchall()


	def fetchOneRow(self):
		"""返回单条结果"""
		return self._cur.fetchone()


	def getRowCount(self):
		"""返回结果行数"""
		return self._cur.rowcount


	def commit(self):
		"""数据库commit操作"""
		self._conn.commit()


	def rollback(self):
		"""回滚操作"""
		self._conn.rollback()


	def __del__(self):
		""" 资源释放（GC自动调用）"""
		try:
			self._cur.close()
			self._conn.close()
		except Exception as e:
			pass


	def close(self):
		"""关闭数据库连接"""
		self.__del__()
		

if __name__ == '__main__':
	'''连接示例'''

	# 数据库连接参数
	dbconfig = {
		'host': '121.42.59.56', 
		'port': 3306,
		'user': 'root',
		'passwd': '101212',
		'db': 'cantonese'
	}

	db = MySQL(dbconfig)

	# 查询
	sql = "select * from activity"
	db.query(sql)

	result = db.fetchAllRows()
	print(result)

	# # 插入
	# sql = 'insert into usertest(name, passwd) values(%s, %s)'
	# param = ("'test'", "'1212'")
	# sql %= (param)

	# n = db.insert(sql)
	# print('insert :', n)

	# 关闭连接
	db.close()
