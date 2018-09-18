#! /env python
# _*_ coding:utf8 _*_
# @author:ren
# @date:2018/7/25.16:52

import json
from flask import Blueprint, jsonify, request, g,current_app
from api.ldap_tools.user import search_user
from api.ldap_tools.user import delete_user
from api.ldap_tools.user import add_user
from api.ldap_tools.user import modify_user_password
from api.ldap_tools.user import search_all_user
from api.ldap_tools.user import search_page_user

# 端点蓝图
user_blueprints = Blueprint("user", __name__, url_prefix="/user")

# 查看所有用户
@user_blueprints.route("", methods=['GET'])
def users():
    current_app.logger.info("查看所有用户")
    return jsonify({"code":200,"message":"","data":search_all_user(g.conn)[1]})

# 查看用户
@user_blueprints.route("/<uid>", methods=['GET'])
def user_info(uid):
    try:
        current_app.logger.info("获取用户信息：{}".format(uid))
        status, data = search_user(g.conn, uid)
        if not status:
            current_app.logger.info("未找到此用户：{}".format(uid))
            return jsonify({"code": 404, "message": data}), 404
        current_app.logger.info("查看用户信息：{}".format(uid))
        return jsonify({"code": 200, "message": "success","user": data})
    except Exception as e:
        current_app.logger.exception(e)
        return jsonify({"code": 500, "message": str(e)}), 500

# # 分页查看用户
# @user_blueprints.route("/<uid>", methods=['GET'])
# def user_info(uid):
#     try:
#         args = json.dumps(request.args)
#         current_app.logger.info(args)
#         statsu, users, total, paged_cookie = search_page_user(conn=g.conn, size=5)
#         return jsonify({"code":200, "data": args, "users": users, "total": total,"paged_cookie":paged_cookie}), 200
#     except Exception as e:
#         return jsonify({"code":500, "message": str(e)}), 500


# 删除用户
@user_blueprints.route("/<uid>", methods=['DELETE'])
def user_delete(uid):
    try:
        current_app.logger.info("删除用户：{}".format(uid))
        status, msg = delete_user(g.conn, uid)
        if status==True:
            current_app.logger.info("删除用户成功：{}".format(uid))
            return jsonify({'code': 200, 'message': msg}),200
        else:
            current_app.logger.info("未找到此用户：{}".format(uid))
            return jsonify({"code":404,"message":msg}),404
    except Exception as e:
        current_app.logger.exception(e)
        return jsonify({"code": 500, "message": str(e)}), 500

# 新增用户
@user_blueprints.route('', methods=['POST'])
def user_add():
    try:
        # 1、判断参数
        for key in ['uid', 'department', 'company', 'password', "sn", "givenName"]:
            if key not in request.json.keys():
                return jsonify({"code": 402, "message": key + " is required"}), 402

        dict = {}
        for key in request.json:
            dict[key] = request.json[key]
        current_app.logger.info("获取参数：{}".format(dict))

        # 2、添加用户
        current_app.logger.info("新增用户：{}".format(dict["uid"]))
        status,msg = add_user(g.conn, dict)
        if status:
            current_app.logger.info("查看用户：{}".format(dict["uid"]))
            user = search_user(g.conn, dict['uid'])[1]
            return jsonify({'code': 201, 'message':msg, "user": user }),201
        else:
            current_app.logger.info("添加用户失败：{}".format(dict["uid"]))
            return jsonify({'code':400, "message":msg}),400
    except Exception as e:
        current_app.logger.exception(e)
        return jsonify({"code": 500, "message": str(e)}), 500

# 修改
@user_blueprints.route('/<uid>', methods=['PUT'])
def user_put(uid):
    try:
        new_password = request.json["new_password"]
        if "old_password" in request.json.keys():
            old_password = request.json["old_password"]
        else:
            old_password = None
        current_app.logger.info("旧密码：{}".format(old_password))
        current_app.logger.info("更新用户{}密码：{}".format(uid, new_password))
        res, msg = modify_user_password(conn=g.conn, user=uid, new_password=new_password, old_password=old_password)
        if res:
            current_app.logger.info("更新用户{}密码成功".format(uid))
            return jsonify({'code': 200, 'message': 'modify password success'})
        else:
            current_app.logger.info("更新用户{}密码失败".format(uid))
            return jsonify({'code': 400, 'message': msg})
    except Exception as e:
        current_app.logger.exception(e)
        return jsonify({"code": 500, "message": str(e)}), 500
