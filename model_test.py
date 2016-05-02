#!/usr/local/bin python
# -*- coding: utf8 -*-

'''model module test.

@date: 2016-04-29
@author: Fan Yitian 
@version: 0.01
'''

# 标准库
import unittest
import re
import sys
from pprint import pprint

# 第三方库

# 应用程序自有库
from model import Model


class TestModelMethods(unittest.TestCase):
  
    def setUp(self):
        self.c = Model()
        reload(sys)
        sys.setdefaultencoding('utf8')
        pass

    def tearDown(self):
        self.c.__del__()
        pass

    def test_getImageUrlFromOSS(self):
        str1 = 2
        imgType1 = 'user'
        url1 = self.c.getImageUrlFromOSS(str1, imgType1)
        pattern = r'.+/avatar/\w+\.jpeg'
        m = re.search(pattern, url1)
        self.assertIsNotNone(m.group(0))


    def test_getUser(self):
        intId = 11212
        user = self.c.getUser(intId)
        # pprint(user)

        self.assertIn('user',user)
        self.assertIn('id', user['user'])
        self.assertIn('name', user['user'])
        self.assertIn('uid', user['user'])
        self.assertIn('avatar', user['user'])

        self.assertIn('works',user)
        if user['works']:
            for row in user['works']:
                self.assertIn('id', row)
                self.assertIn('name', row)
                self.assertIn('company_id', row)
                self.assertIn('position', row)

        self.assertIn('edus',user)
        if user['edus']:
            for row in user['edus']:
                self.assertIn('id', row)
                self.assertIn('school', row)
                
    
if __name__ == '__main__':
      unittest.main()