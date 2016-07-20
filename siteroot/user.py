# -*- coding: utf-8 -*-
from jinja2 import Environment, FileSystemLoader
from modules.helpers import get_first
from modules.serialize import json_serialize
from modules.httpcore import HttpRequest, HttpException
from models.messaging import *
from models.user import *
from config import *

j2_env = Environment(loader=FileSystemLoader(TEMPLATES), trim_blocks=True, autoescape=True)


class Login(HttpRequest):
    def get(self, request, response):
        # render page
        return 'text/html', j2_env.get_template('login.html').render({
            'site': {
                'url': request.uri,
                'title': SITE_TITLE,
            },
        })

    def post(self, request, response):
        """ called from ajax """
        # get inputs
        try:
            un = request.form['user'][0]
            pw = request.form['pswd'][0]
        except KeyError, e:
            raise HttpException(400, "Missing value for %s" % e.message)
        # get user
        user = get_user(self.conn, un)
        if not user:
            raise HttpException(401, "Username or Password incorrect")
        # check pswd
        if not check_pswd(pw, user['pswd']):
            raise HttpException(401, "Username or Password incorrect")
        # generate access token
        token = create_login_token(self.conn, user['id'])
        # return result
        return token


class Message(HttpRequest):
    def post(self, request, response):
        """ called from ajax """
        # check access
        user = check_login(self.conn, get_first(request.cookies.get('accesstoken')))
        if not user:
            raise HttpException(401, "Not logged in")
        # get inputs
        try:
            message = request.form['message'][0].strip()
            recipient = request.form['recipient'][0]
        except KeyError, e:
            raise HttpException(400, "Missing value for %s" % e.message)
        # check not sending to oneself
        if user['id'] == int(recipient):
            raise HttpException(400, "You can't send to yourself")
        # save a copy of the message
        save_message(self.conn, user['id'], recipient, message)
        # return result
        return "Message sent"


class Inbox(HttpRequest):
    def get(self, request, response):
        # check access
        user = check_login(self.conn, get_first(request.cookies.get('accesstoken')))
        if not user:
            response.headers['Location'] = request.uri + '/user/login?r=/user/inbox'
            raise HttpException(302)
        # render page
        return 'text/html', j2_env.get_template('inbox.html').render({
            'site': {
                'url': request.uri,
                'title': SITE_TITLE,
            },
            'user': user,
        })

    def post(self, request, response):
        """ called from ajax """
        # check access
        user = check_login(self.conn, get_first(request.cookies.get('accesstoken')))
        if not user:
            raise HttpException(401, "Not logged in")
        # get request
        query = request.urlparams[0].lower()  # sellers or messages
        # get senders
        if query == 'sellers':
            data = get_sellers(self.conn, user['id'])
        # get messages
        else:
            try:
                senderid = request.form['senderid'][0]
            except KeyError, e:
                raise HttpException(400, "Missing value for %s" % e.message)
            data = get_messages(self.conn, user['id'], senderid)
        # return result
        return 'application/json', json_serialize(data)


class Logout(HttpRequest):
    def get(self, request, response):
        # delete token from db
        token = get_first(request.cookies.get('accesstoken'))
        delete_login_token(self.conn, token)
        # return result
        response.headers['Set-Cookie'] = 'accesstoken=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/'
        response.headers['Location'] = request.uri + '/'
        raise HttpException(302)
