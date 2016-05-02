#!/usr/local/bin python
# -*- coding: utf8 -*-

'''link module test.

@date: 2016-04-29
@author: Fan Yitian 
@version: 0.01
'''

# 标准库
import unittest

# 第三方库

# 应用程序自有库
from link import Link


class TestLinkMethods(unittest.TestCase):
  
    def setUp(self):
        self.c = Link()
        pass

    def tearDown(self):
        pass

    def test_connectMysql(self):
        db = self.c.connectMysql(db = 'maimai')
        db.query('show tables')
        rows = db.fetchAllRows()
        self.assertEqual(type(rows), tuple)
    
    def test_connectRedis(self):
        redis = self.c.connectRedis()
        keys = redis.keys()
        self.assertEqual(type(keys), list)

    def test_connectSphinx(self):
        sphinx = self.c.connectSphinx()
        res = sphinx.query('a')
        self.assertIn('status', res)
        self.assertIn('matches', res)
        
    
if __name__ == '__main__':
      unittest.main()