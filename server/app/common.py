from flask import request, jsonify, g
from app import app, redis_client as redis_instance, secret_key
from app.database import MySQLClient  # 导入 MySQLClient 类
from app.database import RedisClient  # 导入 RedisClient 类
from app.models.User import UserModel
from app.models.Admin import AdminModel
import jwt
from functools import wraps

SECRET_KEY = secret_key

redis_client = RedisClient(redis_instance)
# 在应用程序上下文中初始化 MySQLClient 和 RedisClient
# with app.app_context():
#     redis_client = RedisClient(redis_instance)
#     user_model = UserModel(None, redis_client)
#     admin_model = AdminModel(None, redis_client)
#     work_model = WorkModel(None, redis_client, app)
#     template_model = TemplateModel(None, redis_client, app)


def get_mysql_client():
    """
    每个请求独立创建 MySQLClient，并存入 g 对象，避免共享同一连接
    """
    if 'mysql_client' not in g:
        g.mysql_client = MySQLClient(app)
    return g.mysql_client

# 在请求结束时关闭连接
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('mysql_client', None)
    if db is not None and db.connection:
        db.connection.close()


# 封装 response
def response(status_code, message, data=None):
    if data is None:
        data = []
    return jsonify({'code': status_code, 'message': message, 'data': data})


# 验证管理员token
def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        mysql_client = get_mysql_client()
        admin_model = AdminModel(mysql_client, redis_client)
        token = request.headers.get('x-access-token')
        if not token:
            return response(401, 'token不能为空！')
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            admin_id = data.get('admin_id')
            if not admin_id:
                return response(402, 'token无效！')

            # 从数据库获取用户的电子邮件
            mysql_query = "SELECT email FROM admins WHERE admin_id = %s"
            params = (admin_id,)
            result = mysql_client.execute_query_one(mysql_query, params)
            if not result:
                return response(404, '管理员未找到！')
            email = result['email']

            current_admin = admin_model.get_admin_by_email(email)
            if not current_admin:
                return response(404, '管理员未找到！')

        except Exception as e:
            app.logger.error(f"token验证失败: {e}")
            return response(402, 'token无效！')
        return f(current_admin, *args, **kwargs)
    return decorated

# 验证token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        mysql_client = get_mysql_client()
        user_model = UserModel(mysql_client, redis_client)
        token = request.headers.get('x-access-token')
        if not token:
            return response(401, 'token不能为空！')
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = data.get('user_id')
            if not user_id:
                return response(401, 'token无效！')

            # 从数据库获取用户的电子邮件
            mysql_client = get_mysql_client()
            mysql_query = "SELECT email FROM users WHERE user_id = %s"
            params = (user_id,)
            result = mysql_client.execute_query_one(mysql_query, params)
            if not result:
                return response(404, '用户未找到！')
            email = result['email']

            current_user = user_model.get_user_by_email(email)
            if not current_user:
                return response(404, '用户未找到！')

        except Exception as e:
            app.logger.error(f"token验证失败: {e}")
            return response(401, 'token无效！')
        return f(current_user, *args, **kwargs)
    return decorated