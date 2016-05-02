#!/usr/local/bin python
# -*- coding: utf8 -*-

'''tool test.

@date: 2016-04-29
@author: Fan Yitian 
@version: 0.01
'''

# 标准库
import unittest
import json

# 第三方库

# 应用程序自有库
from tool import Tool


class TestToolMethods(unittest.TestCase):
  
    def setUp(self):
        self.c = Tool()
        pass

    def tearDown(self):
        pass

    def test_md5(self):
        string = 101212
        self.assertEqual(self.c.md5(string), '4601f3ffaf1aa7c525b3d9f5a820ca80')

    def test_getMysqlConfig(self):
        dbconfig = self.c.getMysqlConfig()
        self.assertEqual(type(dbconfig), dict)
        self.assertTrue('host' in dbconfig)
        self.assertTrue('user' in dbconfig)
        self.assertTrue('passwd' in dbconfig)
        self.assertTrue('db' in dbconfig)

    def test_formatDate(self):
        str1 = u'2016/04/30 00:00:12'
        str2 = u'test 2016-04-30 00:00:12'
        str3 = u'sm2016年04月30日 00:00:12'

        distDate = u'2016-04-30'
        self.assertEqual(self.c.formatDate(str1), distDate)
        self.assertEqual(self.c.formatDate(str2), distDate)
        self.assertEqual(self.c.formatDate(str3), distDate)

        str4 = u'sm2016年04月30日 00:00:12'
        self.assertEqual(self.c.formatDate(str1, ' '), '2016 04 30')

        str5 = u'fdsjkkj20kaj3sjx-3'
        self.assertEqual(self.c.formatDate(str5), '0000-00-00')

    def test_convertSpecialUnicode(self):
        oldStr = "\\u002Dtest"
        self.assertEqual(self.c.convertSpecialUnicode(oldStr), '-test')

    def test_filterEmoji(self):
        str1 = u"This is a smiley \uD83C\uDFA6 face \uD860\uDD5D \uD860\uDE07 \uD860\uDEE2 \uD863\uDCCA \uD863\uDCCD \uD863\uDCD2 \uD867\uDD98"
        str1_true = u'This is a smiley ?? face ?? ?? ?? ?? ?? ?? ??'
        self.assertEqual(self.c.filterEmoji(str1), str1_true)
    
    def test_responseSuccess(self):
        data = {'test_id': 101212}
        data_true = {
            'code': 200, 
            'msg': 'ok',
            'data': data
        }
        self.assertEqual(json.loads(self.c.responseSuccess(data)), data_true)

    def test_responseError(self):
        data = {'test_id': 101212}
        data_true = {
            'code': 500, 
            'msg': 'error',
            'data': data
        }
        self.assertEqual(json.loads(self.c.responseError(code = 500, msg = 'error', data = data)), data_true)
    

if __name__ == '__main__':
      unittest.main()