# -*- coding: utf-8 -*-
import bcrypt
from modules.helpers import generate_uid


def get_user(conn, un):
    sql = "select * from users where user = %s and enabled = 1 limit 1"
    return conn.execute(sql, [un]).fetchone()


def check_pswd(pswd, hash):
    return bcrypt.hashpw(str(pswd), str(hash)) == str(hash)


def create_login_token(conn, userid, size=64):
    token = generate_uid(size)
    sql = "insert into logins (token, user_id) values (%s, %s)"
    conn.execute(sql, [token, userid]).commit()
    return token


def delete_login_token(conn, token):
    sql = "delete from logins where token = %s limit 1"
    conn.execute(sql, [token]).commit()


def check_login(conn, token):
    if not token: return None
    sql = "select u.* from logins l join users u on u.id = l.user_id where l.token = %s and u.enabled = 1 limit 1"
    return conn.execute(sql, [token]).fetchone()


def send_message(conn, buyer_id, seller_id, message):
    sql = "insert into messages (buyer_id, seller_id, message) values (%s, %s, %s)"
    conn.execute(sql, [buyer_id, seller_id, message]).commit()
