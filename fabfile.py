# -*- coding: utf-8 -*-
"""
fabfile.py
deploy configuration for fabric
---
Written by Yangwook Ryoo, 2017
MIT License: see LICENSE at root directory
"""
from fabric.api import *
from fabric.operations import get, put

env.hosts = ['gp2.ryoo.kr']
env.user = "ywryoo"

VHOST = 'gp2.ryoo.kr'
APPS_DIR = '/www'
APP_ROOT = '%s/%s' % (APPS_DIR, VHOST.replace('.', '_'))
VENV_ROOT = '%s/venv/bin' % (APP_ROOT)
MODULE = 'gp2-core'

SUPERVISOR_TEMPLATE = '''
[program:gunicorn]
command={vroot}/gunicorn {module}:app -c {root}/gunicorn.conf.py
directory={root}
user=nobody
autostart=true
autorestart=true
redirect_stderr=true
'''
SUPERVISOR_DIR = '/etc/supervisor/conf.d/'

REPO = 'https://github.com/ywryoo/GP2.git'
STATIC = 'static'

NGINX_DIR = '/etc/nginx/sites-'
NGINX_TEMPLATE = '''
  upstream app_server {
    # fail_timeout=0 means we always retry an upstream even if it failed
    # to return a good HTTP response

    # for UNIX domain socket setups
    server unix:/tmp/gunicorn.sock fail_timeout=0;

    # for a TCP configuration
    # server 192.168.0.7:8000 fail_timeout=0;
  }

  server {
    # if no Host match, close the connection to prevent host spoofing
    listen 80 default_server;
    return 444;
  }

  server {
    # use 'listen 80 deferred;' for Linux
    # use 'listen 80 accept_filter=httpready;' for FreeBSD
    listen 80 deferred;
    client_max_body_size 4G;

    # set the correct host(s) for your site
    server_name {host};

    keepalive_timeout 5;

    # path for static files
    root {static};

    location / {
      # checks for static file, if not found proxy to app
      try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      # enable this if and only if you use HTTPS
      # proxy_set_header X-Forwarded-Proto https;
      proxy_set_header Host $http_host;
      # we don't want nginx trying to do something clever with
      # redirects, we set the Host: header above already.
      proxy_redirect off;
      proxy_pass http://app_server;
    }

    error_page 500 502 503 504 /500.html;
    location = /500.html {
      root {static};
    }
  }
'''


def _render_template(string, context):
    return Template(string).render(context)


def _make_supervisor_conf():
    template = StringIO.StringIO()
    get('%sflaskapp.tpl' % SUPERVISOR_DIR, template)
    interpolated = StringIO.StringIO()
    interpolated.write(_render_template(template.getvalue(), {
        'domain': VHOST,
        'root': APP_ROOT,
        'module': MODULE
    }))
    put(interpolated, '%(supervisor_dir)s%(vhost)s.conf' %
        {'supervisor_dir': SUPERVISOR_DIR, 'vhost': VHOST},
        use_sudo=True)


def _make_vhost():
    template = StringIO.StringIO()
    get('%savailable/flask.tpl' % NGINX_DIR, template)
    interpolated = StringIO.StringIO()
    interpolated.write(_render_template(template.getvalue(), {
        'domain': VHOST,
        'root': APP_ROOT,
        'static': STATIC
    }))
    put(interpolated, '%(nginx)savailable/%(vhost)s' %
        {'nginx': NGINX_DIR, 'vhost': VHOST}, use_sudo=True)
    sudo('ln -s %(src)s %(tar)s' %
         {'src': '%(nginx)savailable/%(vhost)s' %
          {'nginx': NGINX_DIR, 'vhost': VHOST},
          'tar': '%(nginx)senabled/%(vhost)s' %
          {'nginx': NGINX_DIR, 'vhost': VHOST}})
    run('touch %s/access.log' % APP_ROOT)
    run('touch %s/error.log' % APP_ROOT)


def _clone_repo():
    with cd(APPS_DIR):
        run('git clone %(repo)s %(to)s' %
            {'repo': REPO, 'to': APP_ROOT})


def _update_repo():
    with cd(APP_ROOT):
        run('git pull')


def _reload_webserver():
    sudo("/etc/init.d/nginx reload")


def _reload_supervisor():
    sudo('supervisorctl update')


def _start_app():
    sudo('supervisorctl start %s' % VHOST)


def _reload_app(touch=True):
    if touch:
        with cd(APP_ROOT):
            run('touch app.wsgi')
    else:
        sudo('supervisorctl restart %s' % VHOST)


def init_deploy():
    _clone_repo()
    _make_vhost()
    _make_supervisor_conf()
    _reload_webserver()
    _reload_supervisor()
    _start_app()


def deploy():
    _update_repo()
    _reload_app()
