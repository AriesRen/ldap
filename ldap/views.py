#! /env python
# _*_ coding:utf-8 _*_
# @author:ren
# @date:2018/7/18.11:28

from flask import Blueprint, current_app, request, jsonify, g
from .ldap_tools import *

# 端点蓝图
ldap_blueprints = Blueprint("ldap", __name__, url_prefix="/ldap")


@ldap_blueprints.before_request
def before_request():
    try:
        g.conn = get_conn()
        g.conn.bind()
        g.conn.start_tls()
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


@ldap_blueprints.teardown_request
def teardown_request(exception):
    g.conn.unbind()

# 修改密码
# params： user 用户名; new_password 新密码; old_password 旧密码
@ldap_blueprints.route("/modify_password", methods=['POST'])
def modify_password():
    # 1、判断参数
    for key in ['user', 'new_password']:
        if key not in request.json.keys():
            return jsonify({"code": 402, "message": key + " is required"}), 402

    # 获取参数
    user = request.json['user']
    new_password = request.json['new_password']
    # old_password可以为空
    if "old_password" not in request.json.keys():
        old_password = None
    else:
        old_password = request.json['old_password']

    try:
        conn = g.conn
        user_dn = search_user_dn(conn, user)
        if not user_dn[0]:
            return jsonify({"code": 404, "message": "Not found this user"}), 404
        modify_status = conn.extend.microsoft.modify_password(user=user_dn[1], new_password=new_password,
                                                              old_password=old_password, controls=None)
        if modify_status:
            return jsonify({"code": 200, "message": u"修改成功", "user_dn": user_dn[1], "new_password": new_password,
                            "status": conn.result["description"], "old_password": old_password}), 200
        else:
            return jsonify({"code": 500, "message": u"请检查密码是否符合规则，或者old_password是否正确",
                            "status": conn.result["description"]}), 500
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


# 搜索部门
# params： org: 部门名称
@ldap_blueprints.route("/search_org", methods=['POST'])
def search_org():
    if "org" not in request.json.keys():
        return jsonify({"code": 402, "message": "org is require"}), 402
    else:
        ou = request.json['org']

    try:
        org_dn = search_org_dn(g.conn, ou)
        if not org_dn[0]:
            return jsonify({"code": 404, "message": "Not found this org"}), 404
        return jsonify({"code": 200, "message": "success", "org": ou, "org_dn": org_dn[1]})

    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


# 搜索用户
# params： user: 用户名
@ldap_blueprints.route("/search_user", methods=['POST'])
def search_user():
    if "user" not in request.json.keys():
        return jsonify({"code": 402, "message": "user is require"}), 402
    else:
        user = request.json['user']
    try:
        user_dn = search_user_dn(g.conn, user)
        if not user_dn[0]:
            return jsonify({"code": 404, "message": "Not found this user"}), 404
        return jsonify({"code": 200, "message": "success", "user": user, "user_dn": user_dn[1]})

    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


# 搜索组
# params： user: 用户名
@ldap_blueprints.route("/search_member", methods=['POST'])
def search_member():
    if "member" not in request.json.keys():
        return jsonify({"code": 402, "message": "member is require"}), 402
    else:
        member = request.json['member']
    try:
        user_dn = search_group_dn(g.conn, member)
        if not user_dn[0]:
            return jsonify({"code": 404, "message": "Not found this user"}), 404
        return jsonify({"code": 200, "message": "success", "user": member, "user_dn": user_dn[1]})

    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


# 添加用户
@ldap_blueprints.route("/add_user", methods=['POST'])
def add_user():
    # 1、判断参数
    for key in ['user', 'department', 'company', 'password', "sn", "givenName"]:
        if key not in request.json.keys():
            return jsonify({"code": 402, "message": key + " is required"}), 402

    # 2、获取参数
    company = request.json['company']
    department = request.json['department']
    user = request.json['user']
    password = request.json['password']
    sn = request.json['sn']
    givenName = request.json['givenName']
    # old_password可以为空
    if "member" not in request.json.keys():
        member = None
    else:
        member = request.json['member']

    # 3、添加用户
    try:
        # 1、存在用户 返回409
        if search_user_dn(g.conn, user)[0]:
            return jsonify({"code": 409, "message": u"该用户已存在"}), 409

        # 2、不存在部门，返回404
        if not search_org_dn(g.conn, department):
            return jsonify({"code": 409, "message": u"不存在该部门:" + department}), 409

        # 3、将用户、部门信息转换为dn
        base_dn = current_app.config['BASE_DN']
        user_dn = "CN={},OU={},OU={},{}".format(user, department, company, base_dn)
        # sn:姓 givenName: 名 memberOf:组
        attritubes = {"sn": sn, "givenName": givenName, "sAMAccountName": user, "displayName": sn + givenName,
                      "userPrincipalName": user + "rhg.com",'gidNumber': 0}

        # 4、添加用户，返回201
        res = add_user_dn(g.conn, user_dn=user_dn, password=password, attritubes=attritubes)
        if not res[0]:
            return jsonify(
                {"code": 500, "message": res[2], "user_dn": user_dn, "status": res[1], "opteration": "add user"}), 500
        # 5、将用户添加到组里

        return jsonify({"code": 201, "message": user + u"添加成功", "user_dn": user_dn, "status": "success",
                        "opteration": "add user"}), 201
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500


# 添加用户
@ldap_blueprints.route("/delete_user", methods=['POST'])
def delete_user():
    if "user" not in request.json.keys():
        return jsonify({"code": 402, "message": "user is require"}), 402
    else:
        user = request.json['user']

    try:
        # 1、不存存在用户 返回404
        if not search_user_dn(g.conn, user)[0]:
            return jsonify({"code": 404, "message": u"该用户不存在"}), 404

        # 2、存在用户，删除，返回201
        ret = delete_user_dn(g.conn, search_user_dn(g.conn, user)[1])
        return jsonify({"code": 200, "message": user, "status": ret[1], "opteration": "delete user"})

    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500
