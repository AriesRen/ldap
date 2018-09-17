#! /env python
# _*_ coding:utf8 _*_
# @author:ren
# @date:2018/7/18.11:08

import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    PORT = 9000
    # Logger
    LOG_PATH = os.path.join(basedir, 'logs')
    LOG_PATH_ERROR = os.path.join(LOG_PATH, 'error.log')
    LOG_PATH_INFO = os.path.join(LOG_PATH, 'info.log')
    LOG_PATH_DEBUG = os.path.join(LOG_PATH, 'debug.log')
    LOG_FILE_MAX_BYTES = 100 * 1024 * 1024
    LOG_FILE_BACKUP_COUNT = 10

    @staticmethod
    def init_app(app):
        pass



class DevConfig(Config):
    DEBUG = True

    # 测试服务器
    HOST = "192.168.142.128"
    BASE_DN = "DC=rhg,DC=com"
    # 管理员账号密码
    ADMIN = "RHG\\Administrator"
    ADMIN_PWD = "!Password"


class ProdConfig(Config):
    DEBUG = False

    # 正式服务器
    HOST = "172.16.0.3"
    BASE_DN = "DC=bw,DC=local"
    # 管理员账号密码
    ADMIN = "bw\\administrator"
    ADMIN_PWD = "qaz.1234"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        import logging
        from logging.handlers import RotatingFileHandler

        # log formatter
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(pathname)s %(lineno)s %(message)s')

        # info file handler
        file_handler_info = RotatingFileHandler(filename=cls.LOG_PATH_INFO,encoding="utf8",mode="a")
        file_handler_info.setFormatter(formatter)
        file_handler_info.setLevel(logging.INFO)
        app.logger.addHandler(file_handler_info)

        # error file handler
        file_handler_error = RotatingFileHandler(filename=cls.LOG_PATH_ERROR,encoding="utf8",mode="a")
        file_handler_error.setFormatter(formatter)
        file_handler_error.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler_error)


config = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'default': DevConfig
}
