# -*- coding: utf-8 -*-
"""
fabfile.py
deploy configuration for fabric
---
Written by Yangwook Ryoo, 2017
MIT License: see LICENSE in the root directory of this source tree.
"""
from fabric.api import *
from fabric.operations import get, put
import StringIO
import os

env.hosts = ['gp2.ryoo.kr']
env.user = "ywryoo"

VHOST = 'gp2.ryoo.kr'
APPS_DIR = '/www'
APP_ROOT = '{}/{}'.format(APPS_DIR, VHOST.replace('.', '_'))
VENV_ROOT = '{}/venv/bin'.format(APP_ROOT)
MODULE = 'gp2'
STATIC = '{}/static'.format(APP_ROOT)
REPO = 'https://github.com/ywryoo/GP2.git'


SUPERVISOR_TEMPLATE = '''
[program:{module}]
command={vroot}/gunicorn app:app -b unix:/tmp/gunicorn.sock -w 2
directory={root}
user=nobody
autostart=true
autorestart=true
redirect_stderr=true
'''
SUPERVISOR_DIR = '/etc/supervisor/conf.d/'
NGINX_DIR = '/etc/nginx/sites-'
NGINX_TEMPLATE = '''
 upstream app_server {{
    # fail_timeout=0 means we always retry an upstream even if it failed
    # to return a good HTTP response

    # for UNIX domain socket setups
    server unix:/tmp/gunicorn.sock fail_timeout=0;

    # for a TCP configuration
    # server 192.168.0.7:8000 fail_timeout=0;
  }}

  server {{
    # use 'listen 80 deferred;' for Linux
    # use 'listen 80 accept_filter=httpready;' for FreeBSD
    listen 80 deferred;
    client_max_body_size 4G;
    listen 443 http2 ssl;
    # set the correct host(s) for your site
    server_name {host};

    keepalive_timeout 5;
        ssl_certificate /etc/letsencrypt/live/{host}/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/{host}/privkey.pem;
        ssl_dhparam /etc/ssl/certs/dhparam.pem;

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_prefer_server_ciphers on;
        ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
        ssl_ecdh_curve secp384r1;
        ssl_session_cache shared:SSL:10m;
#       ssl_session_tickets off;
        ssl_stapling on;
        ssl_stapling_verify on;
        resolver 8.8.8.8 8.8.4.4 valid=300s;
        resolver_timeout 5s;
    add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
    # path for static files

    # this should be automatically appended
    # for each static directory of modules; until then, we just use flask
    # to handle static files
    # location /static/ {{
    #   alias {static}/;
    #   autoindex off;
    # }}

    location ~ /.well-known/ {{
        root /var/www/html;
        allow all;
    }}

    location / {{
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      # enable this if and only if you use HTTPS
      proxy_set_header X-Forwarded-Proto https;
      proxy_set_header Host $http_host;
      proxy_set_header X-real-IP $remote_addr;
      proxy_set_header X-NginX-Proxy true;
      # we don't want nginx trying to do something clever with
      # redirects, we set the Host: header above already.
      proxy_redirect off;
      proxy_buffering off;
      proxy_pass http://app_server;
    }}

    error_page 500 502 503 504 /500.html;
    # location = /500.html {{
    #   alias {static};
    # }}
  }}
'''


def _make_supervisor_conf():
    template = StringIO.StringIO()
    template.write(SUPERVISOR_TEMPLATE
                   .format(vroot=VENV_ROOT, root=APP_ROOT, module=MODULE))
    put(template,
        '{supervisor_dir}{vhost}.conf'
        .format(supervisor_dir=SUPERVISOR_DIR, vhost=VHOST),
        use_sudo=True)
    template.close()


def _make_vhost():
    ngi_avail = '{nginx}available/{vhost}'.format(nginx=NGINX_DIR, vhost=VHOST)
    ngi_enabl = '{nginx}enabled/{vhost}'.format(nginx=NGINX_DIR, vhost=VHOST)
    template = StringIO.StringIO()
    template.write(NGINX_TEMPLATE.format(host=VHOST, static=STATIC))
    put(template,
        ngi_avail, use_sudo=True)
    sudo('ln -s {src} {dest}'.format(src=ngi_avail, dest=ngi_enabl))
    template.close()


def _clone_repo():
    with cd(APPS_DIR):
        run('git clone --recursive {repo} {to}'
            .format(repo=REPO, to=APP_ROOT))


def _install_venv():
    with cd(APP_ROOT):
        run('virtualenv venv')


def _install_dep():
    with cd(APP_ROOT):
        run('{}/pip install -e .'.format(VENV_ROOT))


def _update_repo():
    with cd(APP_ROOT):
        run('git pull && git submodule update --recursive --remote')


def _reload_webserver():
    sudo("systemctl reload nginx")


def _reload_supervisor():
    sudo('supervisorctl update')


def _start_app():
    sudo('supervisorctl start {}'.format(MODULE))


def _reload_app(touch=False):
    if touch:
        with cd(APP_ROOT):
            run('touch app.wsgi')
    else:
        sudo('supervisorctl restart {}'.format(MODULE))


def init_deploy():
    _clone_repo()
    _install_venv()
    _install_dep()
    _make_vhost()
    _make_supervisor_conf()
    _reload_webserver()
    _reload_supervisor()
    _start_app()


def deploy():
    _update_repo()
    _install_dep()
    _reload_app()
