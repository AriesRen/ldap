#! /env python
# _*_ coding:utf8 _*_
# @author:ren
# @date:2018/7/25.16:47

from flask import current_app
import json
from .user import search_user
from .org import search_org

try:
    import ldap3
except ImportError as e:
    raise e


# 搜索组
def search_group(conn, group):
    """
    :param conn ldap3 Connection
    :param group: str group name
    :return a tuble  -- if group exist return (true, :group dn, :member list)
                      -- if group not exist return (False, None, None)
    搜索组，存在返回组成员列表（Ture，group_dn, [members list:])
    """
    base_dn = current_app.config["LDAP_BASE_DN"]
    if isinstance(conn, ldap3.Connection):
        search_filter = '(&(|(name={})(cn={}))(objectClass=group))'.format(group, group)
        conn.search(search_base=base_dn, search_filter=search_filter, search_scope=ldap3.SUBTREE,
                    attributes=[ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES], size_limit=1)

        groups = json.loads(conn.response_to_json())['entries']
        if len(groups) > 0:
            return (True, groups[0])
        else:
            return (False, "Not found this group")
    else:
        raise TypeError("conn shoud be a Connection")


# 搜索所有用户组
def search_all_group(conn):
    base_dn = current_app.config["LDAP_BASE_DN"]
    if isinstance(conn, ldap3.Connection):
        search_filter = '(objectClass=group)'
        conn.search(search_base=base_dn, search_filter=search_filter, search_scope=ldap3.SUBTREE,
                    attributes=[ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES])
        groups = json.loads(conn.response_to_json())['entries']
        return (True, groups)
    else:
        raise TypeError("conn shoud be a Connection")


# 新增组
def add_group(conn, group, department, company):
    """
    :param conn:
    :param group:
    :param department:
    :param company:
    :return:
    """
    if isinstance(conn, ldap3.Connection):
        try:
            # 1、检查部门是否存在
            if not search_org(conn, department)[0]:
                return (False, "The org not exists")
            # 2、检查组是否存在
            if search_group(conn, group)[0]:
                return (False, "The group already exists")
            # 3、新增用户组
            objectClass= ["top","group" ]
            group_dn = "cn={},ou={},ou={},".format(group ,department, company) + current_app.config["LDAP_BASE_DN"]
            attributes = {"name": group,"sAMAccountName":group}

            res = conn.add(dn=group_dn,object_class=objectClass,attributes=attributes,controls=None)
            if res:
                return (True, conn.result['description'])
            else:
                return (False, conn.result['description'])
        except Exception as e:
            raise e



# 添加成员
def add_user_to_group(conn, uid, group):
    """
    :param conn:
    :param uid
    :param group:
    :return:
    """
    if isinstance(conn, ldap3.Connection):
        try:
            # 判断成员是否存在
            if not search_user(conn, uid)[0]:
                return (False, "The member is not exists")

            # 判断group是否存在
            if not search_group(conn, group)[0]:
                return (False, "The group is not exists")

            members_dn = search_user(conn, uid)[1]['dn']
            groups_dn = search_group(conn, group)[1]['dn']
            print(search_group(conn, group)[1]['attributes'])

            # 判断组中是否有此成员
            if "member" in search_group(conn, group)[1]['attributes']:
                if members_dn in search_group(conn, group)[1]['attributes']['member']:
                    return (False, "The member is already in the group")
            conn.extend.microsoft.add_members_to_groups(members=members_dn, groups=groups_dn)

            if conn.result['result']==0:
                return (True, conn.result['description'])
            else:
                return (False, conn.result['description'])
        except Exception as e:
            raise e


# 删除成员
def remove_user_from_group(conn, uid, group):
    """
    :param conn:
    :param uid
    :param group:
    :return:
    """
    if isinstance(conn, ldap3.Connection):
        try:
            # 判断成员是否存在
            if not search_user(conn, uid)[0]:
                return (False, "The member is not exists")
            # 判断group是否存在
            if not search_group(conn, group)[0]:
                return (False, "The group is not exists")
            members_dn = search_user(conn, uid)[1]['dn']
            groups_dn = search_group(conn, group)[1]['dn']
            # 判断组中是否有此成员
            if "member" in search_group(conn, group)[1]['attributes']:
                if members_dn not in search_group(conn, group)[1]['attributes']['member']:
                    return (False, "The member not exists in the group")
            conn.extend.microsoft.remove_members_from_groups(members=members_dn, groups=groups_dn)

            if conn.result['result']==0:
                return (True, conn.result['description'])
            else:
                return (False, conn.result['description'])
        except Exception as e:
            raise e


# 删除组
def delete_group(conn, group):
    if isinstance(conn, ldap3.Connection):
        if not search_group(conn, group)[0]:
            return (False, "Not found this user")
        group_dn = search_group(conn, group)[1]['dn']
        res = conn.delete(group_dn, controls=None)
        return (res, conn.result["description"])

