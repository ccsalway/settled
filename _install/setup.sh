#!/usr/bin/env bash

# apt-get install git
# git clone https://github.com/ccsalway/settled.git /opt/settled
# chown -R www-data:www-data /opt/settled
#

add-apt-repository ppa:nginx/stable

apt-get update

apt-get -y install \
    nginx \
    nginx-extras \
    python-pip \
    python-dev \
    libffi-dev \
    libmysqlclient-dev \
    mysql-server \
    mysql-client

pip install uwsgi
pip install bcrypt
pip install mysql
pip install uwsgitop
pip install jinja2

echo <<'EOF' > /etc/environment
DB_HOST="localhost"
DB_USER="root"
DB_PSWD="MySQLPa$$word"
DB_NAME="settled"
EOF

echo <<'EOF' > /etc/nginx/nginx.conf
user www-data;
worker_processes auto;
worker_rlimit_nofile 99999;
pid /run/nginx.pid;

events {
        worker_connections 2048;
}

http {
        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
        keepalive_timeout 65;
        types_hash_max_size 2048;
        server_tokens off;

        client_body_timeout 5s;
        client_header_timeout 5s;

        include /etc/nginx/mime.types;
        default_type application/octet-stream;

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_prefer_server_ciphers on;

        log_format custom '$http_x_forwarded_for ($remote_addr) $time_iso8601 $host "$request" $status $request_length $body_bytes_sent $request_time';
        access_log /var/log/nginx/access.log custom;
        error_log /var/log/nginx/error.log;

        gzip on;
        gzip_disable "msie6";

        include /etc/nginx/conf.d/*.conf;
        include /etc/nginx/sites-enabled/*;
}
EOF

echo <<'EOF' > /etc/nginx/sites-available/default
server {
        listen 80 default_server;
        listen [::]:80 default_server;

        server_name _;

        root /usr/share/nginx/html;
        index index.html index.htm;

        default_type text/plain;

        location / {
                try_files $uri @app;
        }

        location @app {
                proxy_intercept_errors on;
                include uwsgi_params;
                uwsgi_pass 127.0.0.1:3031;
        }

        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
                add_header Access-Control-Allow-Origin * always;
                echo 'Upstream unavailable';
        }
}
EOF

echo <<'EOF' > /etc/sysctl.d/99-local.conf
net.ipv4.ip_local_port_range = 1024 65535
net.nf_conntrack_max = 150000
net.core.somaxconn = 10000
net.ipv4.tcp_fin_timeout = 10
net.ipv4.tcp_tw_recycle = 1
net.ipv4.tcp_tw_reuse = 1
fs.file-max = 100000
EOF

sysctl -p

echo <<'EOF' > /etc/init/website.conf
description "uWSGI Website"

console log

limit nofile 99999 99999

start on runlevel [2345]
stop on runlevel [016]

setuid www-data
setgid www-data

chdir /opt/settled

script
  set -o allexport
  . /etc/environment
  set +o allexport
  exec /usr/local/bin/uwsgi uwsgi.ini
end script
EOF

mysql -uroot -p'MySQLPa$$word' < schema.sql

start website
restart nginx
restart mysql