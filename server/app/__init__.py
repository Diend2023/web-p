# /server/app/__init__.py
from flask import Flask
from redis import Redis
from flask_cors import CORS
from flask_mysqldb import MySQL
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)
app.json.ensure_ascii = False

app.static_folder = os.path.join(app.config['STATIC_FOLDER'])
redis_client = Redis.from_url(app.config['REDIS_URL'])
secret_key = app.config['SECRET_KEY']
mysql = MySQL(app)
CORS(app)

with app.app_context():
    from app.routes import user, admin, work, template
    app.register_blueprint(user.user_bp, url_prefix='/api/user')
    app.register_blueprint(admin.admin_bp, url_prefix='/api/admin')
    app.register_blueprint(work.work_bp, url_prefix='/api/work')
    app.register_blueprint(template.template_bp, url_prefix='/api/template')
