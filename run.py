#! /env python
# _*_ coding:utf8 _*_
# @author:ren
# @date:2018/7/18.11:09

from flask import Flask, g, current_app, jsonify
from config import config
from api.group import group_blueprints
from api.user import user_blueprints
from api.org import org_blueprints


try:
    import ldap3
except ImportError as e:
    raise e


def create_app(config_name):
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 每次请求重新加载conn
    @app.before_request
    def before_request():
        try:
            host = current_app.config["LDAP_HOST"]
            base_dn = current_app.config["LDAP_BASE_DN"]
            admin = current_app.config['LDAP_ADMIN']
            adminpwd = current_app.config['LDAP_ADMIN_PWD']

            server = ldap3.Server(host=host, get_info=ldap3.ALL)
            g.conn = ldap3.Connection(server=server, user=admin, password=adminpwd, auto_encode=True, auto_escape=True)
            # 连接
            g.conn.bind()
            current_app.logger.info("连接成功：{}".format(g.conn))

            # 开启tls连接
            g.conn.start_tls()
            current_app.logger.info("开启TLS连接：".format(g.conn))
        except Exception as e:
            current_app.logger.exception(e)
            return jsonify({"code": 500, "message": str(e)}), 500

    # 每次请求完毕关闭conn
    @app.teardown_request
    def teardown_request(exception):
        # 关闭连接
        g.conn.unbind()
        current_app.logger.info("关闭连接：".format(g.conn))

    @app.after_request
    def after_request(response):
        # 跨域响应头
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'HEAD,OPTIONS,GET,POST,DELETE,PUT'
        response.headers['Access-Control-Allow-Headers']= "x-requested-with,content-type"
        # json格式
        response.headers['Content-Type'] = 'application/json'
        return response


    # 用户蓝图
    app.register_blueprint(user_blueprints)
    # 组织蓝图
    app.register_blueprint(org_blueprints)
    # 组蓝图
    app.register_blueprint(group_blueprints)

    return app

app = create_app("dev")

if __name__ == '__main__':
    app.logger.info('服务器启动：http://0.0.0.0:5000')
    app.run(host='0.0.0.0',port='5000')
