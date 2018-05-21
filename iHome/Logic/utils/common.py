# _*_ coding:utf-8 _*_
""""
create by lu
"""
import functools

from flask import session, jsonify, g
from werkzeug.routing import BaseConverter

from Logic.utils.response_code import RET

create_time = '2018/4/28 12:13'


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify(errno=RET.SESSIONERR, errmsg="用户尚未登录")
        else:
            g.user_id = user_id
            return func(*args, **kwargs)

    return wrapper
