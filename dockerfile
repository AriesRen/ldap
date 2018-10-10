FROM nginx:1.13-alpine

# 建立文件夹
RUN mkdir -p  /opt/ldap/ && mkdir -p /etc/nginx/ssl

COPY . /opt/ldap/

# 复制nginx配置文件
COPY ./conf/nginx_ldap.conf /etc/nginx/conf.d/
# 复制ssl文件
COPY ./conf/_.bw30.com.crt /etc/nginx/ssl/_.bw30.com.crt
COPY ./conf/_.bw30.com.key /etc/nginx/ssl/_.bw30.com.key

RUN echo "https://mirrors.aliyun.com/alpine/v3.6/main/" > /etc/apk/repositories\
    && echo "https://mirrors.aliyun.com/alpine/v3.6/community/" >>/etc/apk/repositories\
    && apk update\
    && apk add  --no-cache  python3\
    && apk add  gcc libevent-dev python3-dev musl-dev\
    && pip3 install -i http://mirrors.aliyun.com/pypi/simple/ --no-cache-dir --trusted-host mirrors.aliyun.com  -r /opt/ldap/requirement.txt \
    && nginx -s reload

EXPOSE 15000
CMD ["gunicorn" "--chdir" "/opd/ldap" "-w"  "4"  "-b" "127.0.0.1:9000" "run:app"]