from flask import request, Blueprint
from app import app
from app.common import response, token_required, SECRET_KEY, get_mysql_client, redis_client
from app.models.User import User, UserModel
from app.models.Work import WorkModel
import bcrypt
import jwt


user_bp = Blueprint('user', __name__)


# 用户注册接口
@user_bp.route('/register', methods=['POST'])
def register():
    try:
        mysql_client = get_mysql_client()
        user_model = UserModel(mysql_client, redis_client)
        work_model = WorkModel(mysql_client, redis_client, app)
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return response(400, '注册失败，不能为空！')

        existing_user = user_model.get_user_by_email(email)
        if existing_user:
            print(f"邮箱{email}已存在")
            return response(400, '注册失败，邮箱已注册！')

        user = user_model.create_user(username, email, password)

        if not user:
            return response(500, '注册失败！作品文件夹创建失败！')
        
        user_work_file = work_model.make_user_work_folder(user.user_id)
        if not user_work_file:
            user_model.delete_user(user.email)
            return response(500, '注册失败！作品文件夹创建失败！')

        return response(201, '注册成功！', User.to_dict(user))
    except Exception as e:
        app.logger.error(f"注册失败: {e}")
        return response(500, '注册失败！')

# 用户登录接口
@user_bp.route('/login', methods=['POST'])
def login():
    try:
        mysql_client = get_mysql_client()
        user_model = UserModel(mysql_client, redis_client)
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return response(400, '登录失败，不能为空！')

        user = user_model.get_user_by_email(email)
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return response(401, '登录失败，邮箱或密码错误！')

        user_model.update_last_login_time(user.email)

        token = jwt.encode({'user_id': user.user_id}, SECRET_KEY, algorithm="HS256")

        return response(200, '登录成功！', {'token': token})
    except Exception as e:
        app.logger.error(f"登录失败: {e}")
        return response(500, '登录失败！')

# 用户验证接口
@user_bp.route('/verify', methods=['POST'])
@token_required
def verify(current_user):
    return response(200, '用户验证成功！', User.to_dict(current_user))

# 用户登出接口
@user_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    return response(200, '登出成功！')

# 获取用户信息接口
@user_bp.route('/get', methods=['GET'])
@token_required
def get_user_info(current_user):
    try:
        mysql_client = get_mysql_client()
        user_model = UserModel(mysql_client, redis_client)
        email = current_user.email
        if not email:
            return response(400, '用户信息获取失败！')

        user_info = user_model.get_user_by_email(email)
        if not user_info:
            return response(404, '用户未找到！')

        user_info_dict = User.to_dict(user_info)
        user_info_dict.pop('password', None)
        user_info_dict.pop('u_id', None)

        return response(200, '获取成功！', user_info_dict)
    except Exception as e:
        app.logger.error(f"获取用户信息失败: {e}")
        return response(500, '获取用户信息失败！')

# 修改用户信息接口
@user_bp.route('/set', methods=['POST'])
@token_required
def update_user_info(current_user):
    try:
        mysql_client = get_mysql_client()
        user_model = UserModel(mysql_client, redis_client)
        data = request.get_json()
        new_username = data.get('username')
        new_email = data.get('email')
        password = data.get('password')

        if not new_username or not new_email or not password:
            return response(400, '修改失败，不能为空！')

        user_id = current_user.user_id

        user = user_model.get_user_by_email(current_user.email)
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return response(401, '密码错误！')

        if new_email != user.email:
            existing_user = user_model.get_user_by_email(new_email)
            if existing_user:
                return response(400, '修改失败，邮箱已注册！')

        user_data = user_model.update_user_info(user_id, new_username, new_email)
        user_data_dict = User.to_dict(user_data)
        user_data_dict.pop('password', None)
        user_data_dict.pop('u_id', None)
        return response(200, '用户信息修改成功！', user_data_dict)
    except Exception as e:
        app.logger.error(f"修改用户信息失败: {e}")
        return response(500, '修改用户信息失败！')

# 修改密码接口
@user_bp.route('/password', methods=['POST'])
@token_required
def update_password(current_user):
    try:
        mysql_client = get_mysql_client()
        user_model = UserModel(mysql_client, redis_client)
        data = request.get_json()
        old_password = data.get('oldPassword')
        new_password = data.get('newPassword')

        if not old_password or not new_password:
            return response(400, '修改失败，不能为空！')

        user = user_model.get_user_by_email(current_user.email)
        if not user or not bcrypt.checkpw(old_password.encode('utf-8'), user.password.encode('utf-8')):
            return response(401, '旧密码错误！')

        user_model.update_password(user.email, new_password)
        return response(200, '密码修改成功！')
    except Exception as e:
        app.logger.error(f"修改密码失败: {e}")
        return response(500, '修改密码失败！')

# 注销账户接口
@user_bp.route('/del', methods=['POST'])
@token_required
def delete_account(current_user):
    try:
        mysql_client = get_mysql_client()
        user_model = UserModel(mysql_client, redis_client)
        work_model = WorkModel(mysql_client, redis_client, app)
        data = request.get_json()
        password = data.get('password')

        if not password:
            return response(400, '密码不能为空！')

        user = user_model.get_user_by_email(current_user.email)
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return response(401, '密码错误！')

        user_work_file = work_model.remove_user_work_folder(user.user_id, user.u_id)
        if not user_work_file:
            return response(500, '注销账户失败！作品文件夹异常！')

        user_model.delete_user(user.email)
        return response(200, '账户注销成功！')
    except Exception as e:
        app.logger.error(f"注销账户失败: {e}")
        return response(500, '注销账户失败！')