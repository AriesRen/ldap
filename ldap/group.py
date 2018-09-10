#! /env python
# _*_ coding:utf8 _*_
# @author:ren
# @date:2018/7/25.16:53

from flask import Blueprint,jsonify,g,request

from .ldap_tools import search_all_group
from .ldap_tools import search_group
from .ldap_tools import add_user_to_group
from .ldap_tools import remove_user_from_group
from .ldap_tools import delete_group
from .ldap_tools import add_group


# 端点蓝图
group_blueprints = Blueprint("group", __name__, url_prefix="/group")

# 新增组
@group_blueprints.route('', methods=['POST'])
def group_add():
    try:
        # 1、判断参数
        for key in [ 'department', 'company',"group"]:
            if key not in request.json.keys():
                return jsonify({"code": 402, "message": key + " is required"}), 402

        department = request.json['department']
        company = request.json['company']
        group = request.json['group']
        # 2、添加用户组
        status,msg = add_group(conn=g.conn, group=group,department=department,company=company)
        if status:
            group = search_group(conn=g.conn, group=group)[1]
            return jsonify({'code': 201, 'message':msg, "group": group }),201
        else:
            return jsonify({'code':400, "message":msg}),400
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

# 删除组
@group_blueprints.route('/<group>', methods=['DELETE'])
def group_delete(group):
    try:
        status, msg = delete_group(g.conn, group)
        if status==True:
            return jsonify({'code': 200, 'message': msg}),200
        else:
            return jsonify({"code":404,"message":msg}),404
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

# 向组内添加删除成员
@group_blueprints.route('/<group>', methods=['PUT'])
def group_put(group):
    # 用type来区分添加删除
    # type = add  添加
    # type = remove 删除
    try:
        # 1、判断参数
        for key in ['type', 'uid']:
            if key not in request.json.keys():
                return jsonify({"code": 402, "message": key + " is required"}), 402

        type = request.json['type']
        uid = request.json['uid']
        # 2、如果type为add
        if type == "add":
            status, msg = add_user_to_group(g.conn, uid=uid, group=group)
            if status:
                group = search_group(g.conn, group)
                return jsonify({"code": 200, "message": msg, "type":type ,"group": group}), 200
            else:
                return jsonify({"code": 400, "message": msg, "type":type}),400
        if type == "remove":
            status, msg = remove_user_from_group(g.conn, uid=uid, group=group)
            if status:
                group = search_group(g.conn, group)
                return jsonify({"code": 200, "message": msg, "type":type, "group":group}), 200
            else:
                return jsonify({"code": 400, "message": msg, "type":type}), 400
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

# 查看所有组
@group_blueprints.route('', methods=['GET'])
def groups():
    return jsonify({'code': 200, 'message': '',"data":search_all_group(g.conn)})

# 查看用户组
@group_blueprints.route("/<group>", methods=['GET'])
def group_info(group):
    try:
        status, data = search_group(g.conn, group)
        if not status:
            return jsonify({"code": 404, "message": data}), 404
        return jsonify({"code": 200, "message": "success","group": data})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500
