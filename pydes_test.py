#!/usr/local/bin python
# -*- coding: utf8 -*-

'''pydes test.

@date: 2016-04-29
@author: Fan Yitian 
@version: 0.01
'''

# 标准库
import unittest

# 第三方库

# 应用程序自有库
from pydes import PyCrypt


class TestPydesMethods(unittest.TestCase):
  
    def setUp(self):
        self.key = 'B&C#@*UA'   # 加密key
        self.c = PyCrypt(self.key)
        pass

    def tearDown(self):
        pass

    def test_encrypt(self):
        string = '101212'
        self.assertEqual(self.c.encrypt(string), 'VlY9zSbVN4I=')
        self.assertEqual(self.c.decrypt(self.c.encrypt(string)), string)

    def test_decrypt(self):
        string = 'VlY9zSbVN4I='
        self.assertEqual(self.c.decrypt(string), '101212')
        self.assertEqual(self.c.encrypt(str(self.c.decrypt(string))), string)


if __name__ == '__main__':
      unittest.main()