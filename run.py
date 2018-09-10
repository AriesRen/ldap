#! /env python
# _*_ coding:utf8 _*_
# @author:ren
# @date:2018/7/18.11:09

from flask import Flask, g, current_app, jsonify
from config import Config,DevConfig,ProdConfig
from ldap.group import group_blueprints
from ldap.user import user_blueprints
from ldap.org import org_blueprints

try:
    import ldap3
except ImportError as e:
    raise e


def create_app(object=ProdConfig):
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(object)

    # 每次请求重新加载conn
    @app.before_request
    def before_request():
        try:
            host = current_app.config["HOST"]
            base_dn = current_app.config["BASE_DN"]
            admin = current_app.config['ADMIN']
            adminpwd = current_app.config['ADMIN_PWD']

            server = ldap3.Server(host=host, get_info=ldap3.ALL)
            g.conn = ldap3.Connection(server=server, user=admin, password=adminpwd)
            g.conn.bind()
            g.conn.start_tls()
        except Exception as e:
            return jsonify({"code": 500, "message": str(e)}), 500

    # 每次请求完毕关闭conn
    @app.teardown_request
    def teardown_request(exception):
        g.conn.unbind()

    @app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Content-Type'] = 'application/json'
        return response


    # 用户蓝图
    app.register_blueprint(user_blueprints)
    # 组织蓝图
    app.register_blueprint(org_blueprints)
    # 组蓝图
    app.register_blueprint(group_blueprints)

    return app

app = create_app()

# if __name__ == '__main__':
#    print (app.url_map)
#    app.run()
