# _*_ coding:utf-8 _*_
""""
create by lu
实现注册和登录的逻辑
"""
import re

from flask import current_app, session
from . import api
from flask import request, jsonify
from Logic.utils.response_code import RET
from Logic import redis_store, db
from Logic.models import User


@api.route("/session")
def check_login_status():
    user_id = session.get("user_id")
    name = session.get("name")
    return jsonify(erron=RET.OK, errmsg="OK", data={"user_id": user_id, "name": name})


@api.route("/session", methods=["DELETE"])
def logout():
    """
    执行退出操作
    :return:
    """
    session.pop("user_id")
    session.pop("name")
    session.pop("mobile")
    return jsonify(erron=RET.OK, errmsg="OK")


@api.route('/session', methods=['POST'])
def login():
    """
    登录的逻辑
    1.获取前端传过来的账户和密码
    2.对账户密码进行校验（校验是否存在）
    3.查询指定账户（根据mobile）
    4.校验密码
    5.保存当前的信息到session里
    6.返回数据
    :return:
    """
    login_dic = request.json
    mobile = login_dic.get("mobile")
    password = login_dic.get("password")

    if not all([mobile, password]):
        return jsonify(erron=RET.PARAMERR, errmsg="参数有误")
    # 校验手机号码的位数和格式是否有问题
    if not re.match("^1[3456789][0-9]{9}$", mobile):
        return jsonify(erron=RET.PARAMERR, errmsg="手机格式有误")
    # 通过手机号码查询数据库中的用户信息
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR, errmsg="数据库查询问题")
    # 4，校验密码
    if not user.check_passowrd(password):
        return jsonify(erron=RET.PWDERR, errmsg="密码错误")
    # 5保存当前的信息到session里
    session['user_id'] = user.id
    session['name'] = user.name
    session['mobile'] = user.mobile
    return jsonify(erron=RET.OK, errmsg="登录成功")


@api.route('/users', methods=["POST"])
def register():
    # 1. 获取手机号码
    data_dict = request.json
    mobile = data_dict.get("mobile")
    phonenum = data_dict.get("phonecode")
    password = data_dict.get("password")
    if not all([mobile, phonenum, password]):
        return jsonify(erron=RET.PARAMERR, errmsg="参数有问题")
     #TODO:// 测试 暂时关闭验证码功能
    # 2 获取真实的短信验证码
    # try:
    #     read_phonecode = redis_store.get('Mobile:' + mobile)
    #
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(erron=RET.NODATA, errmsg="查询验证码错误")
    # 3.进行验证码校验
    # if phonenum != read_phonecode:
    #     return jsonify(erron=RET.NODATA, errmsg="验证码输入有误")

    # 判断手机号是否已经存在
    if User.query.filter(User.mobile == mobile).first():
        return jsonify(erron=RET.DATAEXIST, errmsg="账户已经存在")

    # 4初始化模型
    user = User()
    user.mobile = mobile
    user.name = mobile
    user.password = password
    # 5.保存到数据库中
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR, errmsg="保存用户数据失败")

    session['user_id'] = user.id
    session['name'] = user.name
    session['mobile'] = user.mobile
    # 给出响应
    return jsonify(erron=RET.OK, errmsg="注册成功")
