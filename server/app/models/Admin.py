from app.database import MySQLClient
from app.database import RedisClient
from app.models.Work import Work
from app.models.Template import Template
from app.models.User import User
import bcrypt
import uuid
import json
import datetime


class Admin:
    def __init__(self, a_id, admin_id, adminname, email, password, create_time, update_time, last_login_time):
        self.a_id = a_id
        self.admin_id = admin_id
        self.adminname = adminname
        self.email = email
        self.password = password
        self.create_time = create_time
        self.update_time = update_time
        self.last_login_time = last_login_time

    @staticmethod
    def _convert_datetime(data):
        """
        将数据中的 datetime 对象转换为字符串格式。
        """
        for key, value in data.items():
            if isinstance(value, datetime.datetime):
                data[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        return data

    @staticmethod
    def from_dict(data):
        """
        从字典创建 Admin 对象。
        """
        data = Admin._convert_datetime(data)
        return Admin(
            a_id=data.get('a_id'),
            admin_id=data.get('admin_id'),
            adminname=data.get('adminname'),
            email=data.get('email'),
            password=data.get('password'),
            create_time=data.get('create_time'),
            update_time=data.get('update_time'),
            last_login_time=data.get('last_login_time')
        )

    @staticmethod
    def to_dict(admin):
        """
        将 Admin 对象转换为字典。
        """
        return Admin._convert_datetime({
            'a_id': admin.a_id,
            'admin_id': admin.admin_id,
            'adminname': admin.adminname,
            'email': admin.email,
            'password': admin.password,
            'create_time': admin.create_time,
            'update_time': admin.update_time,
            'last_login_time': admin.last_login_time
        })


class AdminModel:
    def __init__(self, mysql_client: MySQLClient, redis_client: RedisClient):
        self.mysql_client = mysql_client
        self.redis_client = redis_client

    def get_admin_by_email(self, email):
        redis_key = f"admin_email:{email}"
        admin_data = self.redis_client.get(redis_key)
        if admin_data:
            admin_data = json.loads(admin_data)
            return Admin.from_dict(admin_data)
        mysql_query = "SELECT * FROM admins WHERE email = %s"
        params = (email,)
        admin_data = self.mysql_client.execute_query_one(mysql_query, params)
        if admin_data:
            admin = Admin.from_dict(admin_data)
            self.redis_client.set(
                redis_key, json.dumps(Admin.to_dict(admin)), 300)
            return admin
        return None

    def get_admin_by_a_id(self, a_id):
        mysql_query = "SELECT * FROM admins WHERE a_id = %s"
        params = (a_id,)
        admin_data = self.mysql_client.execute_query_one(mysql_query, params)
        if admin_data:
            return Admin.from_dict(admin_data)
        return None

    def get_admin_by_admin_id(self, admin_id):
        mysql_query = "SELECT * FROM admins WHERE admin_id = %s"
        params = (admin_id,)
        admin_data = self.mysql_client.execute_query_one(mysql_query, params)
        if admin_data:
            return Admin.from_dict(admin_data)
        return None

    def get_admins(self):
        mysql_query = "SELECT * FROM admins"
        admins_data = self.mysql_client.execute_query(mysql_query)
        if admins_data:
            return [Admin.from_dict(admin) for admin in admins_data]
        return []

    def update_last_login_time(self, email):
        last_login_time = datetime.datetime.now()
        mysql_query = "UPDATE admins SET last_login_time = %s WHERE email = %s"
        params = (last_login_time, email)
        self.mysql_client.execute_update(mysql_query, params)
        admin = self.get_admin_by_email(email)
        if admin:
            admin.last_login_time = last_login_time
            self.redis_client.set(
                f"admin_email:{email}", json.dumps(Admin.to_dict(admin)), 300)
        return admin

    def get_users_paginated(self, page, size, u_id=None, user_id=None, username=None, email=None):
        where = []
        params = []
        if u_id:
            where.append("u_id = %s")
            params.append(u_id)
        if user_id:
            where.append("user_id = %s")
            params.append(user_id)
        if username:
            where.append("username LIKE %s")
            params.append(f"%{username}%")
        if email:
            where.append("email LIKE %s")
            params.append(f"%{email}%")
        where_clause = " AND ".join(where) or "1=1"
        # 查询总数
        cnt_sql = f"SELECT COUNT(*) AS cnt FROM users WHERE {where_clause}"
        total = self.mysql_client.execute_query_one(
            cnt_sql, tuple(params))['cnt']
        # 查询当前页
        offset = (page - 1) * size
        list_sql = f"SELECT * FROM users WHERE {where_clause} ORDER BY create_time DESC LIMIT % s OFFSET % s"
        rows = self.mysql_client.execute_query(
            list_sql, tuple(params + [size, offset]))
        users = [User.from_dict(r) for r in rows]
        return users, total

    def get_works_paginated(self, page, size, w_id=None, u_id=None, w_name=None, w_description=None, t_id=None):
        where = []
        params = []
        if w_id:
            where.append("w_id = %s")
            params.append(w_id)
        if u_id:
            where.append("u_id = %s")
            params.append(u_id)
        if w_name:
            where.append("w_name LIKE %s")
            params.append(f"%{w_name}%")
        if w_description:
            where.append("w_description LIKE %s")
            params.append(f"%{w_description}%")
        if t_id:
            where.append("t_id = %s")
            params.append(t_id)

        where_clause = " AND ".join(where) or "1=1"
        # 总数
        cnt_sql = f"SELECT COUNT(*) AS cnt FROM works WHERE {where_clause}"
        total = self.mysql_client.execute_query_one(
            cnt_sql, tuple(params))['cnt']
        # 分页数据
        offset = (page - 1) * size
        list_sql = f"SELECT * FROM works WHERE {where_clause} ORDER BY create_time DESC LIMIT %s OFFSET %s"
        rows = self.mysql_client.execute_query(
            list_sql, tuple(params + [size, offset]))
        works = [Work.from_dict(r) for r in rows]
        return works, total

    def get_templates_paginated(self, page, size, t_id=None, t_author=None, t_name=None, t_description=None):
        where = []
        params = []
        if t_id:
            where.append("t_id = %s")
            params.append(t_id)
        if t_author:
            where.append("t_author LIKE %s")
            params.append(f"%{t_author}%")
        if t_name:
            where.append("t_name LIKE %s")
            params.append(f"%{t_name}%")
        if t_description:
            where.append("t_description LIKE %s")
            params.append(f"%{t_description}%")
        where_clause = " AND ".join(where) or "1=1"
        # 总数
        cnt_sql = f"SELECT COUNT(*) AS cnt FROM templates WHERE {where_clause}"
        total = self.mysql_client.execute_query_one(
            cnt_sql, tuple(params))['cnt']
        # 分页数据
        offset = (page - 1) * size
        list_sql = f"SELECT * FROM templates WHERE {where_clause} ORDER BY t_id DESC LIMIT %s OFFSET %s"
        rows = self.mysql_client.execute_query(list_sql,
                                               tuple(params + [size, offset]))
        templates = [Template.from_dict(r) for r in rows]
        return templates, total

    def get_admins_paginated(self, page, size, a_id=None, admin_id=None, adminname=None, email=None):
        where = []
        params = []
        if a_id:
            where.append("a_id = %s")
            params.append(a_id)
        if admin_id:
            where.append("admin_id = %s")
            params.append(admin_id)
        if adminname:
            where.append("adminname LIKE %s")
            params.append(f"%{adminname}%")
        if email:
            where.append("email LIKE %s")
            params.append(f"%{email}%")
        where_clause = " AND ".join(where) or "1=1"
        # 总数
        cnt_sql = f"SELECT COUNT(*) AS cnt FROM admins WHERE {where_clause}"
        total = self.mysql_client.execute_query_one(
            cnt_sql, tuple(params))['cnt']
        # 分页数据
        offset = (page - 1) * size
        list_sql = f"SELECT * FROM admins WHERE {where_clause} ORDER BY create_time DESC LIMIT %s OFFSET %s"
        rows = self.mysql_client.execute_query(
            list_sql, tuple(params + [size, offset]))
        admins = [Admin.from_dict(r) for r in rows]
        return admins, total

    def create_admin(self, adminname, email, password):
        hashed_password = bcrypt.hashpw(password.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin_id = str(uuid.uuid4())
        create_time = datetime.datetime.now()
        update_time = create_time
        last_login_time = None
        mysql_query = "INSERT INTO admins (admin_id, adminname, email, password, create_time, update_time, last_login_time) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        params = (admin_id, adminname, email, hashed_password,
                  create_time, update_time, last_login_time)
        self.mysql_client.execute_insert(mysql_query, params)

        # 获取自增的 a_id
        mysql_query = "SELECT a_id FROM admins WHERE admin_id = %s"
        params = (admin_id,)
        admin_data = self.mysql_client.execute_query_one(mysql_query, params)
        a_id = admin_data['a_id']

        admin = Admin(a_id, admin_id, adminname, email,
                      hashed_password, create_time, update_time, last_login_time)
        self.redis_client.set(
            f"admin_email:{email}", json.dumps(Admin.to_dict(admin)), 300)
        return admin

    def update_admin_info(self, a_id, new_adminname, new_email):
        update_time = datetime.datetime.now()
        mysql_query = "UPDATE admins SET adminname = %s, email = %s, update_time = %s WHERE a_id = %s"
        params = (new_adminname, new_email, update_time, a_id)
        self.mysql_client.execute_update(mysql_query, params)
        admin = self.get_admin_by_a_id(a_id)
        if admin:
            old_email = admin.email
            admin.adminname = new_adminname
            admin.email = new_email
            admin.update_time = update_time
            self.redis_client.set(
                f"admin_email:{new_email}", json.dumps(Admin.to_dict(admin)), 300)
            self.redis_client.delete(f"admin_email:{old_email}")
        return admin

    def update_password(self, email, new_password):
        hashed_new_password = bcrypt.hashpw(new_password.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')
        update_time = datetime.datetime.now()
        mysql_query = "UPDATE admins SET password = %s, update_time = %s WHERE email = %s"
        params = (hashed_new_password, update_time, email)
        self.mysql_client.execute_update(mysql_query, params)
        admin = self.get_admin_by_email(email)
        if admin:
            admin.password = hashed_new_password
            admin.update_time = update_time
            self.redis_client.set(
                f"admin_email:{email}", json.dumps(Admin.to_dict(admin)), 300)
        return admin

    def update_last_login_time(self, email):
        last_login_time = datetime.datetime.now()
        mysql_query = "UPDATE admins SET last_login_time = %s WHERE email = %s"
        params = (last_login_time, email)
        self.mysql_client.execute_update(mysql_query, params)
        admin = self.get_admin_by_email(email)
        if admin:
            admin.last_login_time = last_login_time
            self.redis_client.set(
                f"admin_email:{email}", json.dumps(Admin.to_dict(admin)), 300)
        return admin

    def delete_admin(self, email):
        admin = self.get_admin_by_email(email)
        if admin:
            mysql_query = "DELETE FROM admins WHERE email = %s"
            params = (email,)
            self.mysql_client.execute_delete(mysql_query, params)
            self.redis_client.delete(f"admin_email:{email}")
        return True
