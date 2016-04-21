#!/usr/local/bin python
# -*- coding: utf8 -*-


'''web_mai
'''

# 标准库
import os
import json
import sys
import re

# 第三方库
from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, flash

# 应用程序自有库
from model import Model
import log
from log import logging


app = Flask(__name__)

@app.before_request
def before_request():
	# py2.7设置编码
	reload(sys)
	sys.setdefaultencoding('utf8')


	# 记录access_log
	row = [
		request.headers.get('X-Forwarded-For', request.remote_addr),
		request.path,
		request.url,
		request.headers.get('Referer', ''),
	];
	strlog = "access_info(ip/path/url/referer) \t"
	for v in row:
		strlog +=  v + "\t"
	logging.info(strlog)  


@app.teardown_request
def teardown_request(exception):
	pass

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))
    return render_template('500.htm'), 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', (e))
    return render_template('500.htm'), 500
    

""" 路由模块
"""
@app.route('/')	
@app.route('/index')	
def index():
	"""首页"""

	m = Model()
	searchIndex = m.getSearchIndexByConf()

	result = {
		'searchIndex': searchIndex
	}
	return response(result, 'index.html')


@app.route('/company', methods=['GET'])
def company():
	"""公司列表"""
	try:
	    page = int(request.args.get('page', 0))# 获取GET参数，没有参数就赋值 0

	    m = Model()
	    company = m.getCompany(page = page)

	    result = {
			'company': company
		}
	    return response(result)
	except ValueError:
		return responseError(msg = '参数错误')


@app.route('/users', methods=['GET'])
def users():
	"""用户列表"""
	try:
	    cid = int(request.args.get('cid', 0))
	    page = int(request.args.get('page', 0))

	    m = Model()
	    users = m.getUsersByCid(cid = cid, page = page)
	    cname = ''
	    if users:
	    	cname = users[0].get('company_name', 'Users')

	    result = {
	    	'users': users,
	    	'cname': cname
	    }
	    return response(result, 'users.html')
	except ValueError:
		return responseError(msg = '参数错误')


@app.route('/user', methods=['GET'])
def user():
	"""个人信息"""
	try:
	    intId = int(request.args.get('id', 0))

	    m = Model()
	    userInfo= m.getUser(intId)

	    result = {
	    	'user': userInfo['user'],
	    	'works': userInfo['works'],
	    	'edus': userInfo['edus'],
	    }
	    return response(result, 'user.html')
	except ValueError:
		return responseError(msg = '参数错误')

@app.route('/photos', methods=['GET'])
def photos():
	"""图片墙"""
	try:
	    gender = int(request.args.get('gender', 2))
	    page = int(request.args.get('page', 0))

	    pageSize = 60

	    m = Model()
	    photos = m.getPhotos(gender = gender, page = page, pageSize = pageSize)

	    result = {
	    	'photos': photos,
	    }
	    return response(result, 'photos.html')
	except ValueError:
		return responseError(msg = '参数错误')


@app.route('/search', methods=['GET'])
def search():
	"""搜索接口"""
	try:
		strType = str(request.args.get('type', 'user'))			# 搜索类型
		page = int(request.args.get('page', 0))					# 获取GET参数，没有参数就赋值 0
		pageSize = int(request.args.get('page_size', 20))					# 获取GET参数，没有参数就赋值 0
		# cid = request.args.get('cid', None)						# company类型中
		q = request.args.get('q')								# 搜索关键词
		q = str(q.encode('utf8'))

		m = Model()
		result = m.getSearch(strType, q, page, pageSize)

		return response(result)
	except ValueError as e:
		msg = '出现错误, %s' % (e)
		return responseError(msg = msg)


@app.route('/search_suggest', methods=['GET'])
def search_suggest():
	"""搜索推荐接口, 即弹框, 为了更好的精确搜索"""
	try:
		strType = str(request.args.get('type', 'company'))		# 搜索类型
		q = request.args.get('q')								# 搜索关键词
		q = str(q.encode('utf8'))

		m = Model()
		arrList = m.getSearchSuggest(q, type = strType)

		result = {
		 	'list': arrList,
		}
		return response(result)
	except ValueError as e:
		msg = '出现错误, %s' % (e)
		return responseError(msg = msg)





""" 接口公共方法
"""
def response(data, template = None):
	"""封装请求相应"""
	display = str(request.args.get('_display', 'html'))		# 显示方式

	if 'json' == display or template is None:
		return responseSuccess(data)
	else:
		return render_template(template, **data)


def responseSuccess(data):
	# 返回数据格式
	res = {
		'code': 200, 
		'msg': 'ok',
		'data': data,
	}
	return json.dumps(res)


def responseError(code = 400, msg = 'error', data = {}):
	# 返回数据格式
	res = {
		'code': code, 
		'msg': msg,
		'data': data,
	}
	return json.dumps(res)


if __name__ == '__main__':

	log.init_log('log/app')

	# app.debug = True
	app.run()
