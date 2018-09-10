#! /env python
# _*_ coding:utf8 _*_
# @author:ren
# @date:2018/7/18.11:08


class Config():
    PORT = 9000

class DevConfig(Config):
    DEBUG = True

    # 测试服务器
    HOST =  "192.168.142.128"
    BASE_DN = "DC=rhg,DC=com"
    # 管理员账号密码
    ADMIN = "RHG\\Administrator"
    ADMIN_PWD = "!Password"

class ProdConfig(Config):
    DEBUG = False

    # 正式服务器
    HOST =  "172.16.0.3"
    BASE_DN = "DC=bw,DC=local"
    # 管理员账号密码
    ADMIN = "bw\\administrator"
    ADMIN_PWD = "qaz.1234"