# _*_ coding:utf-8 _*_
""""
create by lu
"""
import datetime
from flask import current_app, jsonify, request, g, session

from Logic import db, constants, redis_store
from Logic.api_1_0 import api
from Logic.models import Area, House, Facility, HouseImage, Order
from Logic.utils import image_storage
from Logic.utils.common import login_required
from Logic.utils.response_code import RET


@api.route("/houses")
def search_houses():
    current_app.logger.debug(request.args)
    aid = request.args.get("aid", "")
    sk = request.args.get("sk", "new")
    p = request.args.get("p", 1)
    sd = request.args.get("sd", "")
    ed = request.args.get("ed", "")

    start_time = None
    end_time = None
    houses = None

    try:
        p = int(p)
        if sd:
            start_time = datetime.datetime.strptime(sd, "%Y-%m-%d")
        if ed:
            end_time = datetime.datetime.strptime(ed, "%Y-%m-%d")

        if start_time and end_time:
            assert start_time < end_time, Exception("结束日期必须大于开始日期")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")
    # 确认缓存里面的数据
    try:
        redis_name = "house_list_%s_%s_%s_%s" % (aid, sk, sd, ed)
        resp = redis_store.hget(redis_name, p)
        if resp:
            return jsonify(error=RET.OK, errmsg="OK", data=eval(resp))
    except Exception as e:
        current_app.logger.error(e)

    try:
        house_query = House.query
        if aid:
            house_query = house_query.filter(House.area_id == aid)
            # 根据时间过滤冲突订单
            conflict_orders = []
            if start_time and end_time:
                conflict_orders = Order.query.filter(end_time > Order.begin_date, start_time < Order.end_date)
            if start_time:
                conflict_orders = Order.query.filter(start_time < Order.end_date)
            if end_time:
                conflict_orders = Order.query.filter(end_time > Order.begin_date)

            if conflict_orders:
                conflict_houses_ids = [order.house_id for order in conflict_orders]
                house_query = house_query.filter(House.id.notin_(conflict_houses_ids))
            if sk == "booking":
                house_query = house_query.order_by(House.order_count.desc())
            elif sk == "price-inc":
                house_query = house_query.order_by(House.price.asc())
            elif sk == "price-des":
                house_query = house_query.order_by(House.price.desc())
            else:
                house_query.order_by(House.create_time.desc())
                # 分页的逻辑
        paginate = house_query.paginate(p, constants.HOUSE_LIST_PAGE_CAPACITY, False)
        # 当前的页面
        houses = paginate.items
        # 总的页数
        total_pages = paginate.pages

    except Exception as e:
        current_app.logger.error(e)

    houses_dict_li = []

    for house in houses:
        houses_dict_li.append(house.to_basic_dict())

    resp = {"houses": houses_dict_li, "total_pages": total_pages}
    # 换成redis里面 根据数据库的事物
    try:
        redis_name = "house_list_%s_%s_%s_%s" % (aid, sk, sd, ed)
        redis_line = redis_store.pipeline()
        redis_line.multi()  # 开启事物
        redis_line.hset(redis_name, p, resp)
        redis_line.expire(redis_name, constants.HOUSE_LIST_REDIS_EXPIRES)
        redis_line.execute()

    except Exception as e:
        current_app.logger.error(e)

    return jsonify(error=RET.OK, errmsg="OK", data=resp)


@api.route("/houses/index")
def get_index_house():
    # 从数据库中查询前五个房屋的信息
    try:
        houses = House.query.order_by(House.create_time.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
    except Exception as e:
        return jsonify(errno=RET.DATAEXIST, errmsg='没有数据')
    houses_li = []
    for house in houses:
        houses_li.append(house.to_basic_dict())

    return jsonify(errno=RET.OK, errmsg='OK', data=houses_li)


@api.route("/houses/<int:house_id>")
def get_house_detail(house_id):
    try:
        house = House.query.get(house_id)
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='数据库查询问题')

    if not house:
        return jsonify(errno=RET.DATAEXIST, errmsg='房屋不存在')

    resp_dict = house.to_full_dict()
    user_id = session.get("user_id", -1)
    # current_app.logger.debug(user_id)
    return jsonify(errno=RET.OK, errmsg='OK', data={"house": resp_dict, "user_id": user_id})


@api.route("/houses/image", methods=["POST"])
@login_required
def upload_hourse_image():
    """
    1.获取到参数，图片，房屋的ID
    2.获取到制定的房屋的id的模型
    3.上传到七牛云
    4.初始化房屋图片的模型
    5.设置图片并且保存到数据库中
    6.返回图片的url链接
    :return:
    """
    # 获取到参数，图片，房屋的ID
    try:
        house_image = request.files.get("house_image").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误1')
    # 2.获取到制定的房屋的id的模型
    house_id = request.form.get("house_id")
    current_app.logger.debug(house_id)
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误2')
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询问题')
    if not house:
        return jsonify(errno=RET.DBERR, errmsg='房屋不存在')

    # 3.上传到七牛云
    try:
        image_url = image_storage.upload_image(house_image)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='第三方错误')

        # 4.初始化房屋图片的模型
    hourse_image = HouseImage()
    hourse_image.house_id = house_id
    hourse_image.url = image_url
    # 5.设置图片并且保存到数据库中
    if not house.index_image_url:
        house.index_image_url = image_url
    try:
        db.session.add(hourse_image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据库存储失败')
    # 6.返回图片的url链接
    whole_url = constants.QINIU_DOMIN_PREFIX + image_url

    return jsonify(errno=RET.OK, errmsg='OK', data={"image_url": whole_url})


@api.route("/houses", methods=["POST"])
@login_required
def get_house_info():
    # //从后台获取到相关的数据
    json_dict = request.json
    title = json_dict.get('title')
    price = json_dict.get('price')
    address = json_dict.get('address')
    area_id = json_dict.get('area_id')
    room_count = json_dict.get('room_count')
    acreage = json_dict.get('acreage')
    unit = json_dict.get('unit')
    capacity = json_dict.get('capacity')
    beds = json_dict.get('beds')
    deposit = json_dict.get('deposit')
    min_days = json_dict.get('min_days')
    max_days = json_dict.get('max_days')

    # 确定数据不能为空
    if not all(
            [title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 对个别的数据进行处理
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
        # 设置数据到模型
    user_id = g.user_id
    house = House()
    house.user_id = user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    facility = json_dict.get('facility')
    if facility:
        facilities = Facility.query.filter(Facility.id.in_(facility)).all()
        house.facilities = facilities

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存房屋信息失败')
    return jsonify(errno=RET.OK, errmsg='OK', data={'house_id': house.id})


@api.route("/area")
def get_areas():
    # 先从缓存中获取数据 如果没有再从数据库里查询
    try:
        area_dict_li = redis_store.get("Area")
        if area_dict_li:
            return jsonify(error=RET.OK, errmsg="ok", data=eval(area_dict_li))
    except Exception as e:
        current_app.logger(e)

    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="数据库查询失败")

    area_dict_li = []

    for area in areas:
        area_dict_li.append(area.to_dict())
    current_app.logger.debug(len(area_dict_li))
    # 缓存到redis里面 方面查询的时候使用
    try:
        redis_store.set("Area", area_dict_li, constants.AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger(e)

    return jsonify(error=RET.OK, errmsg="OK", data=area_dict_li)
