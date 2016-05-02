#!/usr/local/bin python
# -*- coding: utf8 -*-

'''封装Model

日期：2016-04-14
作者：Fan Yitian
'''

# 标准库

# 第三方库
from ConfigParser import ConfigParser
import markdown
import json

# 应用程序自有库
import pydes
import log
from log import logging
from tool import Tool
from link import Link


REDIS_PRE = 'maimai_v0_'	# redis前缀


class Model(object):
	"""docstring for Model"""
	db = None	# mysql
	r = None	# redis
	sp = None	# sphinx

	# 教育信息对应关系
	eduDegreeMap = {
		'0': '专科',
		'1': '本科',
		'2': '硕士',
		'3': '博士',
		'4': '博士后',
		'5': '中学',
		'255': '其他',
	}

	def __init__(self):
		self.tool = Tool()
		self.link = Link()

		if not self.db:
			self.db = self.link.connectMysql(db = 'maimai')

		if not self.r:
			self.r = self.link.connectRedis()
			
		if not self.sp:
			self.sp = self.link.connectSphinx()

		cf = ConfigParser()
		cf.read('conf/config.ini')
		self.imageHost = cf.get('aliyun_oss', 'host')


	def getImageUrlFromOSS(self, keyword, imgType = 'user'):
		"""从OSS获取图片地址

		Args:
			keyword string 		关键词, 分别对应类型为(user[id], company[pycompany], school[pyschool])
			imgType	string 		类型：user/company/school 

		Returns:
			The image url saved OSS.
		"""
		if imgType == 'user':
			intId = keyword
			url = '/avatar/' + self.tool.md5(u'm_d_' + str(intId)) + '.jpeg'
		elif imgType == 'company': 
			pass
		elif imgType == 'school':
			pass
		else:
			return ''

		return self.imageHost + url


	""" 用户信息 start"""

	def getUser(self, intId):
		"""
		查询用户信息，工作经历，教育经历

		Args:
			intId 		- 用户主键id

		Returns:
			user info dict. 
			{
				'user': [],
				'works': [],
				'edus': [],
			}
		"""

		sql = "select id, uid, name, company_id, company_name, position, avatar, gender, rank, loc, trade, trade_category, create_time from user where id = '%s' " % (intId)
		self.db.query(sql)
		userInfo = self.db.fetchOneRow()

		user = {
			'id': userInfo[0],
			'uid': userInfo[1],
			'name': userInfo[2],
			'company_id': userInfo[3],
			'company_name': userInfo[4],
			'position': userInfo[5],
			# 'avatar': userInfo[6],
			'avatar': self.getImageUrlFromOSS(userInfo[0], 'user'),
			'gender': userInfo[7],
			'rank': userInfo[8],
			'loc': userInfo[9],
			'trade': userInfo[10],
			'trade_category': userInfo[11],
			'create_time': str(userInfo[12]),
		}
		
		uid = user['uid']

		# 工作经历
		sql = "select id, uid, name, company_id, company_name, position, description, start_date, end_date, update_time, create_time from work where uid = '%s'" % (uid)
		self.db.query(sql)
		works = []
		for row in self.db.fetchAllRows():
			# 暂时取用serial_info的头像
			clogo = 'http://i9.taou.com/maimai/c/interlogo/default.png'

			tmp = {
				'id': row[0],
				'uid': row[1],
				'name': row[2],
				'company_id': row[3],
				'company_name': row[4],
				'position': row[5],
				'description': markdown.markdown(row[6], extensions=['markdown.extensions.nl2br']),
				'start_date': row[7].replace('-','.'),
				'end_date': row[8].replace('-','.').replace('None','至今'),
				'update_time': str(row[9]),
				'create_time': str(row[10]),
				'clogo': clogo,
			}
			works.append(tmp)

		# 教育经历 
		sql = "select id, uid, name, school, department, degree, start_date, end_date, update_time, create_time from education where uid = '%s'" % (uid)
		self.db.query(sql)
		edus = []
		for row in self.db.fetchAllRows():
			# 暂时取用serial_info的公司头像
			schoolUrl = 'http://i9.taou.com/maimai/c/interlogo/default.png'
			
			tmp = {
				'id': row[0],
				'uid': row[1],
				'name': row[2],
				'school': row[3],
				'department': row[4],
				'degree': row[5],
				'degree_name': self.eduDegreeMap.get(str(row[5]), '其他'),
				'start_date': row[6].replace('-','.'),
				'end_date': row[7].replace('-','.').replace('None','至今'),
				'update_time': str(row[8]),
				'create_time': str(row[9]),
				'school_url': schoolUrl,
			}
			edus.append(tmp)

		return {
			'user': user,
			'works': works,
			'edus': edus,
		}


	def getUserByIds(self, ids):
		"""
		查询一批用户

		Args:
			ids[list] 	- 用户主键id

		Returns:
			user list.
		"""
		users = []
		if ids:
			sql = "select id, uid, name, company_id, company_name, position, avatar, gender, rank, loc, trade, trade_category from user where id in (%s)" % (','.join(ids))
			self.db.query(sql)

			users = []
			uids = []
			for row in self.db.fetchAllRows():
				uids.append(str(row[1]))
				users.append({
					'id': row[0],
					'uid': row[1],
					'name': row[2],
					'company_id': row[3],
					'company_name': row[4],
					'position': row[5],
					'avatar': self.getImageUrlFromOSS(row[0], 'user'),
					'gender': row[7],
					'rank': row[8],
					'loc': row[9],
					'trade': row[10],
					'trade_category': row[11],
					})

			# 获取最高学历的学校
			sql = "select uid, school from education where uid in (%s) group by uid order by degree desc" % (','.join(uids))
			self.db.query(sql)
			schoolDict = {}
			for row in self.db.fetchAllRows():
				schoolDict[row[0]] = row[1]

			for row in users:
				if schoolDict.has_key(row['uid']):
					row['school'] = schoolDict[row['uid']]
				else:
					row['school'] = 'None'
		return users

	def getUserByUids(self, uids):
		"""
		根据uid查询一批用户

		Args:
			uids[list] 	- 用户uid列表

		Returns:
			user list.
		"""
		users = []
		if uids:
			sql = "select id, uid, name, company_id, company_name, position, avatar, gender, rank, loc, trade, trade_category from user where uid in (%s)" % (','.join(uids))
			self.db.query(sql)
			users = [dict(id=row[0], uid=row[1], name=row[2], company_id=row[3], company_name=row[4], position=row[5], \
				avatar=self.getImageUrlFromOSS(row[0], 'user'), gender=row[7], rank=row[8], loc=row[9], trade=row[10], trade_category=row[11]) \
			 		for row in self.db.fetchAllRows()]

			# 获取最高学历的学校
			sql = "select uid, school from education where uid in (%s) group by uid order by degree desc" % (','.join(uids))
			self.db.query(sql)
			schoolDict = {}
			for row in self.db.fetchAllRows():
				schoolDict[row[0]] = row[1]

			for row in users:
				if schoolDict.has_key(row['uid']):
					row['school'] = schoolDict[row['uid']]
				else:
					row['school'] = 'None'
		return users



	def getUsersByCid(self, cid = 0, page = 0, pageSize = 20):
		"""
		根据公司id获取用户列表

		Args:
			cid 		- 公司id
			page 		- 分页参数，页码
			pageSize	- 分页参数，每页数量

		Returns:
			user list.
		"""

		start = page * pageSize
		sql = "select id, uid, name, company_id, company_name, position, avatar, gender, rank, loc, trade, trade_category from user where company_id = '%s' limit %s, %s" % (cid, start, pageSize)
		self.db.query(sql)
		users = [dict(id=row[0], uid=row[1], name=row[2], company_id=row[3], company_name=row[4], position=row[5], \
			avatar=self.getImageUrlFromOSS(row[0], 'user'), gender=row[7], rank=row[8], loc=row[9], trade=row[10], trade_category=row[11]) \
		 		for row in self.db.fetchAllRows()]

		# users = [dict(id=row[0], uid=row[1], name=row[2], company_id=row[3], company_name=row[4], position=row[5], avatar=getUserAvatarByLocal(row[0]), gender=row[7], rank=row[8], loc=row[9], trade=row[10], trade_category=row[11]) \
		#  		for row in g.db.fetchAllRows()]
		return users



	""" 照片photo start"""

	def getPhotos(self, gender = 2, page = 0, pageSize = 20):
		"""
		获取头像图片列表

		Args:
			gender 		- 性别：1男，2女
			page 		- 分页参数，页码
			pageSize 	- 分页参数，每页数量

		Returns:
			photo list. id is user AUTO_INCREMENT id.

		"""
		start = page * pageSize 
		# sql = "select id, avatar, trade_category from user where gender = '%s' and avatar like '%%a160%%' limit %s, %s" % (gender, start, pageSize)
		# 随机获取id  条件: gender、160头像、行业trade(IT互联网\通信电子\文化传媒\学生\金融\教育培训)
		sql = 'SELECT t1.id, name, position, trade_category ' \
			'FROM `user` AS t1 JOIN (SELECT ROUND(RAND() * ((SELECT MAX(id) FROM `user`) - (SELECT MIN(id) FROM `user`)) + (SELECT MIN(id) FROM `user`)) AS id) AS t2 ' \
			'WHERE t1.id >= t2.id AND gender = "%s" AND avatar like "%%a160%%" AND trade IN ("IT互联网", "文化传媒", "学生")'\
			'ORDER BY t1.id LIMIT %s' % (gender, pageSize)
		
		self.db.query(sql)
		photos = [dict(id=row[0], avatar=self.getImageUrlFromOSS(row[0], 'user'), name=row[1], position=row[2], trade_category=row[3]) \
		 		for row in self.db.fetchAllRows()]
		return photos

	def getUserAvatarByLocal(self, intId):
		""" (该方法已弃用)
		从本地获取用户图片

		Args:
			intId 		- 用户主键Id

		Returns:
			image file name.
		"""
	    # 读取配置文件, 获得加密key
		cf = ConfigParser()
		cf.read('conf/config.ini')
		key = cf.get('DES', 'image_key')

		# 加密对象
		pc = pydes.PyCrypt(key)
		encryId = pc.encrypt(intId)
		# 由于出现 '/' 问题，导致如法正在写入图片，这里替换 '/' 为 '*_*'
		encryId = encryId.replace('/', '*_*')

		dirPath = '/users/160/'
		fileName = dirPath + encryId + '.jpg'
		return fileName



	""" 公司信息 start"""

	def getCompany(self, page = 0, pageSize = 20):
		"""
		查询公司列表

		Args:
			page 		- 分页参数，页码
			pageSize	- 分页参数，每页数量

		Returns:
			company list.
		"""
		start = page * pageSize
		self.db.query("select company_id from company limit %s, %s" % (start, pageSize))

		company = []
		for row in self.db.fetchAllRows():
			key = REDIS_PRE + 'company_' + str(row[0])
			companyExtend = self.r.hmget(key, 'company_id', 'company_name', 'num', 'trade')
			companyExtend = [x.decode('utf8') for x in companyExtend if isinstance(x, (bytes))]

			if companyExtend:
				oneCompany = {
					'company_id': companyExtend[0],
					'company_name': companyExtend[1],
					'num': companyExtend[2],
					'trade': companyExtend[3], 
				}
				company.append(oneCompany)
		return company


	""" 搜索Search start """

	def getSearchIndexByConf(self):
		"""
		读取配置文件获取搜索的索引

		依赖:
			local_init.int 
		"""
		cf = ConfigParser()
		cf.read('conf/local_init.ini')

		# logging.info('test main logger') 

		result = {}
		for section in cf.sections():
			result[section] = cf.items(section)

		return result

	def getSearchBySphinx(self, q, index = '*'):
		"""
		从sphinx搜索结果

		Args:
			q 		- 搜索词
			index 	- 需要使用的索引, default: '*'

		Returns:
			Id list.
		"""
		res = self.sp.query(q, index)

		lastError = self.sp.getLastError()
		lastWarning = self.sp.getLastWarning()
		if lastError:
			logging.error('getSearchBySphinx has error: %s' % (lastError))
		if lastWarning:
			logging.warning('getSearchBySphinx has warning: %s' % (lastWarning))
		
		return res

	def getSearch(self, strType, q, page = 0, pageSize = 20):
		"""
		搜索

		Args:
			strType			- 搜索类型: user/company/school/position
			q 				- 搜索关键词
			page 			- 分页页码
			pageSize 		- 每页数量

		Returns:
			User List.
		"""
		# 设置分页
		pageSize = min(pageSize, 100)

		result = {}
		if strType == 'user':
			result = self.getSearchUser(q, page, pageSize)
		elif strType == 'company':
			result = self.getSearchCompany(q, page, pageSize);
		elif strType == 'school':
			result  = self.getSearchSchool(q, page, pageSize);
		elif strType == 'position':
			result = self.getSearchPosition(q, page, pageSize);
		
		return result


	def getSearchUser(self, q, page = 0, pageSize = 20):
		"""
		搜索 User

		Args:
			q 			- 搜索词
			page 		- 分页参数

		Returns:
			users list.
		"""

		self.sp.matchMode(0)
		
		# 设置分页
		self.sp.limit(page*pageSize, pageSize)

		res = self.getSearchBySphinx(q, index = 'user')
		if res: 
			ids = []
			if res.has_key('matches') and res['matches']:
				ids = [ str(item['id']) for item in res['matches']]

			users = self.getUserByIds(ids)

			result = {
				'users': users,
				'time': res['time'],
				'total': res['total'],
				'total_found': res['total_found'],
			}
		else: 
			result = {
				'users': [],
				'time': '0',
				'total': 0,
				'total_found': 0,
			}
		return result	

	def getSearchCompany(self, q, page = 0, pageSize = 20):
		"""
		搜索 User

		Args:
			q 				- 公司名称
			page 			- 分页参数

		Returns:
			users list.
		"""

		# self.sp.matchMode(0)
		
		# 设置分页
		self.sp.limit(page*pageSize, pageSize)

		res = self.getSearchBySphinx(q, index = 'company')
		if res: 
			ids = []
			if res.has_key('matches') and res['matches']:
				ids = [ str(item['id']) for item in res['matches']]

			users = self.getUserByIds(ids)

			result = {
				'users': users,
				'time': res['time'],
				'total': res['total'],
				'total_found': res['total_found'],
			}
		else: 
			result = {
				'users': [],
				'time': '0',
				'total': 0,
				'total_found': 0,
			}


		return result	

	def getSearchSchool(self, q, page = 0, pageSize = 20):
		"""
		搜索 User

		Args:
			q 				- 学校名称
			page 			- 分页参数

		Returns:
			users list.
		"""

		## search语句
		# ./search -c /usr/local/coreseek/etc/csft.conf --index school --sortby "uid asc" --filter degree 255 --group uid 北京大学

		# self.sp.matchMode(0)
			
		# 设置分页
		self.sp.limit(page*pageSize, pageSize)
		# @todo ，后期增加过滤
		# self.filter('degree', [255])
		self.sp.groupby('uid')	
		res = self.getSearchBySphinx(q, index = 'school')
		
		if res: 
			uids = []
			if res.has_key('matches') and res['matches']:
				uids = [ str(item['uid']) for item in res['matches']]
			
			users = self.getUserByUids(uids)

			result = {
				'users': users,
				'time': res['time'],
				'total': res['total'],
				'total_found': res['total_found'],
			}
		else: 
			result = {
				'users': [],
				'time': '0',
				'total': 0,
				'total_found': 0,
			}


		return result	

	def getSearchPosition(self, q, page = 0, pageSize = 20):
		"""
		搜索 User

		Args:
			q 				- 职位
			page 			- 分页参数

		Returns:
			users list.
		"""

		# self.sp.matchMode(0)
		
		# ./search -c /usr/local/coreseek/etc/csft.conf --index position --group uid php
			
		# 设置分页
		self.sp.limit(page*pageSize, pageSize)

		self.sp.groupby('uid')	
		res = self.getSearchBySphinx(q, index = 'position')
		
		if res: 
			uids = []
			if res.has_key('matches') and res['matches']:
				uids = [ str(item['uid']) for item in res['matches']]
			
			users = self.getUserByUids(uids)

			result = {
				'users': users,
				'time': res['time'],
				'total': res['total'],
				'total_found': res['total_found'],
			}
		else: 
			result = {
				'users': [],
				'time': '0',
				'total': 0,
				'total_found': 0,
			}

		return result	


	def getSearchSuggest(self, q, type = 'company'):
		"""
		搜索推荐

		Args:
			q 			- 搜索关键词
			type 		- 搜索类型, [company/school/position]

		Returns:
			suggestion string list.

		"""
		limitNum = 5	# 默认只取5条
		result = []
		if type == 'company':
			sql = "select company_name from company where company_name like '%%%s%%' limit %s" % (q, limitNum)
			self.db.query(sql)
			result = [row[0] for row in self.db.fetchAllRows()]
		elif type == 'school':
			# ./search -c /usr/local/coreseek/etc/csft.conf --index school --group school --groupsort '@count desc' 北方工业大学
			self.sp.groupby('school')	
			self.sp.limit(0, limitNum) 	
			res = self.getSearchBySphinx(q, index = 'school')
			if res: 
				result = []
				if res.has_key('matches') and res['matches']:
					result = [ str(item['school']) for item in res['matches']]
		elif type == 'position':
			# ./search -c /usr/local/coreseek/etc/csft.conf --index position --group position --groupsort '@count desc' php
			self.sp.groupby('position')	
			self.sp.limit(0, limitNum) 	
			res = self.getSearchBySphinx(q, index = 'position')
			if res: 
				result = []
				if res.has_key('matches') and res['matches']:
					result = [ str(item['position']) for item in res['matches']]

		return result



	def __del__(self):
		""" 资源释放（GC自动调用）"""
		if self.db is not None:
			self.db.close()

if __name__ == '__main__':
	# main()
	pass