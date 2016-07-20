# -*- coding: utf-8 -*-


def save_message(conn, sender, recipient, message):
    sql = "insert into messages (sender, recipient, message) values (%s, %s, %s)"
    conn.execute(sql, [sender, recipient, message]).commit()


def get_sellers(conn, userid):
    sql = "select u.id, u.name, MAX(m.created) 'updated' from messages m " \
          "join users u on u.id = if(recipient = %(userid)s, sender, recipient) " \
          "where %(userid)s in (sender, recipient) " \
          "group by u.id " \
          "order by updated desc"
    return conn.execute(sql, {'userid': userid}).fetchall()


def get_messages(conn, userid, senderid):
    sql = "select u.name, m.sender, m.message, m.created from messages m " \
          "join users u on u.id = m.sender " \
          "where (sender = %(userid)s and recipient = %(senderid)s) " \
          "or (recipient = %(userid)s and sender = %(senderid)s) " \
          "order by created desc"
    return conn.execute(sql, {'userid': userid, 'senderid': senderid}).fetchall()
