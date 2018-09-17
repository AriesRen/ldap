#! /env python
# _*_ coding:utf8 _*_
# @author:ren
# @date:2018/7/25.16:42

from flask import current_app
from .org import search_org
import json

try:
    import ldap3
except ImportError as e:
    raise e


# 添加用户
def add_user(conn, user=None):
    """
    添加用户
    :param conn:
    :param user:
    :return:
    """
    if user is None:
        raise ValueError("无效参数：{}".format(user))
    if not isinstance(conn, ldap3.Connection):
        raise ValueError("无效参数：{}".format(conn))
    if isinstance(conn, ldap3.Connection) and user is not None:
        # 获取用户所需参数
        uid = user['uid']
        department = user['department']
        company = user['company']
        sn = user['sn']
        givenName = user['givenName']
        password = user['password']
        # 1、判断用户是否存在
        if search_user(conn, uid)[0]:
            return (False, "The user already exists")

        # 2、判断组织是否存在
        if not search_org(conn, department) or not search_org(conn, company):
            return (False, "This organizational {}-{} is not exists".format(company, department))

        # 3、构造所需参数
        user_dn = "cn={},ou={},ou={},".format(uid, department, company) + current_app.config["BASE_DN"]
        attributes = {"sn": sn, "givenName": givenName, "sAMAccountName": uid, "displayName": sn + givenName,
                      "userPrincipalName": uid }
        objectClass = ['top', 'person', 'user', "organizationalPerson"]
        try:
            # 4、添加用户
            a = conn.add(user_dn, attributes=attributes, object_class=objectClass, controls=None)
            # 5、解锁用户
            b = conn.extend.microsoft.unlock_account(user_dn)
            # 6、更改密码
            c = modify_user_password(conn, uid, new_password=password)
            # 7、启动账户
            d = conn.modify(user_dn, changes={"userAccountControl":(ldap3.MODIFY_REPLACE, [512])})
            print(a,b,c,d)
            print(conn.result['result'])
            if a and b and c[0] and d and conn.result['result']==0:
                return (True, conn.result['description'])
            else:
                return (False, conn.result['message'])
        except Exception as e:
            raise e


# 删除用户
def delete_user(conn, user):
    """
    :param conn: ldap3 connection
    :param user dn
    :return:
    """
    if isinstance(conn, ldap3.Connection):
        if not search_user(conn, user)[0]:
            return (False, "Not found this user")
        user_dn = search_user(conn, user)[1]['dn']
        res = conn.delete(user_dn, controls=None)
        return (res, conn.result["description"])


# 搜索用户
def search_user(conn, user):
    """
    :param ldap3 Connection
    :param user uid
    :return a tuble  if user exist return (true, :user dn)
                      if user not exist return (False, None)
    """
    base_dn = current_app.config["BASE_DN"]
    if isinstance(conn, ldap3.Connection):
        search_filter = '(&(|(userPrincipalName={})(samaccountname={})(mail={})(name={}))(objectClass=person))'.format(
            user, user, user, user)
        conn.search(search_base=base_dn, search_filter=search_filter, search_scope=ldap3.SUBTREE,
                    attributes=[ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES], size_limit=1)
        users = json.loads(conn.response_to_json())['entries']
        if len(users) > 0:
            return (True, users[0])
        else:
            return (False, "Not found this user")
    else:
        raise TypeError("conn shoud be a Connection")

# 搜索所有用户
def search_all_user(conn):
    """
    :param conn:
    :return: all user
    """
    if isinstance(conn, ldap3.Connection):
        try:
            search_filter = '(objectClass=person)'
            base_dn = current_app.config["BASE_DN"]
            conn.search(search_base=base_dn, search_filter=search_filter, search_scope=ldap3.SUBTREE,
                    attributes=[ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES])
            users = json.loads(conn.response_to_json())['entries']
            return (True, users)
        except Exception as e:
            raise e

# 分页查询用户
def search_page_user(conn, page, size):
    """
    分页查询用户信息
    :param conn: 连接
    :param page: page页
    :param size: 大小
    :return:
    """
    if isinstance(conn, ldap3.Connection):
        try:
            search_filter = '(objectClass=person)'
            base_dn = current_app.config["BASE_DN"]
            conn.search(search_base=base_dn, search_filter=search_filter, search_scope=ldap3.SUBTREE,
                        attributes=[ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES])
            users = json.loads(conn.response_to_json())['entries']
            return (True, users)
        except Exception as e:
            raise e



# 修改用户密码
def modify_user_password(conn, user, new_password, old_password=None):
    """
    :param conn: ldap3 Connection
    :param user: user uid
    :param new_password: user new password
    :param old_password: user old password
                          -- Con be None that will be reset user password
    :return: a boolen if modify success return true else retrun false
    """
    if isinstance(conn, ldap3.Connection):
        if search_user(conn, user)[0]:
            user_dn = search_user(conn, user)[1]['dn']
            conn.extend.microsoft.modify_password(user=user_dn, new_password=new_password,
                                                           old_password=old_password, controls=None)
            if conn.result['result'] == 0:
                return (True, conn.result['description'])
            else:
                return (False, conn.result['description'])
