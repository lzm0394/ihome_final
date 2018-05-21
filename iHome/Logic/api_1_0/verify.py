# _*_ coding:utf-8 _*_
""""
create by lu
"""
import json
import re
import random
from flask import request, jsonify, make_response, abort, current_app

from Logic import redis_store, constants, db
from Logic.api_1_0 import api
from Logic.models import User
from Logic.utils.captcha.captcha import captcha
from Logic.utils.response_code import RET
from Logic.utils.sms import CCPR

"""
@提供验证码的信息 
@主要是图片验证码和短信验证码
"""


@api.route('/sms_code', methods=["POST"])
def send_sms_code():
    # j接受前端发来的信息 提取想要的数据s
    json_data = request.data
    current_app.logger.debug(json_data)
    json_dict = json.loads(json_data)
    mobile = json_dict.get("mobile")
    image_code = json_dict.get("image_code")
    image_code_id = json_dict.get("image_code_id")
    """ 参数初步的校验"""
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数有误')
    """ 判断手机号码是否正确"""
    if not re.match("^1[345789][0-9]{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号码有误')
    """ 判断验证码和redis 对比判断是否正确"""
    try:
        redis_image_id = redis_store.get('imageCode:' + image_code_id)
        current_app.logger.debug(redis_image_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='验证码出错')
    # 从redis中取不出来数据 说明验证码的过期
    current_app.logger.debug(image_code_id)
    if not redis_image_id:
        return jsonify(errno=RET.NODATA, errmsg='验证码已过期')
    if redis_image_id != image_code:
        return jsonify(errno=RET.PARAMERR, errmsg='验证码输入错误')
        """ 发送验证消息"""

    sms_code = "%06d" % random.randint(0, 999999)
    current_app.logger.debug(sms_code)
    ccpr = CCPR()
    result = ccpr.sendTemplateSMS(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], '1')
    if result != 1:
        return jsonify(errno=RET.THIRDERR, errmsg='第三方平台出错')
    # 保存短信信息到redis中
    try:
        redis_store.set('Mobile:' + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存数据库失败')

    return jsonify(errno=RET.OK, errmsg='发送成功')


@api.route('/image_code')
def get_image_code():
    cur_id = request.args.get('cur_id')
    pre_id = request.args.get('pre_id')
    if not cur_id:
        abort(403)

    name, text, image = captcha.generate_captcha()
    current_app.logger.debug(text)
    try:
        redis_store.set('imageCode:' + cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
        if pre_id:
            redis_store.delete('imageCode:' + pre_id)
    except  Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存验证码数据失败！")
    response = make_response(image)
    response.headers["Content-Type"] = "image/jpg"

    return response


