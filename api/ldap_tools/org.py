#! /env python
# _*_ coding:utf8 _*_
# @author:ren
# @date:2018/7/25.16:45


from flask import current_app
import json
try:
    import ldap3
except ImportError as e:
    raise e


# 搜索部门
def search_org(conn, ou=None):
    """
    :param ldap3 Connection
    :param orginazation  name
    :return a tuble  -- if orginazation exist return (true, :org dn)
                      -- if orginazation not exist return (False, None)
    搜索部门组织，存在返回（Ture，org dn)
    """
    base_dn = current_app.config["LDAP_BASE_DN"]
    if isinstance(conn, ldap3.Connection):
        search_filter = '(&(|(name={})(ou={}))(objectClass=OrganizationalUnit))'.format(ou, ou)
        conn.search(search_base=base_dn, search_filter=search_filter, search_scope=ldap3.SUBTREE,
                    attributes=[ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES])

        orgs = json.loads(conn.response_to_json())['entries']
        if len(orgs) > 0:
            return (True, orgs[0])
        else:
            return (False, "Not found this org")
    else:
        raise TypeError("Conn shoud be a ldap3 Connection")


# 搜索所有部门
def search_all_org(conn):
    """
    :param conn:
    :return: all org
    """
    if isinstance(conn, ldap3.Connection):
        try:
            search_filter = '(objectClass=OrganizationalUnit)'
            base_dn = current_app.config["LDAP_BASE_DN"]
            conn.search(search_base=base_dn, search_filter=search_filter, search_scope=ldap3.SUBTREE,
                    attributes=[ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES])
            orgs = json.loads(conn.response_to_json())['entries']
            return (True, orgs)
        except Exception as e:
            raise e

# 新增部门
def add_org(conn, department, company):
    """
    :param conn:
    :param department:
    :param company:
    :return:
    """
    if isinstance(conn, ldap3.Connection):
        try:
            # 1、检查部门是否存在
            if search_org(conn, department)[0]:
                return (False, "The org already exists")
            # 2、新增部门
            objectClass= ["top","organizationalUnit" ]
            org_dn = "ou={},ou={},".format(department, company) + current_app.config["LDAP_BASE_DN"]
            attributes = {"name": department}

            res = conn.add(dn=org_dn,object_class=objectClass,attributes=attributes,controls=None)
            if res:
                return (True, conn.result['description'])
            else:
                return (False, conn.result['description'])
        except Exception as e:
            raise e


# 删除部门
# 删除子用户、子部门。。。
def delete_org(conn, org):
    pass