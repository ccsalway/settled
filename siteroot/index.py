# -*- coding: utf-8 -*-
from jinja2 import Environment, FileSystemLoader
from modules.httpcore import HttpRequest
from modules.helpers import get_first
from models.user import check_login
from config import *

j2_env = Environment(loader=FileSystemLoader(TEMPLATES), trim_blocks=True, autoescape=True)


class Index(HttpRequest):
    def get(self, request, response):
        # get user - login not required
        token = get_first(request.cookies.get('accesstoken'), default='')
        user = check_login(self.conn, token)
        # render page
        return 'text/html', j2_env.get_template('index.html').render({
            'site': {
                'url': request.uri,
                'title': SITE_TITLE,
            },
            'user': user,
            'accesstoken': token,
        })
