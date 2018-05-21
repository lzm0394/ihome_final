# _*_ coding:utf-8 _*_
""""
create by lu
"""
import logging
from logging.handlers import RotatingFileHandler

import redis
from flask_wtf import CSRFProtect
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

from Logic.utils.common import RegexConverter
from Logic.web_html import html_hand
from config import dev_config, Config

create_time = '2018/4/27 20:19'

db = SQLAlchemy()

redis_store = None


def setup_logging(level):
    # 设置日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def creat_app(dev_config_name):
    setup_logging(dev_config[dev_config_name].LOGGING_LEVEL)
    app = Flask(__name__)
    app.config.from_object(dev_config[dev_config_name])
    """mysql的创建"""
    db.init_app(app)
    """redis的创建"""
    global redis_store
    redis_store = redis.StrictRedis(host=dev_config[dev_config_name].REDIS_HOST,
                                    port=dev_config[dev_config_name].REDIS_PORT)
    """CSRF开启"""
    CSRFProtect(app)
    Session(app)
    app.url_map.converters['re'] = RegexConverter

    from Logic.api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/v1.0')
    app.register_blueprint(html_hand)

    print app.url_map

    return app
