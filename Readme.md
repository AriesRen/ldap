#LDAP 域管理系统

## 环境及版本
Python版本： Python36
```
click==6.7
Flask==1.0.2
Flask-Script==2.0.6
greenlet==0.4.15
gevent==1.3.6
gunicorn==19.9.0
itsdangerous==0.24
Jinja2==2.10
ldap3==2.5
MarkupSafe==1.0
numpy==1.14.5
pyasn1==0.4.3
python-dateutil==2.7.3
pytz==2018.5
six==1.11.0
Werkzeug==0.14.1
```

## 安装Python环境
```bash
# 安装python34或python36，yum安装即可
yun install python34
# 安装虚拟环境
pip install virtualenv
virtualenv --python=python3 py3
# 激活使用虚拟python环境
source py3/bin/activate
```
## 安装依赖
```bash
pip install -r requirement.txt
```

## 设置域地址及用户名和密码
测试环境修改config文件如下：
```python

class DevConfig(Config):
    DEBUG = True
    # 测试服务器地址
    HOST = "192.168.142.128"
    # 域 名
    BASE_DN = "DC=rhg,DC=com"
    # 管理员账号密码
    ADMIN = "RHG\\Administrator"
    # 管理员密码
    ADMIN_PWD = "!Password"
```

生产环境设置密码修改config文件
```python
class ProdConfig(Config):
    DEBUG = False

    # 正式服务器地址
    HOST = "***.***.***.***"
    # 正式服务器域名
    BASE_DN = "DC=bw,DC=local"
    # 管理员账号密码
    ADMIN = "bw\\**********"
    # 管理员密码
    ADMIN_PWD = "********"
```