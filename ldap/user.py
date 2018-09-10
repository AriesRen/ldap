#! /env python
# _*_ coding:utf8 _*_
# @author:ren
# @date:2018/7/25.16:52

from flask import Blueprint, jsonify, request, g
from .ldap_tools import search_user
from .ldap_tools import delete_user
from .ldap_tools import add_user
from .ldap_tools import modify_user_password
from .ldap_tools import search_all_user

# 端点蓝图
user_blueprints = Blueprint("user", __name__, url_prefix="/user")

# 查看所有用户
@user_blueprints.route("", methods=['GET'])
def users():
    return jsonify({"code":200,"message":"","data":search_all_user(g.conn)[1]})

# 查看用户
@user_blueprints.route("/<uid>", methods=['GET'])
def user_info(uid):
    try:
        status, data = search_user(g.conn, uid)
        if not status:
            return jsonify({"code": 404, "message": data}), 404
        return jsonify({"code": 200, "message": "success","user": data})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


# 删除用户
@user_blueprints.route("/<uid>", methods=['DELETE'])
def user_delete(uid):
    try:
        status, msg = delete_user(g.conn, uid)
        if status==True:
            return jsonify({'code': 200, 'message': msg}),200
        else:
            return jsonify({"code":404,"message":msg}),404
    except Exception as e:
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
        # 2、添加用户
        status,msg = add_user(g.conn, dict)
        if status:
            user = search_user(g.conn, dict['uid'])[1]
            return jsonify({'code': 201, 'message':msg, "user": user }),201
        else:
            return jsonify({'code':400, "message":msg}),400
    except Exception as e:
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
        res, msg = modify_user_password(conn=g.conn, user=uid, new_password=new_password, old_password=old_password)
        if res:
            return jsonify({'code': 200, 'message': 'modify password success'})
        else:
            return jsonify({'code': 400, 'message': msg})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500
