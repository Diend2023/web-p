# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    REDIS_URL = os.environ.get('REDIS_URL', "redis://localhost:6379/0")
    STATIC_FOLDER = os.path.join(os.getcwd(), 'src')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'web_p')
    MYSQL_CURSORCLASS = 'DictCursor'
    TEMPLATE_FOLDER = os.path.join(os.getcwd(), 'src', 'static', 'templates')
    USER_WORK_FOLDER = os.path.join(os.getcwd(), 'src', 'static', 'works')