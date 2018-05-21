# _*_ coding:utf-8 _*_
""""
create by lu
"""
import datetime
from flask import request, jsonify, current_app, g

from Logic import constants, db
from Logic.api_1_0 import api
from Logic.models import House, Order
from Logic.utils.common import login_required
from Logic.utils.response_code import RET


@api.route("/orders/<order_id>/comment", methods=["POST"])
@login_required
def set_order_comment(order_id):
    """
    设置订单的评论
    1.接受参数订单的评论数据 校验参数
    2.通过order_id查询出制定的ID
    3.更新订单信息
    4.保存数据库
    5.返回数据
    :param order_id:
    :return:
    """
    comment = request.json.get("comment")
    if not comment:
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
        # 2.通过order_id查询出制定的ID
    try:
        order = Order.query.filter(Order.id == order_id, Order.status == "WAIT_COMMENT",
                                   Order.user_id == g.user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="数据库查询错误")
    if not order:
        return jsonify(error=RET.DBERR, errmsg="未查出对应id的订单")

    order.status = "COMPLETE"
    order.comment = comment
    # 4.保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error=RET.DBERR, errmsg="数据库存储错误")
    return jsonify(error=RET.OK, errmsg="ok")


@api.route("/orders/<order_id>", methods=["PUT"])
@login_required
def get_order_status(order_id):
    """
    设置订单的状态
    1.根据order_id找到对应的订单
    2.判断当前的登录用户是否是该订单对应的房东
    3.修改订单状态
    4.保存到数据库
    5.返回相应的数据
    :return:
    """
    action = request.args.get("action")

    if action not in ("accept", "reject"):
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")

    # 1.根据order_id找到对应的订单
    try:
        order = Order.query.filter(Order.id == order_id, Order.status == "WAIT_ACCEPT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="查询数据错误")
    if not order:
        return jsonify(error=RET.NODATA, errmsg="订单不存在")

    # 2.判断当前的登录用户是否是该订单对应的房东
    user_id = g.user_id

    landlord_id = order.house.user_id
    if user_id != landlord_id:
        return jsonify(error=RET.ROLEERR, errmsg="不允许修改订单状态")

    # 3.修改订单状态
    if action == "accept":
        order.status = "WAIT_COMMENT"
    else:
        order.status = "REJECTED"
        reason = request.json.get("reason")
        if not reason:
            return jsonify(error=RET.PARAMERR, errmsg="请输入拒单原因")
        order.comment = reason
    # 4.保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error=RET.DBERR, errmsg="数据库存储错误")
    return jsonify(error=RET.OK, errmsg="ok")


@api.route("/orders")
@login_required
def order_list():
    """
    获取当前登陆账户的所有的订单
    :return:
    """
    user_id = g.user_id
    role = request.args.get("role")
    if not role:
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    if role not in ("landlord", "custom"):
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")

    try:
        if role == "landlord":
            houses = House.query.filter(House.user_id == user_id).all()
            house_id = [house.id for house in houses]
            orders = Order.query.filter(Order.user_id.in_(house_id)).all()
        elif role == "custom":
            orders = Order.query.filter(Order.user_id == user_id).all()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="没有查询到数据")
    order_list_dict = []

    for order in orders:
        order_list_dict.append(order.to_dict())

    return jsonify(error=RET.OK, errmsg="OK", data=order_list_dict)


@api.route("/orders", methods=["POST"])
@login_required
def creat_order():
    """
    1.获取参数 房屋的ID  入住的开始时间和结束时间
    2.判断校验参数
    3.判断当前的房屋是否在这个时间段内被预定
    4.创建订单模型 并且设置相关的数据
    5.返回相应
    :return:
    """

    # 1.获取参数 房屋的ID  入住的开始时间和结束时间
    resp_data = request.json
    house_id = resp_data.get("house_id")
    start_data = resp_data.get("start_data")
    end_data = resp_data.get("end_data")
    # 2.判断校验参数
    if not all([house_id, start_data, end_data]):
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    try:
        start_time = datetime.datetime.strptime(start_data, "%Y-%m-%d")
        end_time = datetime.datetime.strptime(end_data, "%Y-%m-%d")

        if start_time and end_time:
            assert start_time < end_time, Exception("结束日期必须大于开始日期")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="没有查询到改数据")
    if not house:
        return jsonify(error=RET.DBERR, errmsg="没有查询到数据")

    # 3.判断当前的房屋是否在这个时间段内被预定
    try:
        conflict_orders = Order.query.filter(end_time > Order.begin_date, start_time < Order.end_date,
                                             Order.house_id == house_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="读取数据出错")
    if conflict_orders:
        return jsonify(error=RET.DBERR, errmsg="当前房屋被预定")

        # 4.创建订单模型 并且设置相关的数据
    order = Order()
    days = (end_time - start_time).days
    order.user_id = g.user_id
    order.house_id = house_id
    order.begin_date = start_time
    order.end_date = end_time
    order.days = days
    order.house_price = house.price
    order.amount = days * house.price

    house.order_count += 1
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error=RET.DBERR, errmsg="订单保存失败")
    # 5.返回相应
    return jsonify(error=RET.OK, errmsg="OK")
