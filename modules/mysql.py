# -*- coding: utf-8 -*-
import logging
import _mysql
from datetime import datetime
from Queue import Queue
from _mysql_exceptions import *
from MySQLdb.converters import conversions


class NoConnection(Exception):
    """captures 2006 errors"""
    pass


class MySql(object):
    _conn = None
    _data = None
    _insertid = None
    isalive = False

    def __init__(self, host, user, pswd, name, timeout=5, ident=0):
        self.ident = ident
        self.host = host
        self.user = user
        self.pswd = pswd
        self.name = name
        self.timeout = timeout
        self.connect()

    def _reset(self):
        self._data = None
        self._insertid = None
        self.isalive = False

    def connect(self):
        try:
            logging.info("Connecting to db [%s] %s@%s" % (self.ident, self.user, self.host))
            self._conn = _mysql.connect(host=self.host, user=self.user, passwd=self.pswd, db=self.name, connect_timeout=self.timeout, conv=conversions)
            self._conn.set_character_set('utf8')
            self._conn.autocommit(False)
            self.isalive = True
        except MySQLError, e:
            # specifically written to remove identity data from the message
            if e.args[0] == 2005:
                raise Exception("MySQL Error [2005]: Unknown host")
            elif e.args[0] == 1045:
                raise Exception("MySQL Error [1045]: Invalid username or password")
            elif e.args[0] == 1044:
                raise Exception("MySQL Error [1044]: Access denied to database")
            else:
                raise Exception("MySQL Error [{}]: {}".format(e.args[0], e.args[1]))

    def close(self):
        try:
            self._conn.close()
            self.isalive = False
        except:
            logging.warning("Connection [%s] already closed" % self.ident)

    def commit(self):
        self._conn.commit()
        return self

    def last_insert_id(self):
        return self._insertid

    def format_statement(self, sql, vals):
        if not vals: return sql
        for v in vals:
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            elif isinstance(v, datetime):
                v = v.strftime('%Y-%m-%d %H:%M:%S')
            if sql.find('%s') == -1:
                raise Exception('Not enough placeholders in statement')
            sql = sql.replace('%s', self._conn.escape(v), 1)
        if sql.find('%s') > -1:
            raise Exception('Not all placeholders filled in statement')
        return sql

    def execute(self, sql, vals=None):
        self._reset()
        sql = self.format_statement(sql, vals)
        for _ in xrange(2):  # try x times
            try:
                self._conn.query(sql)
                self._data = self._conn.store_result()
                self._insertid = self._conn.insert_id()
                self.isalive = True
                return self
            except MySQLError, e:
                # SERVER_GONE_ERROR|SERVER_LOST
                if e.args[0] in (2006, 2013):
                    logging.warning("MySQL Error [%s]: %s - [%s]" % (e.args[0], e.args[1], self.ident))
                    self._conn.ping(True)
                elif e.args[0] == 1064:  # protect database secrets
                    raise Exception("MySQL Error [1064]: Error in SQL syntax")
                else:
                    raise Exception("MySQL Error [{}]: {}".format(e.args[0], e.args[1]))
        raise NoConnection("MySQL Error: Could not connect to database")

    def fetchone(self):
        row = self._data.fetch_row(1, 1)
        return row[0] if row else None

    def fetchall(self):
        rows = self._data.fetch_row(0, 1)
        return rows if rows else None


class MySQLConnectionPool(object):
    conn_pool = Queue()
    pool_size = 50
    dbident = 0

    def get_connection(self):
        try:
            return self.conn_pool.get()
        except Exception, e:  # pool is empty or problem connecting
            self.dbident += 1
            return MySql(self.db_host, self.db_user, self.db_pswd, self.db_name, ident=self.dbident)

    def put_connection(self, conn):
        self.conn_pool.put(conn)

    def initialize(self):
        for i in xrange(self.pool_size):
            self.dbident += 1
            conn = MySql(self.db_host, self.db_user, self.db_pswd, self.db_name, ident=self.dbident)
            self.conn_pool.put_nowait(conn)

    def __init__(self, host, user, pswd, name):
        self.db_host = host
        self.db_user = user
        self.db_pswd = pswd
        self.db_name = name
        self.initialize()
