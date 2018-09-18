#! /env python
# _*_ coding:utf8 _*_
# @author:ren
# @date:2018/7/18.11:08

import os
import logging
import sys

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
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
    PORT = '5000'

    # 测试服务器
    LDAP_HOST = "192.168.4.111"
    LDAP_BASE_DN = "DC=rhg,DC=com"
    # 管理员账号密码
    LDAP_ADMIN = "RHG\\Administrator"
    LDAP_ADMIN_PWD = "123456789"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        import logging
        from logging.handlers import RotatingFileHandler

        # log formatter
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(pathname)s %(lineno)s %(message)s')

        # info file handler
        file_handler_info = RotatingFileHandler(filename=cls.LOG_PATH_INFO,encoding="utf8",mode="a", maxBytes=cls.LOG_FILE_MAX_BYTES, backupCount=cls.LOG_FILE_BACKUP_COUNT)
        file_handler_info.setFormatter(formatter)
        file_handler_info.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler_info)

        # error file handler
        file_handler_error = RotatingFileHandler(filename=cls.LOG_PATH_ERROR,encoding="utf8",mode="a", maxBytes=cls.LOG_FILE_MAX_BYTES, backupCount=cls.LOG_FILE_BACKUP_COUNT)
        file_handler_error.setFormatter(formatter)
        file_handler_error.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler_error)


class ProdConfig(Config):
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = '5000'

    # 正式服务器
    LDAP_HOST = ""
    LDAP_BASE_DN = ""
    # 管理员账号密码
    LDAP_ADMIN = ""
    LDAP_ADMIN_PWD = ""

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        import logging
        from logging.handlers import RotatingFileHandler

        # log formatter
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(pathname)s %(lineno)s %(message)s')

        # info file handler
        file_handler_info = RotatingFileHandler(filename=cls.LOG_PATH_INFO,encoding="utf8",mode="a", maxBytes=cls.LOG_FILE_MAX_BYTES, backupCount=cls.LOG_FILE_BACKUP_COUNT)
        file_handler_info.setFormatter(formatter)
        file_handler_info.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler_info)

        # error file handler
        file_handler_error = RotatingFileHandler(filename=cls.LOG_PATH_ERROR,encoding="utf8",mode="a", maxBytes=cls.LOG_FILE_MAX_BYTES, backupCount=cls.LOG_FILE_BACKUP_COUNT)
        file_handler_error.setFormatter(formatter)
        file_handler_error.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler_error)


config = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'default': DevConfig
}
