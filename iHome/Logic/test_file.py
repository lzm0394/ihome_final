# _*_ coding:utf-8 _*_
""""
create by lu
"""
import random

import redis

sms_code = "%06d" % random.randint(0, 999999)
print sms_code
