# -*- coding: utf-8 -*-
from jinja2 import Environment, FileSystemLoader
from modules.helpers import get_first
from modules.serialize import json_serialize
from modules.httpcore import HttpRequest, HttpException
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
            message = request.form['message'][0]
            seller_id = request.form['sellerid'][0]
        except KeyError, e:
            raise HttpException(400, "Missing value for %s" % e.message)
        # check not sending to oneself
        if user['id'] == int(seller_id):
            raise HttpException(400, "You can't send to yourself")
        # save a copy of the message for each user
        sql = "insert into messages (owner, editor, message) values (%s, %s, %s)"
        #self.conn.execute(sql, [user['id'], user['id'], message]).commit()
        self.conn.execute(sql, [seller_id, user['id'], message]).commit()
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
        # check access
        user = check_login(self.conn, get_first(request.cookies.get('accesstoken')))
        if not user:
            raise HttpException(401, "Not logged in")
        # get request
        query = request.urlparams[0].lower()
        # get sellers
        if query == 'sellers':
            sql = "select distinct u.id,u.name,max(m.created) 'updated' " \
                "from messages m " \
                "join users u on u.id=m.editor " \
                "where owner = %s " \
                "group by m.editor " \
                "order by updated desc " \
                "limit 20"
            data = self.conn.execute(sql, [user['id']]).fetchall()
        else:
            try:
                editor = request.form['id'][0]
            except KeyError, e:
                raise HttpException(400, "Missing value for %s" % e.message)
            sql = "select u.name,m.* from messages m join users u on u.id = m.owner where m.owner = %s and m.editor = %s " \
                "union all " \
                "select u.name,m.* from messages m join users u on u.id = m.owner where m.editor = %s and m.owner = %s " \
                "order by created desc"
            data = self.conn.execute(sql, [user['id'], editor, user['id'], editor]).fetchall()
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
