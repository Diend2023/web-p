from app.database import MySQLClient
from app.database import RedisClient
import bcrypt
import uuid
import json
import datetime


class User:
    def __init__(self, u_id, user_id, username, email, password, create_time, update_time, last_login_time):
        self.u_id = u_id
        self.user_id = user_id
        self.username = username
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
        从字典创建 User 对象。
        """
        data = User._convert_datetime(data)
        return User(
            u_id=data.get('u_id'),
            user_id=data.get('user_id'),
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            create_time=data.get('create_time'),
            update_time=data.get('update_time'),
            last_login_time=data.get('last_login_time')
        )

    @staticmethod
    def to_dict(user):
        """
        将 User 对象转换为字典。
        """
        return User._convert_datetime({
            'u_id': user.u_id,
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'password': user.password,
            'create_time': user.create_time,
            'update_time': user.update_time,
            'last_login_time': user.last_login_time
        })

class UserModel:
    def __init__(self, mysql_client: MySQLClient, redis_client: RedisClient):
        self.mysql_client = mysql_client
        self.redis_client = redis_client

    def get_user_by_email(self, email):
        redis_key = f"user_email:{email}"
        user_data = self.redis_client.get(redis_key)
        if user_data:
            user_data = json.loads(user_data)
            return User.from_dict(user_data)
        mysql_query = "SELECT * FROM users WHERE email = %s"
        params = (email,)
        user_data = self.mysql_client.execute_query_one(mysql_query, params)
        if user_data:
            user = User.from_dict(user_data)
            self.redis_client.set(redis_key, json.dumps(User.to_dict(user)))
            return user
        return None
    
    def get_user_by_user_id(self, user_id):
        mysql_query = "SELECT * FROM users WHERE user_id = %s"
        params = (user_id,)
        user_data = self.mysql_client.execute_query_one(mysql_query, params)
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def get_user_by_u_id(self, u_id):
        mysql_query = "SELECT * FROM users WHERE u_id = %s"
        params = (u_id,)
        user_data = self.mysql_client.execute_query_one(mysql_query, params)
        if user_data:
            return User.from_dict(user_data)
        return None

    def create_user(self, username, email, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = str(uuid.uuid4())
        create_time = datetime.datetime.now()
        update_time = create_time
        last_login_time = None
        mysql_query = "INSERT INTO users (user_id, username, email, password, create_time, update_time, last_login_time) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        params = (user_id, username, email, hashed_password, create_time, update_time, last_login_time)
        self.mysql_client.execute_insert(mysql_query, params)
        
        # 获取自增的 u_id
        mysql_query = "SELECT u_id FROM users WHERE user_id = %s"
        params = (user_id,)
        user_data = self.mysql_client.execute_query_one(mysql_query, params)
        u_id = user_data['u_id']

        user = User(u_id, user_id, username, email, hashed_password, create_time, update_time, last_login_time)
        self.redis_client.set(f"user_email:{email}", json.dumps(User.to_dict(user)))
        return user


    def update_user_info(self, user_id, new_username, new_email):
        update_time = datetime.datetime.now()
        mysql_query = "UPDATE users SET username = %s, email = %s, update_time = %s WHERE user_id = %s"
        params = (new_username, new_email, update_time, user_id)
        self.mysql_client.execute_update(mysql_query, params)
        user = self.get_user_by_email(new_email)
        if user:
            old_email = user.email
            user.username = new_username
            user.email = new_email
            user.update_time = update_time
            self.redis_client.set(f"user_email:{new_email}", json.dumps(User.to_dict(user)))
            self.redis_client.delete(f"user_email:{old_email}")
        return user

    def update_password(self, email, new_password):
        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        update_time = datetime.datetime.now()
        mysql_query = "UPDATE users SET password = %s, update_time = %s WHERE email = %s"
        params = (hashed_new_password, update_time, email)
        self.mysql_client.execute_update(mysql_query, params)
        user = self.get_user_by_email(email)
        if user:
            user.password = hashed_new_password
            user.update_time = update_time
            self.redis_client.set(f"user_email:{email}", json.dumps(User.to_dict(user)))
        return user

    def update_last_login_time(self, email):
        last_login_time = datetime.datetime.now()
        mysql_query = "UPDATE users SET last_login_time = %s WHERE email = %s"
        params = (last_login_time, email)
        self.mysql_client.execute_update(mysql_query, params)
        user = self.get_user_by_email(email)
        if user:
            user.last_login_time = last_login_time
            self.redis_client.set(f"user_email:{email}", json.dumps(User.to_dict(user)))
        return user

    def delete_user(self, email):
        user = self.get_user_by_email(email)
        if user:
            mysql_query = "DELETE FROM users WHERE email = %s"
            params = (email,)
            self.mysql_client.execute_delete(mysql_query, params)
            self.redis_client.delete(f"user_email:{email}")