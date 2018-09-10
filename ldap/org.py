#! /env python
# _*_ coding:utf8 _*_
# @author:ren
# @date:2018/7/25.16:53

from flask import Blueprint,jsonify, g, request
from .ldap_tools import search_org
from .ldap_tools import search_all_org
from .ldap_tools import add_org

# 端点蓝图
org_blueprints = Blueprint("org", __name__, url_prefix="/org")


# 新增部门
@org_blueprints.route('', methods=['POST'])
def org_add():
    try:
        # 1、判断参数
        for key in [ 'department', 'company']:
            if key not in request.json.keys():
                return jsonify({"code": 402, "message": key + " is required"}), 402

        department = request.json['department']
        company = request.json['company']
        # 2、添加用户
        status,msg = add_org(g.conn, department, company)
        if status:
            org = search_org(g.conn, department)[1]
            return jsonify({'code': 201, 'message':msg, "org": org }),201
        else:
            return jsonify({'code':400, "message":msg}),400
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

# 查看所有部门
@org_blueprints.route("", methods=['GET'])
def orgs():
    return jsonify({"code":200,"message":"","data":search_all_org(g.conn)[1]})

# 删除部门
@org_blueprints.route('/<org>', methods=['DELETE'])
def org_delete(org):
    return jsonify({'code': 500, 'message': 'not this method'})

# 查看部门
@org_blueprints.route('/<org>', methods=['GET'])
def org_info(org):
    try:
        status, data = search_org(g.conn, org)
        if not status:
            return jsonify({"code": 404, "message": data}), 404
        return jsonify({"code": 200, "message": "success","org": data})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500