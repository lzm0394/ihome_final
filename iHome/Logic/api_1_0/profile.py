# _*_ coding:utf-8 _*_
""""
create by lu
"""
from flask import session, current_app, jsonify, request, g

from Logic import constants, db
from Logic.api_1_0 import api
from Logic.models import User, House
from Logic.utils.common import login_required
from Logic.utils.image_storage import upload_image
from Logic.utils.response_code import RET


@api.route("/user/houses")
@login_required
def get_user_houses():
    """获取当前id下的所有的房屋信息"""
    try:
        houses = House.query.filter(House.user_id == g.user_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="没有查询到数据")
    house_dict_li = []
    for house in houses:
        house_dict_li.append(house.to_basic_dict())
    return jsonify(errno=RET.OK, errmsg="OK", data=house_dict_li)


@api.route("/user/auth")
@login_required
def get_user_auth():
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="没有查询到数据")
    if not all([user.real_name, user.id_card]):
        return jsonify(errno=RET.DATAEXIST, errmsg="没有查询到数据")
    data_dict = {
        "real_name": user.real_name,
        "id_card": user.id_card
    }

    return jsonify(errno=RET.OK, errmsg="OK", data=data_dict)


@api.route("/user/auth", methods=["POST"])
@login_required
def set_user_auth():
    # 获取后台传递过来的数据
    my_data = request.json
    real_name = my_data.get("real_name")
    id_card = my_data.get("id_card")
    if not all([real_name, id_card]):
        return jsonify(errno=RET.OK, errmsg="OK")
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="没有查询到数据")
    # 更新数据库
    user.real_name = real_name
    user.id_card = id_card
    if not user:
        return jsonify(errno=RET.DBERR, errmsg="用户不存在")
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="存储失败")

    return jsonify(errno=RET.OK, errmsg="OK")


@api.route("/user/name", methods=["POST"])
@login_required
def upload_user_name():
    user_name = request.json.get("name")
    if not user_name:
        return jsonify(errno=RET.PARAMERR, errmsg="数据不能为空")
        # 确保当前是处于登录状态 从缓存里获取相关信息
        # user_id = session.get("user_id")
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询问题")
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")
    # 更新数据库的内容 之后从新存储
    user.name = user_name
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据库失败")
    # 更新session的内容
    session["name"] = user.name
    # 返回响应
    return jsonify(errno=RET.OK, errmsg="保存数据成功")


@api.route("/user/avatar", methods=["POST"])
@login_required
def upload_avatar():
    """
    1.从后台获取图片文件
    2.上传本地图片到七牛云
    3.上传完成后保存到本地和数据库
    4.把上传完成后获得的链接填写到前端
    """
    try:
        avatar_data = request.files.get("avatar").read()
        print "shuju" + avatar_data
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="读取文件失败")
    # 2上传七牛云盘
    try:
        url_link = upload_image(avatar_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传文件失败")
    # 3.上传完成后保存到本地和数据库
    # user_id = session.get("user_id")
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")
    if not user:
        return jsonify(errno=RET.DBERR, errmsg="用户不存在")
    user.avatar_url = url_link
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    qiniu_url = constants.QINIU_DOMIN_PREFIX + url_link
    return jsonify(errno=RET.OK, errmsg="上传数据成功", data=qiniu_url)


@api.route("/user")
@login_required
def get_user_info():
    """"
    1.判断是否登陆
    2.获取当前登陆用户的user_id
    3.根据user_id查询出用户的信息
    4.组织数据进行返回
    """
    # user_id = session.get("user_id")
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="查询不到数据")
    # 4.组织数据进行返回
    # resp = {
    #     "name": user.name,
    #     "avartar_url": user.avatar_url,
    #     "user_id": user.id
    # }
    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())
