#!/usr/local/bin python
# -*- coding: utf8 -*-

'''pyDes加解密封装
'''

# 标准库
import base64

# 第三方库
from pyDes import *

# 应用程序自有库

class PyCrypt():
    """docstring for PyDes"""
    des_IV = b"\x22\x33\x35\x81\xBC\x38\x5A\xE7" # 自定IV向量

    def __init__(self, key):
        if isinstance(key, (str)):
            key = str.encode(key)

        self.key = key

    def encrypt(self, text):
        """加密函数"""
        if isinstance(text, (int)):
            text = str(text)

        if isinstance(text, (str)):
            text = str.encode(text)

        k = des(self.key, CBC, self.des_IV, pad=None, padmode=PAD_PKCS5)
        encryStr = k.encrypt(text)

        baseStr = base64.b64encode(encryStr) #转base64编码返回
        if isinstance(baseStr, (bytes)):
            baseStr = bytes.decode(baseStr)

        return baseStr

    def decrypt(self, encryStr):
        """解密函数"""
        text = base64.b64decode(encryStr)
        k = des(self.key, CBC, self.des_IV, pad=None, padmode=PAD_PKCS5)
        decryStr = k.decrypt(text)

        if isinstance(decryStr, (bytes)):
            decryStr = bytes.decode(decryStr)

        return decryStr


if __name__ == '__main__':
    key = 'B&C#@*UA'
    # text = 5
    pc = PyCrypt(key)
    # encry = pc.encrypt(text)
    encry = 'YBsb35WqgSI='
    decry = pc.decrypt(encry)

    transEncry = encry.replace('/', '%_%')

    # transEncry = transEncry.replace('%_%', '/')

    print('key:',key)
    # print('text:',text)
    print('encry:', encry)
    print('decry:', decry)

    print('transEncry:', transEncry)
