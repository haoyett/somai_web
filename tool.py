#!/usr/local/bin python3
# -*- coding: utf8 -*-

'''Tool工具类

@date: 2016-04-29
@author: Fan Yitian 
@version: 0.01
'''

# 标准库
import hashlib
import logging
import re
import json

# 第三方库
from ConfigParser import ConfigParser

# 应用程序自有库


class Tool(object):
	def __init__(self):
		pass

	def md5(self, string):
		"""md5加密串

		Returns:
			md5 string.
		"""
		strMd5 = hashlib.md5(str(string)).hexdigest()
		return strMd5


	def getMysqlConfig(self, db = 'test'):
		"""获取mysql连接配置

		- 依赖配置文件[conf/config.ini]，节点[db]

		Returns:
			dbconfig dict.
		"""

		try:
			cf = ConfigParser()
			cf.read('conf/config.ini')
			dbconfig = {
				'host': cf.get('db', 'host'), 
				'port': cf.getint('db', 'port'), 
				'user': cf.get('db', 'user'), 
				'passwd': cf.get('db', 'passwd'), 
				'db': db
			}
			return dbconfig			
		except Exception as e:
			error = """Can't load config from [conf/config.ini] or [db] node doesn't exist.\n
			Please make sure this file."""
			logging.warning(error)
			print(error)
			raise Exception(e)


	def formatDate(self, strDate, split = '-'):
		"""格式化时间

		Args:
			strDate	string		原日期；支持如下格式
								(xxxx年xx月xx日)
								(xxxx/xx/xx)
								(xxxx-xx-xx)
			split string		转换后分隔符

		Returns:
			date string by `split` segmentation. e.g. 2016-04-30

		Exception:
			not matching format, will return `0000-00-00`
		"""

		f_date = strDate.replace(u"年", split).replace(u"月", split).replace("/", split).replace("-", split)
		re_str = r'(\d{2,4}%s\d{1,2}%s\d{1,2})' % (split, split)
		pattern = re.compile(re_str)
  		pattern_str = pattern.search(f_date)
		if pattern_str:
		    resultDate = pattern_str.group(0)
		else:
		    resultDate = "0000-00-00"

		return resultDate


	def convertSpecialUnicode(self, oldStr):
		"""将unicode编码转换

		Args:
			oldStr string 		待转换的字符

		Returns:
			converted string.
		"""
		oldStr = oldStr.replace("\\u0022", "\"")
		oldStr = oldStr.replace("\\u002D", "-")
		oldStr = oldStr.replace("\\u003D", "=")
		oldStr = oldStr.replace("\\u0026", "&")
		oldStr = oldStr.replace("\\u005C", "\\")

		newStr = oldStr
		return newStr


	def filterEmoji(self, srcStr):
		"""过滤emoji表情"""
		try:
			highpoints = re.compile(u'[\U00010000-\U0010ffff]')
		except Exception as e:
			highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
		resValue = highpoints.sub(u'??', srcStr)
		return resValue


	def responseSuccess(self, data):
		"""响应：成功

		Args:
			data list|dict 		响应数据

		Returns:
			json string.
		"""
		res = {
			'code': 200, 
			'msg': 'ok',
			'data': data,
		}
		return json.dumps(res)


	def responseError(self, code = 400, msg = 'error', data = {}):
		"""响应：失败

		Args:
			code int 		响应码
			msg string 		错误信息
			data list 		响应数据

		Returns:
			Json String.
		"""
		# 返回数据格式
		res = {
			'code': code, 
			'msg': msg,
			'data': data,
		}
		return json.dumps(res)


if __name__ == '__main__':
	pass
