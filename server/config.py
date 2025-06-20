# /server/config.py
import os


class Config:
    SECRET_KEY = 'b46112cf43124cb35c45d487ec4ce1ce'
    REDIS_URL = "redis://localhost:6379/0"
    STATIC_FOLDER = os.path.join(os.getcwd(), 'src')
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'root'
    MYSQL_DB = 'web_p'
    MYSQL_CURSORCLASS = 'DictCursor'
    TEMPLATE_FOLDER = os.path.join(os.getcwd(), 'src', 'static', 'templates')
    USER_WORK_FOLDER = os.path.join(os.getcwd(), 'src', 'static', 'works')
