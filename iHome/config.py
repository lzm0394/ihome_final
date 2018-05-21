# _*_ coding:utf-8 _*_
""""
create by lu
"""
import logging

import redis

create_time = '2018/4/27 20:15'


class Config(object):
    SECRET_KEY = 'krjPsIhmbdb+C0vAxpF1R2/TvI4tjvbA1b6FN1EQKhesRj8gPntTYBUZwgw0sugz'
    """mysql配置"""
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1:3306/ihome"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """redis的配置"""
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    """session的配置"""
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 开启签名认证
    SESSION_USE_SIGNER = True
    # 设置缓存只保留一天
    PERMANENT_SESSION_LIFETIME = 86400 * 2


class DevelopmentConfig(Config):
    """开发测试环境的配置"""
    DEBUG = True
    """ 日志等级"""
    LOGGING_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """正式环境的配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1：3306/ihome"
    """ 日志等级"""
    LOGGING_LEVEL = logging.WARN


dev_config = {
    'DevelopmentConfig': DevelopmentConfig,
    'ProductionConfig': ProductionConfig

}
