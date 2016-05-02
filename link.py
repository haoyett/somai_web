#!/usr/local/bin python
# -*- coding: utf8 -*-

'''各类资源连接类

@date: 2016-04-30
@author: Fan Yitian 
@brief:
	依赖：[conf/config.ini]
'''

# 标准库
import logging

# 第三方库
from ConfigParser import ConfigParser
import redis

# 应用程序自有库
from mysql import MySQL
from sphinx import Sphinx


class Link(object):
	def __init__(self):
		pass

	def connectMysql(self, db = 'test'):
		"""连接mysql数据库

		- 依赖配置文件[conf/config.ini]，节点[db]

		Args:
			db string 		需要连接的db名称

		Returns:
			mysql instance.
		"""

		cf = ConfigParser()
		cf.read('conf/config.ini')
		dbconfig = {
			'host': cf.get('db', 'host'), 
			'port': cf.getint('db', 'port'), 
			'user': cf.get('db', 'user'), 
			'passwd': cf.get('db', 'passwd'), 
			'db': db
		}	
		dbInstance = MySQL(dbconfig)
		return dbInstance

	def connectRedis(self):
		"""连接Redis

		- 依赖配置文件[conf/config.ini]，节点[redis]

		Returns:
			redis instance.
		"""
		cf = ConfigParser()
		cf.read('conf/config.ini')

		r = redis.StrictRedis(
				host = cf.get('redis', 'host'), 
				port = cf.get('redis', 'port'),
				password = cf.get('redis', 'password')
			)
		return r

	def connectSphinx(self):
		"""
		连接Sphinx

		Returns:
			sphinx instance.
		"""
		cf = ConfigParser()
		cf.read('conf/config.ini')
		sphinxconfig = {
			'host': cf.get('sphinx', 'host'), 
			'port': cf.get('sphinx', 'port')
		}
		sp = Sphinx(sphinxconfig)
		return sp

if __name__ == '__main__':
	pass

