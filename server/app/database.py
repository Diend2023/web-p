# /server/app/database.py
from flask import current_app as app
import MySQLdb
import datetime
import json

class MySQLClient:
    def __init__(self, app):
        self.app = app
        self.connection = self.connect()

    def connect(self):
        """
        初始化 MySQL 连接。
        """
        try:
            connection = MySQLdb.connect(
                host=self.app.config['MYSQL_HOST'],
                user=self.app.config['MYSQL_USER'],
                password=self.app.config['MYSQL_PASSWORD'],
                db=self.app.config['MYSQL_DB'],
                cursorclass=MySQLdb.cursors.DictCursor
            )
            return connection
        except MySQLdb.Error as e:
            app.logger.error(f"MySQL 连接失败: {e}")
            return None

    def _convert_params(self, params):
        """
        将参数中的 datetime 对象转换为字符串格式。
        """
        if params is None:
            return None
        return tuple(
            param.strftime('%Y-%m-%d %H:%M:%S') if isinstance(param, datetime.datetime) else param
            for param in params
        )

    def check_connection(self):
        """
        检查数据库连接是否正常。
        """
        try:
            cur = self.connection.cursor()
            cur.execute("SELECT 1")
            cur.close()
            app.logger.info("MySQL 连接正常")
        except MySQLdb.Error as e:
            app.logger.error(f"MySQL 连接出错: {e}")

    def execute_query(self, query, params=None):
        """
        执行 MySQL 查询并返回所有结果。
        """
        params = self._convert_params(params)
        try:
            cur = self.connection.cursor()
            cur.execute(query, params)
            result = cur.fetchall()
            cur.close()
            return result
        except MySQLdb.Error as e:
            app.logger.error(f"MySQL 查询出错: {e} - Query: {query} - Params: {params}")
            return None

    def execute_query_one(self, query, params=None):
        """
        执行 MySQL 查询并返回单行结果。
        """
        params = self._convert_params(params)
        try:
            self.connection.ping(True)
            with self.connection.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchone()
            return result
        except MySQLdb.Error as e:
            app.logger.error(f"MySQL 查询出错: {e} - Query: {query} - Params: {params}")
            return None

    def execute_update(self, query, params=None):
        """
        执行 MySQL 更新操作。
        """
        params = self._convert_params(params)
        try:
            cur = self.connection.cursor()
            cur.execute(query, params)
            self.connection.commit()
            cur.close()
        except MySQLdb.Error as e:
            app.logger.error(f"MySQL 更新出错: {e} - Query: {query} - Params: {params}")

    def execute_insert(self, query, params=None):
        """
        执行 MySQL 插入操作，并返回最后插入的ID。
        """
        params = self._convert_params(params)
        try:
            cur = self.connection.cursor()
            cur.execute(query, params)
            self.connection.commit()
            last_id = cur.lastrowid
            cur.close()
            return last_id
        except MySQLdb.Error as e:
            app.logger.error(f"MySQL 插入出错: {e} - Query: {query} - Params: {params}")
            return None

    def execute_delete(self, query, params=None):
        """
        执行 MySQL 删除操作。
        """
        params = self._convert_params(params)
        try:
            cur = self.connection.cursor()
            cur.execute(query, params)
            self.connection.commit()
            cur.close()
        except MySQLdb.Error as e:
            app.logger.error(f"MySQL 删除出错: {e} - Query: {query} - Params: {params}")



class RedisClient:
    def __init__(self, client):
        self.client = client

    def get(self, key):
        """
        从 Redis 获取数据并反序列化。
        """
        try:
            redis_data = self.client.get(key)
            if redis_data:
                return json.loads(redis_data)
            return None
        except Exception as e:
            app.logger.error(f"从 Redis 获取数据出错: {e}")
            return None

    def set(self, key, data, time=3600):
        """
        将数据序列化后存入 Redis，并设置过期时间。
        """
        try:
            self.client.setex(key, time, json.dumps(data))
        except Exception as e:
            app.logger.error(f"将数据存入 Redis 出错: {e}")

    def delete(self, key):
        """
        从 Redis 删除数据。
        """
        try:
            self.client.delete(key)
        except Exception as e:
            app.logger.error(f"从 Redis 删除数据出错: {e}")