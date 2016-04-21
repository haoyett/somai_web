#!/usr/local/bin python
# -*- coding: utf8 -*-

"""sphinx调用封装

@date: 2016-04-10
@author: Fan Yitian
@brief: 
相关依赖：1. sphinxapi.py
用法示例：
	sphinxconfig = {
		'host': '127.0.0.1',
		'port': 9312
	}
	cl = Sphinx(sphinxconfig)

	q = 'fanyitian'
	res = cl.query(q)
	lastError = cl.getLastError()
	lastWarning = cl.getLastWarning()

	print('error: %s' % (lastError))
	print('warning: %s' % (lastWarning))
"""

# 标准库
import sys
import time
# 第三方库
from sphinxapi import *
# 应用程序自有库

class Sphinx(object):
	"""docstring for Sphinx"""

	_cl = None		# sphinxclient

	def __init__(self, sphinxconfig):
		try:
			self._cl = SphinxClient()

			host = sphinxconfig.get('host', 'localhost')
			port = int(sphinxconfig.get('port', 9312))
			self._cl.SetServer(host, port)

			# mode = sphinxconfig.get('mode', SPH_MATCH_ANY)
			mode = sphinxconfig.get('mode', SPH_MATCH_ALL)
			self._cl.SetMatchMode(mode)

		except Exception as e:
			print('SphinxClient Connect Error! %s' % (e))

	def matchMode(self, mode):
		"""设置匹配模式"""
		self._cl.SetMatchMode(mode)

	def filterWeights(self, weights):
		"""设置字段权重"""
		self._cl.SetFieldWeights(weights)

	def filter(self, filtercol, filtervals):
		"""设置属性过滤"""
		self._cl.SetFilter(filtercol, filtervals)

	def groupby(self, groupby, groupsort = '@count desc'):
		"""设置分组属性"""
		self._cl.SetGroupBy(groupby, SPH_GROUPBY_ATTR, groupsort)

	def sortby(self, sortby):
		"""设置排序模式"""
		self._cl.SetSortMode(SPH_SORT_EXTENDED, sortby)

	def limit(self, offset, limit):
		"""设置结果集偏移量"""
		self._cl.SetLimits(offset, limit, max(limit,1000))
		# self._cl.SetLimits(offset, limit, limit)

	def select(self, select = '*'):
		self._cl.SetSelect(select);
		pass

	def query(self, q, index='*'):
		"""查询"""
		# index可以包含一个或多个索引名。默认*。允许"空格、;、,"分割
		res = self._cl.Query(q, index)

		if isinstance(res, (dict)):
			if res.has_key('matches'):
				matchesPros = []
				for match in res['matches']:
					attrsDict = {}
					attrsDict['id'] = match['id']
					attrsDict['weight'] = match['weight']
					for attr in res['attrs']:
						attrname = attr[0]
						attrtype = attr[1]
						value = match['attrs'][attrname]
						if attrtype==SPH_ATTR_TIMESTAMP:
							value = time.strftime ( '%Y-%m-%d %H:%M:%S', time.localtime(value) )

						attrsDict[attrname] = value

					matchesPros.append(attrsDict)
				
				res['matches'] = matchesPros

		# res结构
		## res = {
		# 	'total': '',
		# 	'total_found': '',
		# 	'time': '',
		# 	'words': '',
		# 	'matches': '',
		# }
		return res

	def getLastError(self):
		"""获取错误信息"""
		return self._cl.GetLastError()

	def getLastWarning(self):
		"""获取告警信息"""
		return self._cl.GetLastWarning()


if __name__ == '__main__':
	
	sphinxconfig = {
		'host': '127.0.0.1',
		'port': 9312
	}
	cl = Sphinx(sphinxconfig)

	q = 'fanyitian'

	res = cl.query(q)

	lastError = cl.getLastError()
	print('error: %s' % (lastError))

	lastWarning = cl.getLastWarning()
	print('warning: %s' % (lastWarning))


	print('Query \'%s\' retrieved %d of %d matches in %s sec' % (q, res['total'], res['total_found'], res['time']))
	print('Query stats:')

	if res.has_key('words'):
		for info in res['words']:
			print('\t\'%s\' found %d times in %d documents' % (info['word'], info['hits'], info['docs']))

	if res.has_key('matches'):
		n = 1
		print('\nMatches:')
		for match in res['matches']:
			attrsdump = ''
			for key, value in match.items():
				attrsdump = '%s, %s=%s' % ( attrsdump, key, value )
			print('%d. %s' % (n, attrsdump))
			n += 1	

